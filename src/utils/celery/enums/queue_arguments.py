from aenum import StrEnum

__all__ = 'OverflowParamEnum', 'QueueModeParamEnum',


class OverflowParamEnum(StrEnum):
    DROP_HEAD = 'drop-head'
    "Dropa a mensagem mais antiga."

    REJECT_PUBLISH = 'reject-publish'
    "Rejeita novas mensagens."

    REJECT_PUBLISH_DLX = 'reject-publish-dlx'
    "Rejeita novas mensagens e as manda para o 'dead-letter exchange'."


class QueueModeParamEnum(StrEnum):
    DEFAULT = 'default'
    "Fila padrão."

    LAZY = 'lazy'
    "Mensagens são paginadas em disco para reduzir o uso de memória."

    SINGLE_ACTIVE_CONSUMER = 'single-active-consumer'
    "Apenas um 'consumer' recebe mensagens da fila por vez."
