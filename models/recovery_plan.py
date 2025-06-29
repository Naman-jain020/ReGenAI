from datetime import date, datetime
from typing import Dict, List
from models.deficiency import Deficiency
import uuid

class DailyActivity:
    def __init__(self, time: str, activity_type: str, description: str, 
                 duration: str = "", intensity: str = "medium", 
                 is_critical: bool = False, completed: bool = False):
        self.id = str(uuid.uuid4())
        self.time = time  # morning, afternoon, evening
        self.activity_type = activity_type  # exercise, diet, medication, rest
        self.description = description
        self.duration = duration  # in minutes for exercises
        self.intensity = intensity  # low, medium, high
        self.is_critical = is_critical  # whether missing this would significantly impact recovery
        self.completed = completed
    
    def copy(self):
        return DailyActivity(
            time=self.time,
            activity_type=self.activity_type,
            description=self.description,
            duration=self.duration,
            intensity=self.intensity,
            is_critical=self.is_critical,
            completed=self.completed
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'time': self.time,
            'activity_type': self.activity_type,
            'description': self.description,
            'duration': self.duration,
            'intensity': self.intensity,
            'is_critical': self.is_critical,
            'completed': self.completed
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            time=data.get('time'),
            activity_type=data.get('activity_type'),
            description=data.get('description'),
            duration=data.get('duration', ''),
            intensity=data.get('intensity', 'medium'),
            is_critical=data.get('is_critical', False),
            completed=data.get('completed', False)
        )

class RecoveryPlan:
    def __init__(self, plan_id: str, user_id: str, start_date: date, end_date: date, 
                 deficiencies: List[Deficiency], daily_activities: Dict[date, List[DailyActivity]]):
        self.plan_id = plan_id
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.deficiencies = deficiencies
        self.daily_activities = daily_activities
    
    def get_daily_activities(self, date: date) -> List[DailyActivity]:
        return self.daily_activities.get(date, [])
    
    def to_dict(self):
        return {
            'plan_id': self.plan_id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'deficiencies': [d.to_dict() for d in self.deficiencies],
            'daily_activities': {
                date.isoformat(): [a.to_dict() for a in activities]
                for date, activities in self.daily_activities.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        from datetime import date
        deficiencies = [Deficiency.from_dict(d) for d in data.get('deficiencies', [])]
        daily_activities = {
            date.fromisoformat(d): [DailyActivity.from_dict(a) for a in activities]
            for d, activities in data.get('daily_activities', {}).items()
        }
        return cls(
            plan_id=data.get('plan_id'),
            user_id=data.get('user_id'),
            start_date=date.fromisoformat(data.get('start_date')),
            end_date=date.fromisoformat(data.get('end_date')),
            deficiencies=deficiencies,
            daily_activities=daily_activities
        )