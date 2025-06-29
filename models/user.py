from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, id: str, email: str, name: str, password_hash: str = None, medical_history: dict = None):
        self.id = id
        self.email = email
        self.name = name
        self.password_hash = password_hash
        self.medical_history = medical_history or {}
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'password_hash': self.password_hash,
            'medical_history': self.medical_history
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            email=data.get('email'),
            name=data.get('name'),
            password_hash=data.get('password_hash'),
            medical_history=data.get('medical_history', {})
        )