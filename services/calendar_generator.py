from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from models.recovery_plan import RecoveryPlan, DailyActivity
from models.deficiency import Deficiency
from utils.gemini_client import GeminiClient
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
from config import Config
from dotenv import load_dotenv

load_dotenv()

class CalendarGenerator:
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    def generate_calendar(self, deficiencies: List[Deficiency], days: int, user_id: str) -> RecoveryPlan:
        plan_id = f"plan_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days-1)
        
        # Generate the recovery plan using Gemini
        prompt = self._build_calendar_prompt(deficiencies, days)
        response = self.gemini_client.generate_text(prompt)
        
        # Parse the response
        daily_activities = self._parse_calendar_response(response, start_date, end_date)
        
        # Create the recovery plan
        plan = RecoveryPlan(
            plan_id=plan_id,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            deficiencies=deficiencies,
            daily_activities=daily_activities
        )
        
        return plan
    
    def _build_calendar_prompt(self, deficiencies: List[Deficiency], days: int) -> str:
        deficiency_list = "\n".join([
            f"- {d.name}: Current {d.current_value}, Normal range {d.normal_range}, Severity: {d.severity}"
            for d in deficiencies
        ])
        
        prompt = f"""
        Create a detailed recovery plan calendar for {days} days to address the following deficiencies:
        {deficiency_list}
        
        The plan should include:
        1. Daily exercises tailored to the deficiencies
        2. A diet plan with specific meals and supplements
        3. Medication schedule if needed
        4. Rest periods and sleep recommendations
        
        For each day, provide:
        - Morning, afternoon, and evening activities
        - Specific exercises with duration and intensity
        - Meals with ingredients and portions
        - Medications with dosage and timing
        - Any additional recommendations
        
        Format the output as JSON with the following structure:
        {{
            "daily_plans": [
                {{
                    "day": 1,
                    "date": "YYYY-MM-DD",
                    "activities": [
                        {{
                            "time": "morning/afternoon/evening",
                            "type": "exercise/diet/medication/rest",
                            "description": "Detailed description",
                            "duration": "Duration in minutes if applicable",
                            "intensity": "low/medium/high if applicable",
                            "is_critical": true/false
                        }},
                        ...
                    ]
                }},
                ...
            ]
        }}
        """
        
        return prompt
    
    def _parse_calendar_response(self, response: str, start_date: datetime, end_date: datetime) -> Dict[datetime, List[DailyActivity]]:
        daily_activities = {}
        
        try:
            # Extract JSON part from the response
            import re
            import json
            json_str = re.search(r'\{.*\}', response, re.DOTALL).group()
            data = json.loads(json_str)
            
            current_date = start_date
            for day_plan in data.get('daily_plans', []):
                activities = []
                for activity_data in day_plan.get('activities', []):
                    activity = DailyActivity(
                        time=activity_data.get('time', 'morning'),
                        activity_type=activity_data.get('type', 'exercise'),
                        description=activity_data.get('description', ''),
                        duration=activity_data.get('duration', ''),
                        intensity=activity_data.get('intensity', 'medium'),
                        is_critical=activity_data.get('is_critical', False),
                        completed=False
                    )
                    activities.append(activity)
                
                daily_activities[current_date] = activities
                current_date += timedelta(days=1)
                
                if current_date > end_date:
                    break
        except Exception as e:
            print(f"Error parsing calendar response: {e}")
            # Fallback to generating a simple plan if parsing fails
            current_date = start_date
            while current_date <= end_date:
                activities = []
                # Morning exercise
                activities.append(DailyActivity(
                    time="morning",
                    activity_type="exercise",
                    description="30 minute walk",
                    duration="30",
                    intensity="low",
                    is_critical=True,
                    completed=False
                ))
                # Breakfast
                activities.append(DailyActivity(
                    time="morning",
                    activity_type="diet",
                    description="Balanced breakfast with proteins and vitamins",
                    duration="",
                    intensity="",
                    is_critical=True,
                    completed=False
                ))
                # Add more default activities as needed
                
                daily_activities[current_date] = activities
                current_date += timedelta(days=1)
        
        return daily_activities