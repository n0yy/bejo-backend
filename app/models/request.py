from pydantic import BaseModel
from typing import Literal


class ChatRequest(BaseModel):
    question: str
    category: str


class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    division: str
    role: str = "user"
    status: Literal["pending", "active", "reject"] = "pending"
    category: Literal["1", "2", "3", "4"] = "1"


class UserLogin(BaseModel):
    email: str
    password: str
