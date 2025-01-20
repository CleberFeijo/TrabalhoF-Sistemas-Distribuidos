from .value_error_msg import *
from .type_error_msg import *

error_msg_map: dict[str, str] = {
    **value_error_msg,
    **type_error_msg,
}
"Mapeia os erros do pydantic com suas respectivas mensagens em pt-br."
