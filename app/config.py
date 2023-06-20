"""Module is responsible to get and hold ENVIRONMENTAL VARIABLES."""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """class is responsible for getting values of environmental variables."""

    db_hostname: str
    db_username: str
    db_password: str
    db_port: str
    db_name: str
    db_name_test: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
