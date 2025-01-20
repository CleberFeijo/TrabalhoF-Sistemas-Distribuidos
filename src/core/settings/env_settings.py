from ipaddress import IPv4Address
from pydantic import AmqpDsn, HttpUrl, MongoDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from common.enums import EnvEnum

__all__ = 'env_settings', 'env',


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )

    APP_PORT: str
    "Porta da aplicação FastAPI."

    APP_WORKERS: int
    "Quantidade de workers servindo a aplicação gunicorn."

    CELERY_BROKER_API_URL: str

    CELERY_RESULT_BACKEND: str | None = None
    "String de conexão (opcional) usado como 'result backend' pelo celery."

    COMPOSE_PROJECT_NAME: str
    "Nome do projeto e diretório de trabalho dentro do container docker."

    ENV: EnvEnum
    "Determina o tipo de ambiente que se está executando a aplicação."

    HOST_IP: IPv4Address
    "IPv4 do servidor onde a aplicação está hospedada."

    RABBITMQ_DEFAULT_USER: str
    "Usuário do rabbitMQ local."

    RABBITMQ_DEFAULT_PASS: SecretStr
    "Senha do rabbitMQ local."

    RABBITMQ_PORT: str
    "Porta exposta do rabbitMQ local."

    # noinspection PyPep8Naming
    @property
    def CELERY_LOCAL_BROKER_URL(self) -> AmqpDsn:
        """
        Cria a string de conexão do 'message broker' do celery local com base
        nos parâmetros de criação do rabbitmq local.
        """
        return 'amqp://{}:{}@rabbitmq:{}/?authSource=admin'.format(
            self.RABBITMQ_DEFAULT_USER,
            self.RABBITMQ_DEFAULT_PASS.get_secret_value(),
            self.RABBITMQ_PORT,
        )


env_settings = EnvSettings()
"""Singleton contendo as variáveis de ambiente."""

env = env_settings.ENV
"""
Alias para `env_settings.ENV`;

Determina o tipo de ambiente que se está executando a aplicação.
"""
