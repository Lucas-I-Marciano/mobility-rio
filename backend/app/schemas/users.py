from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from app.db.user import UserBase

# Schema para criar um usuário (recebe senha em texto plano)
class UserCreate(UserBase):
    password: str = Field(min_length=8) # Exige senha no input

# Schema para ler/retornar dados do usuário (sem senha)
class UserRead(UserBase):
    id: int

# Schema para atualizar um usuário (todos os campos opcionais)
# Não herda de UserBase diretamente para tornar campos opcionais facilmente
class UserUpdate(SQLModel):
    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = Field(default=None)
    password: Optional[str] = Field(default=None, min_length=8)

# Schema para resposta de deleção (opcional)
class DeleteResponse(SQLModel):
    message: str