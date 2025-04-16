from ninja import Schema
from pydantic import EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
import re

# Esquemas para autenticação
class TokenSchema(Schema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayloadSchema(Schema):
    user_id: int
    exp: datetime

class LoginSchema(Schema):
    email: EmailStr
    password: str

class PasswordResetRequestSchema(Schema):
    email: EmailStr

class PasswordResetConfirmSchema(Schema):
    token: str
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        """Valida a força da senha."""
        if len(v) < 8:
            raise ValueError('A senha deve ter pelo menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('A senha deve conter pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('A senha deve conter pelo menos uma letra minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('A senha deve conter pelo menos um número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('A senha deve conter pelo menos um caractere especial')
        return v

# Esquemas para operações de usuário
class UserCreateSchema(Schema):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    user_type: str = Field(default="client", pattern="^(client|provider|admin)$")
    preferred_language: str = Field(default="pt-br", pattern="^(pt-br|en|es)$")
    
    @validator('password')
    def password_strength(cls, v):
        """Valida a força da senha."""
        if len(v) < 8:
            raise ValueError('A senha deve ter pelo menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('A senha deve conter pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('A senha deve conter pelo menos uma letra minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('A senha deve conter pelo menos um número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('A senha deve conter pelo menos um caractere especial')
        return v

class UserUpdateSchema(Schema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = Field(default=None, pattern="^(pt-br|en|es)$")

class UserPreferenceSchema(Schema):
    notification_type: str = Field(pattern="^(html|text)$")
    receive_reminders: bool
    report_frequency: str = Field(pattern="^(never|daily|weekly|monthly)$")

class UserPreferenceUpdateSchema(Schema):
    notification_type: Optional[str] = Field(default=None, pattern="^(html|text)$")
    receive_reminders: Optional[bool] = None
    report_frequency: Optional[str] = Field(default=None, pattern="^(never|daily|weekly|monthly)$")

class UserOutSchema(Schema):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    user_type: str
    preferred_language: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

# Esquema para resposta de erro
class ErrorSchema(Schema):
    detail: str 