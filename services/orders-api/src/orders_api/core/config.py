from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração da API, lida das variáveis de ambiente."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Orders API"
    app_version: str = "0.1.0"
    environment: str = "local"

    users_table: str = "users"
    orders_table: str = "orders"
    notifications_table: str = "notifications"

    kafka_bootstrap_servers: str = "localhost:9092"

    aws_region: str = "us-east-1"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    dynamodb_endpoint_url: str | None = None

    jwt_secret_key: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
