import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3307"))
    db_name: str = os.getenv("DB_NAME", "businesslens")
    db_admin_user: str = os.getenv("DB_ADMIN_USER", "root")
    db_admin_password: str = os.getenv("DB_ADMIN_PASSWORD", "")
    db_readonly_user: str = os.getenv("DB_READONLY_USER", "businesslens_ro")
    db_readonly_password: str = os.getenv("DB_READONLY_PASSWORD", "")


settings = Settings()