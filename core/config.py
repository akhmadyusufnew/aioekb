from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    ADMIN_ID: int
    CHANNEL_MDB_ID: int
    GROUP_MONITORING_KLIK_ID: int
    GROUP_MONITORING_SUPPORT_TOKO: int
    GROUP_MONITORING_EDP_R1: int

    class Config:
        env_file = ".env"


settings = Settings()
