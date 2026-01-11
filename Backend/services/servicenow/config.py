"""ServiceNow configuration."""
from pydantic_settings import BaseSettings
from Backend.settings import settings


class ServiceNowSettings(BaseSettings):
    """ServiceNow configuration settings."""

    instance_url: str = settings.servicenow_instance_url
    table_name: str = settings.servicenow_table_name
    username: str = settings.servicenow_username
    password: str = settings.servicenow_password

    @property
    def table_api_url(self) -> str:
        """Get the full table API URL."""
        return f"{self.instance_url}/api/now/table/{self.table_name}"

    class Config:
        """Pydantic configuration."""

        env_prefix = "SERVICENOW_"
        case_sensitive = False


servicenow_settings = ServiceNowSettings()
