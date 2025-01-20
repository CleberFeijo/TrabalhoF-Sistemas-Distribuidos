from pydantic import Field

from common.classes import Undefined
from utils.pydantic import BaseModel

from ..enums import *

__all__ = 'QueueArguments',


class QueueArguments(BaseModel):
    max_priority: int = Field(
        default_factory=Undefined,
        alias='x-max-priority',
        le=9,
        ge=0,
    )
    """
    Define o valor máximo de prioridade que as mensagens podem ter.
    Mensagens de maior prioridade serão entregues antes das de menor prioridade.
    """

    message_ttl: int = Field(
        default_factory=Undefined,
        alias='x-message-ttl',
        ge=0,
    )
    "Define um tempo de vida (em milisegundos) para as mensagens dessa fila."

    expires: int = Field(
        default_factory=Undefined,
        alias='x-expires',
        ge=0,
    )
    """
    Define um tempo de expiração (em milisegundos) para a fila. A fila será
    deletada se estiver ociosa por um período de tempo superior ao valor
    estipulado.
    """

    overflow: OverflowParamEnum = Field(
        default_factory=Undefined,
        alias='x-overflow',
    )
    "Especifica o comportamento quando a fila estiver cheia."

    queue_mode: QueueModeParamEnum = Field(
        default_factory=Undefined,
        alias='x-queue-mode',
    )
    "Especifica o comportamento quando a fila estiver cheia."

    max_length: int = Field(
        default_factory=Undefined,
        alias='x-max-length',
    )
    """
    Determina um número máximo de mensagens que a fila pode conter. Ao atingir
    o valor máximo, mensagens novas serão tratadas conforme comportamento
    especificado pelo parâmetro 'x-overflow'.
    """

    max_length_bytes: int = Field(
        default_factory=Undefined,
        alias='x-max-length-bytes',
    )
    """
    Determina um número máximo em bytes que a fila pode conter. Ao atingir o
    valor máximo, mensagens novas serão tratadas conforme comportamento
    especificado pelo parâmetro 'x-overflow'.
    """
