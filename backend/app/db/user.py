from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, max_length=50)
    email: EmailStr = Field(index=True, unique=True) # Usa EmailStr para validação básica

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False) # Armazena o hash, não a senha