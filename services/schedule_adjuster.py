from models.recovery_plan import RecoveryPlan
from utils.firebase_client import FirebaseClient
from services.calendar_generator import CalendarGenerator
from datetime import datetime, timedelta
from typing import Dict, List

class ScheduleAdjuster:
    def __init__(self):
        self.firebase_client = FirebaseClient()
        self.calendar_generator = CalendarGenerator()
    
    def adjust_schedule(self, plan_id: str, missed_date: str, missed_activity_id: str):
        # Get the current plan
        plan = self.firebase_client.get_recovery_plan(plan_id)
        if not plan:
            return
        
        # Find the missed activity
        date_obj = datetime.strptime(missed_date, '%Y-%m-%d').date()
        missed_activity = None
        daily_activities = plan.daily_activities.get(date_obj, [])
        
        for activity in daily_activities:
            if activity.id == missed_activity_id:
                missed_activity = activity
                break
        
        if not missed_activity:
            return
        
        # Determine adjustment strategy based on activity criticality
        if missed_activity.is_critical:
            self._adjust_for_critical_miss(plan, date_obj, missed_activity)
        else:
            self._adjust_for_non_critical_miss(plan, date_obj, missed_activity)
    
    def _adjust_for_critical_miss(self, plan: RecoveryPlan, missed_date: datetime, missed_activity):
        # For critical misses, we need to extend the plan or intensify remaining days
        remaining_days = (plan.end_date - missed_date).days
        
        if remaining_days > 3:
            # Spread the missed activity over next 3 days
            for i in range(1, 4):
                adjust_date = missed_date + timedelta(days=i)
                if adjust_date in plan.daily_activities:
                    # Add a modified version of the missed activity
                    adjusted_activity = missed_activity.copy()
                    adjusted_activity.duration = str(int(adjusted_activity.duration) // 3) if adjusted_activity.duration else ""
                    plan.daily_activities[adjust_date].append(adjusted_activity)
        else:
            # Extend the plan by 1 day and add the missed activity
            plan.end_date += timedelta(days=1)
            new_date = plan.end_date
            plan.daily_activities[new_date] = [missed_activity]
        
        # Update the plan in Firebase
        self.firebase_client.update_recovery_plan(plan)
    
    def _adjust_for_non_critical_miss(self, plan: RecoveryPlan, missed_date: datetime, missed_activity):
        # For non-critical misses, we can either add to next day or leave it
        next_date = missed_date + timedelta(days=1)
        
        if next_date <= plan.end_date:
            if next_date in plan.daily_activities:
                # Add the missed activity to the next day
                plan.daily_activities[next_date].append(missed_activity)
            else:
                plan.daily_activities[next_date] = [missed_activity]
            
            # Update the plan in Firebase
            self.firebase_client.update_recovery_plan(plan)