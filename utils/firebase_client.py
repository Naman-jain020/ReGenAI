import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime
from config import Config
from models.user import User
from models.medical_report import MedicalReport
from models.recovery_plan import RecoveryPlan
from typing import List

class FirebaseClient:
    def __init__(self):
        if not firebase_admin._apps:
            try:
                # Initialize with the service account key
                cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred, {
                    'projectId': Config.FIREBASE_PROJECT_ID,
                    'storageBucket': Config.FIREBASE_STORAGE_BUCKET
                })
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Firebase: {str(e)}")
        
        self.db = firestore.client()
    
    # User operations
    def get_user(self, user_id: str) -> User:
        doc = self.db.collection('users').document(user_id).get()
        if doc.exists:
            return User.from_dict(doc.to_dict())
        return None
    
    def create_user(self, user_data: dict) -> User:
        user_ref = self.db.collection('users').document(user_data['id'])
        user_ref.set(user_data)
        return User.from_dict(user_data)
    
    # Report operations
    def save_report(self, report: MedicalReport):
        self.db.collection('medical_reports').document(report.report_id).set(report.to_dict())
    
    def get_report(self, report_id: str) -> MedicalReport:
        doc = self.db.collection('medical_reports').document(report_id).get()
        if doc.exists:
            return MedicalReport.from_dict(doc.to_dict())
        return None
    
    def get_user_reports(self, user_id: str) -> List[MedicalReport]:
        docs = self.db.collection('medical_reports').where('user_id', '==', user_id).get()
        return [MedicalReport.from_dict(doc.to_dict()) for doc in docs]
    
    # Recovery plan operations
    def save_recovery_plan(self, plan: RecoveryPlan):
        self.db.collection('recovery_plans').document(plan.plan_id).set(plan.to_dict())
    
    def get_recovery_plan(self, plan_id: str) -> RecoveryPlan:
        doc = self.db.collection('recovery_plans').document(plan_id).get()
        if doc.exists:
            return RecoveryPlan.from_dict(doc.to_dict())
        return None
    
    def get_user_plans(self, user_id: str) -> List[RecoveryPlan]:
        docs = self.db.collection('recovery_plans').where('user_id', '==', user_id).get()
        return [RecoveryPlan.from_dict(doc.to_dict()) for doc in docs]
    
    def get_user_by_email(self, email: str) -> User:
        docs = self.db.collection('users').where('email', '==', email).limit(1).get()
        if docs:
            return User.from_dict(docs[0].to_dict())
        return None
    
    def update_activity_status(self, plan_id: str, date_str: str, activity_id: str, completed: bool):
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        plan_ref = self.db.collection('recovery_plans').document(plan_id)
        
        # Get the current plan
        plan = self.get_recovery_plan(plan_id)
        if not plan:
            return
        
        # Find and update the activity
        updated = False
        for activity in plan.daily_activities.get(date, []):
            if activity.id == activity_id:
                activity.completed = completed
                updated = True
                break
        
        if updated:
            # Save the updated plan
            plan_ref.set(plan.to_dict())
    
    def update_recovery_plan(self, plan: RecoveryPlan):
        self.db.collection('recovery_plans').document(plan.plan_id).set(plan.to_dict())
    
    def log_notification(self, plan_id: str, date: str, activity_id: str, timestamp: datetime):
        log_data = {
            'plan_id': plan_id,
            'date': date,
            'activity_id': activity_id,
            'timestamp': timestamp
        }
        self.db.collection('notification_logs').add(log_data)