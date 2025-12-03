from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional


class EmployeeCreate(BaseModel):
    """Схема для создания сотрудника с валидацией"""
    user_id: Optional[int] = None
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: EmailStr = Field(..., description="Email адрес сотрудника")
    passport_data: str = Field(..., min_length=10, description="Паспортные данные (минимум 10 символов)")
    inn: Optional[str] = Field(None, min_length=12, description="ИНН (минимум 12 символов)")
    snils: Optional[str] = Field(None, min_length=11, description="СНИЛС (минимум 11 символов)")
    department_id: int
    is_active: bool = True
    
    @validator('passport_data')
    def validate_passport_data(cls, v):
        if v and len(v) < 10:
            raise ValueError('Паспортные данные должны содержать не менее 10 символов')
        return v
    
    @validator('inn')
    def validate_inn(cls, v):
        if v is not None and len(v) < 12:
            raise ValueError('ИНН должен содержать не менее 12 символов')
        return v
    
    @validator('snils')
    def validate_snils(cls, v):
        if v is not None and len(v) < 11:
            raise ValueError('СНИЛС должен содержать не менее 11 символов')
        return v


class EmployeeUpdate(BaseModel):
    """Схема для обновления сотрудника с валидацией"""
    user_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = Field(None, description="Email адрес сотрудника")
    passport_data: Optional[str] = Field(None, min_length=10, description="Паспортные данные (минимум 10 символов)")
    inn: Optional[str] = Field(None, min_length=12, description="ИНН (минимум 12 символов)")
    snils: Optional[str] = Field(None, min_length=11, description="СНИЛС (минимум 11 символов)")
    department_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    @validator('passport_data')
    def validate_passport_data(cls, v):
        if v is not None and len(v) < 10:
            raise ValueError('Паспортные данные должны содержать не менее 10 символов')
        return v
    
    @validator('inn')
    def validate_inn(cls, v):
        if v is not None and len(v) < 12:
            raise ValueError('ИНН должен содержать не менее 12 символов')
        return v
    
    @validator('snils')
    def validate_snils(cls, v):
        if v is not None and len(v) < 11:
            raise ValueError('СНИЛС должен содержать не менее 11 символов')
        return v

