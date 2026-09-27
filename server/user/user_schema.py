import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from fastapi import HTTPException

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    confirm_password: str

    @field_validator('email', 'username', 'password', 'confirm_password')
    def check_empty(cls, v):
        if not v or v.isspace():
            raise HTTPException(status_code=422, detail="필수 항목을 입력해주세요.")
        return v
    
    @field_validator('confirm_password')
    def check_password(cls, v, values: FieldValidationInfo):
        if 'password' in values.data and v != values.data['password']:
            raise HTTPException(status_code=422, detail="비밀번호가 일치하지 않습니다.")
        return v

class UsernameUpdate(BaseModel):
    username: str

    @field_validator('username')
    def check_empty(cls, v):
        if not v or v.isspace():
            raise HTTPException(status_code=422, detail="필수 항목을 입력해주세요.")
        return v

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str

    @field_validator('current_password', 'new_password', 'confirm_new_password')
    def check_empty(cls, v):
        if not v or v.isspace():
            raise HTTPException(status_code=422, detail="필수 항목을 입력해주세요.")
        return v
    
    @field_validator('confirm_new_password')
    def check_password(cls, v, values: FieldValidationInfo):
        if 'new_password' in values.data and v != values.data['new_password']:
            raise HTTPException(status_code=422, detail="비밀번호가 일치하지 않습니다.")
        return v

class UserInfo(BaseModel):
    """비밀번호 해시를 응답에서 제외하기 위한 사용자 정보 스키마"""
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    user_name: str
    user_email: str
    user_status: str | None
    created_at: datetime.datetime
    last_connected_at: datetime.datetime | None

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    email: str