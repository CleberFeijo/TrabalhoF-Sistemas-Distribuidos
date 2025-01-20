"""
Módulo responsável por agregar à lib `fastapi` algumas funcionalidades
genéricas bastante utilizadas entre projetos, como modelos de base para
respostas, classes de controle de exceções, dependências genéricas, etc.

Dependências:
    - common.classes;
    - common.typealiases
    - core.settings;
    - utils.pydantic;
"""
from .app import *
from .classes import *
from .dependencies import *
from .exception_handlers import *
from .factories import *
from .functions import *
from .models import *
from .servers import *
