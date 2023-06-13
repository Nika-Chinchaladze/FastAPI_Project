"""Module is responsible to get and hold ENVIRONMENTAL VARIABLES."""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """class is responsible for getting values of environmental variables."""

    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
