"""
Módulo responsável por agregar à lib nativa `typing` alguns typealiases e
typevars genéricos.

- Importar este módulo utilizando "*" (wildcard) também importará o módulo
  "typing".

- Dependências:
- N/A;
"""
from typing import *  # noqa: F401 ("Unused import statement")

from .common import *
from .mongodb import *
from .typevar import *
