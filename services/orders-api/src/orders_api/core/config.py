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


settings = Settings()
