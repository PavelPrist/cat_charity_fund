from typing import Optional

from pydantic import BaseSettings, EmailStr


PASSWORD_LENGTH = 3


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    description: str = 'Помощь котейкам'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'MOST_SECURE_SECRET'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
