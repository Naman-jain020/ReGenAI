class Deficiency:
    def __init__(self, name: str, current_value: str, normal_range: str, 
                 severity: str = "medium", is_border_value: bool = False):
        self.name = name
        self.current_value = current_value
        self.normal_range = normal_range
        self.severity = severity  # low, medium, high
        self.is_border_value = is_border_value
    
    def to_dict(self):
        return {
            'name': self.name,
            'current_value': self.current_value,
            'normal_range': self.normal_range,
            'severity': self.severity,
            'is_border_value': self.is_border_value
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get('name'),
            current_value=data.get('current_value'),
            normal_range=data.get('normal_range'),
            severity=data.get('severity', 'medium'),
            is_border_value=data.get('is_border_value', False)
        )