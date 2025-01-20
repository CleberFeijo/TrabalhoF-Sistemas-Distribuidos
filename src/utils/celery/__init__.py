"""
Módulo responsável por agregar à lib `celery` algumas funcionalidades
genéricas bastante utilizadas entre projetos, como modelos de base para
tarefas, *factory classes* para a construção de configurações do celery,
etc.

- Compatível com "pymongo", "requests" e "httpx" (mas não obrigatório).

Dependências:
    - common.classes;
    - common.typealiases
    - core.settings;
    - utils.pydantic;
"""
from .classes import *
from .enums import *
from .factories import *
from .functions import *
from .models import *
