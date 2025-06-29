from datetime import datetime
from typing import List
from models.deficiency import Deficiency

class MedicalReport:
    def __init__(self, report_id: str, user_id: str, file_path: str, upload_date: datetime, 
                 deficiencies: List[Deficiency] = None):
        self.report_id = report_id
        self.user_id = user_id
        self.file_path = file_path
        self.upload_date = upload_date
        self.deficiencies = deficiencies or []
    
    def to_dict(self):
        return {
            'report_id': self.report_id,
            'user_id': self.user_id,
            'file_path': self.file_path,
            'upload_date': self.upload_date.isoformat(),
            'deficiencies': [d.to_dict() for d in self.deficiencies]
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        from datetime import datetime
        deficiencies = [Deficiency.from_dict(d) for d in data.get('deficiencies', [])]
        return cls(
            report_id=data.get('report_id'),
            user_id=data.get('user_id'),
            file_path=data.get('file_path'),
            upload_date=datetime.fromisoformat(data.get('upload_date')),
            deficiencies=deficiencies
        )