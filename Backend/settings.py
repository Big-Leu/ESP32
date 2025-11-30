import enum
import os
from pathlib import Path
from tempfile import gettempdir

import yaml
from catilo import catilo  # type: ignore
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL
from loguru import logger

TEMP_DIR = Path(gettempdir())


cfg = catilo.VariableDirectory()
# cfg.clear()
cfg.add_file_source("DefaultConfig", 10, "default.yml")

print(os.getcwd())
try:
    cfg.add_file_source("MainConfig", 5, "config.yml")
except Exception:
    logger.warning("No config file found, using default")

with open("config.yml", "r") as f:
    cfg_data = yaml.safe_load(f)
    print(cfg_data)
cfg.add_source("YamlConfig", 4, cfg_data)


cfg.enable_environment_vars("AUDITROL_", strip=True)


class LogLevel(enum.StrEnum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = cfg.get("BACKEND_HOST")
    port: int = cfg.get("BACKEND_PORT")
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = cfg.get("BACKEND_RELOAD")

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    users_secret: str = os.getenv("USERS_SECRET", "")
    # Variables for the database
    db_host: str = cfg.get("BACKEND_DB_HOST")
    db_port: int = cfg.get("BACKEND_DB_PORT")
    db_user: str = cfg.get("BACKEND_DB_USER")
    db_pass: str = cfg.get("BACKEND_DB_PASS")  # noqa: S105
    db_base: str = cfg.get("BACKEND_DB_BASE")
    db_echo: bool = cfg.get("BACKEND_DB_ECHO")
    # Variables for Redis
    redis_host: str = "Backend-redis"
    redis_port: int = 6379
    redis_user: str | None = None
    redis_pass: str | None = None
    redis_base: int | None = None

    # This variable is used to define
    # multiproc_dir. It's required for [uvi|guni]corn projects.
    prometheus_dir: Path = TEMP_DIR / "prom"

    # Grpc endpoint for opentelemetry.
    # E.G. http://localhost:4317
    opentelemetry_endpoint: str | None = None

    # Alert configuration
    sustain_seconds: int = cfg.get("SUSTAIN_SECONDS")

    # Twilio SMS configuration
    twilio_sid: str | None = cfg.get("TWILIO_SID")
    twilio_token: str | None = cfg.get("TWILIO_TOKEN")
    twilio_phone: str | None = cfg.get("TWILIO_PHONE")
    alert_phone: str | None = cfg.get("ALERT_PHONE")
    # SendGrid email configuration
    sendgrid_api_key: str | None = cfg.get("SENDGRID_API_KEY")
    from_email: str | None = cfg.get("FROM_EMAIL")
    alert_email: str | None = cfg.get("ALERT_EMAIL")
    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    @property
    def redis_url(self) -> URL:
        """
        Assemble REDIS URL from settings.

        :return: redis URL.
        """
        path = ""
        if self.redis_base is not None:
            path = f"/{self.redis_base}"
        return URL.build(
            scheme="redis",
            host=self.redis_host,
            port=self.redis_port,
            user=self.redis_user,
            password=self.redis_pass,
            path=path,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BACKEND_",
        env_file_encoding="utf-8",
    )


settings = Settings()
