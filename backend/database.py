from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from app.config import settings


def get_admin_engine():
    url = URL.create(
        "mysql+pymysql",
        username=settings.db_admin_user,
        password=settings.db_admin_password,
        host=settings.db_host,
        port=settings.db_port,
        database="mysql",
    )
    return create_engine(url, pool_pre_ping=True)


def get_readonly_engine():
    url = URL.create(
        "mysql+pymysql",
        username=settings.db_readonly_user,
        password=settings.db_readonly_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
    return create_engine(url, pool_pre_ping=True)