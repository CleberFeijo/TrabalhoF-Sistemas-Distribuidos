"""
Módulo responsável por agregar à lib `pydantic` um "BaseModel" personalizado,
alguns campos genéricos, mapear as mensagens de erro pra versão pt-br, etc.

Dependências:
    - common.classes;
    - common.serializers;
"""
from .decorators import *
from .fields import *
from .functions import *
from .locale import *
from .models import *
