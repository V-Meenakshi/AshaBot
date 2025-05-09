#auth_service.py
from pydantic import BaseModel
from typing import Optional, Dict

# Simple user models
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class SimpleAuthService:
    def __init__(self):
        # In-memory user database
        self.users: Dict[str, dict] = {}
    
    def create_user(self, user: UserCreate) -> User:
        # Store user (in a real app, you'd hash the password)
        user_data = user.dict()
        password = user_data.pop("password")  # Remove password from returned user
        
        # Store user with password in private dict
        self.users[user.username] = {
            **user_data,
            "password": password  # In production, hash this!
        }
        
        # Return user without password
        return User(**user_data)
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        # Check if user exists and password matches
        if username in self.users and self.users[username]["password"] == password:
            # Return user data without password
            user_data = self.users[username].copy()
            user_data.pop("password")
            return User(**user_data)
        return None
