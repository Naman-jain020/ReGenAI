import schedule
import time
from threading import Thread
from datetime import datetime, timedelta
from utils.firebase_client import FirebaseClient
import os
from plyer import notification

class NotificationManager:
    def __init__(self):
        self.firebase_client = FirebaseClient()
        self.running = False
        self.thread = None
    
    def schedule_notifications(self, recovery_plan):
        # Clear any existing notifications
        schedule.clear()
        
        # Schedule notifications for each activity in the plan
        current_date = recovery_plan.start_date
        end_date = recovery_plan.end_date
        
        while current_date <= end_date:
            if current_date in recovery_plan.daily_activities:
                for activity in recovery_plan.daily_activities[current_date]:
                    # Determine notification time based on activity time
                    if activity.time == "morning":
                        notify_time = "08:00"
                    elif activity.time == "afternoon":
                        notify_time = "13:00"
                    else:  # evening
                        notify_time = "18:00"
                    
                    # Schedule the notification
                    schedule.every().day.at(notify_time).do(
                        self.send_notification,
                        title=f"Recovery Activity: {activity.activity_type}",
                        message=activity.description,
                        plan_id=recovery_plan.plan_id,
                        date=current_date.strftime('%Y-%m-%d'),
                        activity_id=activity.id
                    )
            
            current_date += timedelta(days=1)
        
        # Start the scheduler in a separate thread if not already running
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.run_scheduler)
            self.thread.start()
    
    def send_notification(self, title, message, plan_id, date, activity_id):
        # Send desktop notification
        notification.notify(
            title=title,
            message=message,
            app_name="Medical Recovery Planner"
        )
        
        # Log the notification in Firebase
        self.firebase_client.log_notification(
            plan_id=plan_id,
            date=date,
            activity_id=activity_id,
            timestamp=datetime.now()
        )
    
    def run_scheduler(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()