from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
from models.user import User
from models.medical_report import MedicalReport
from models.recovery_plan import RecoveryPlan
from services import schedule_adjuster
from services.report_analyzer import ReportAnalyzer
from services.calendar_generator import CalendarGenerator
from services.notification_manager import NotificationManager
from utils.firebase_client import FirebaseClient
from config import Config
import uuid
import email_validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = 'uploads'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

firebase_client = FirebaseClient()
report_analyzer = ReportAnalyzer()
calendar_generator = CalendarGenerator()
notification_manager = NotificationManager()

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

@login_manager.user_loader
def load_user(user_id):
    return firebase_client.get_user(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('upload.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = firebase_client.get_user_by_email(form.email.data)
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            id=str(uuid.uuid4()),
            name=form.name.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        firebase_client.create_user(user.to_dict())
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')



@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Save report to Firebase
            report_id = str(uuid.uuid4())
            report = MedicalReport(
                report_id=report_id,
                user_id=current_user.id,
                file_path=filepath,
                upload_date=datetime.now()
            )
            firebase_client.save_report(report)
            
            return redirect(url_for('analyze_report', report_id=report_id))
    
    return render_template('upload.html')

@app.route('/analyze/<report_id>')
@login_required
def analyze_report(report_id):
    report = firebase_client.get_report(report_id)
    if report.user_id != current_user.id:
        return "Unauthorized", 403
    
    deficiencies = report_analyzer.analyze_report(report.file_path)
    min_days, max_days = report_analyzer.calculate_recovery_time(deficiencies)
    
    return render_template('deficiencies.html', 
                         deficiencies=deficiencies,
                         min_days=min_days,
                         max_days=max_days,
                         report_id=report_id)

@app.route('/generate_calendar', methods=['POST'])
@login_required
def generate_calendar():
    report_id = request.form['report_id']
    selected_days = int(request.form['days'])
    
    report = firebase_client.get_report(report_id)
    if report.user_id != current_user.id:
        return "Unauthorized", 403
    
    deficiencies = report_analyzer.analyze_report(report.file_path)
    calendar = calendar_generator.generate_calendar(
        deficiencies=deficiencies,
        days=selected_days,
        user_id=current_user.id
    )
    
    # Save calendar to Firebase
    firebase_client.save_recovery_plan(calendar)
    
    # Schedule notifications
    notification_manager.schedule_notifications(calendar)
    
    return redirect(url_for('view_calendar', plan_id=calendar.plan_id))

@app.route('/calendar/<plan_id>')
@login_required
def view_calendar(plan_id):
    plan = firebase_client.get_recovery_plan(plan_id)
    if plan.user_id != current_user.id:
        return "Unauthorized", 403
    
    return render_template('calendar.html', plan=plan)

@app.route('/daily_schedule/<plan_id>/<date>')
@login_required
def daily_schedule(plan_id, date):
    plan = firebase_client.get_recovery_plan(plan_id)
    if plan.user_id != current_user.id:
        return "Unauthorized", 403
    
    schedule_date = datetime.strptime(date, '%Y-%m-%d').date()
    daily_activities = plan.get_daily_activities(schedule_date)
    
    return render_template('daily_schedule.html', 
                         activities=daily_activities,
                         date=date,
                         plan_id=plan_id)

@app.route('/update_activity', methods=['POST'])
@login_required
def update_activity():
    data = request.get_json()
    plan_id = data['plan_id']
    date = data['date']
    activity_id = data['activity_id']
    completed = data['completed']
    
    plan = firebase_client.get_recovery_plan(plan_id)
    if plan.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    
    # Update activity status
    firebase_client.update_activity_status(plan_id, date, activity_id, completed)
    
    # If activity was missed, adjust the schedule
    if not completed:
        schedule_adjuster.adjust_schedule(plan_id, date, activity_id)
    
    return jsonify({"success": True})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)