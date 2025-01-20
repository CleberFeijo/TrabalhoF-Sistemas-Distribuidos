"""
Módulo contendo as classes responsáveis por serializar/deserializar objetos
python para outros formatos (JSON, MongoDB ou até mesmo outros objetos python).

- Dependências:
- common.classes;
- utils.enums;
- utils.functions;
- common.typealiases;
"""
from .classes import *
from .decoders import *
from .encoders import *
