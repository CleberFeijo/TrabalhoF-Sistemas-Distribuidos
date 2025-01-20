from dataclasses import dataclass
from fastapi import status
from pydantic import BaseModel
from typing import Any, Optional, Union, Type

from common.classes import UNDEFINED

from ..models import RequestValidationErrorModel

__all__ = 'OpenAPISchema', 'OpenAPISchemaFactory',


@dataclass
class OpenAPIDefaults:
    status_code: int
    description: str
    model: Optional[Type[BaseModel]] = UNDEFINED


class OpenAPISchema(dict):
    """
    Subclasse de dict usada para descrever um schema OpenAPI para a
    documentação automática do swagger/redoc.

    - Contém somente os dados que não são definidos automaticamente pelo
      FastAPI, ou quando há a necessidade de sobrescrevê-los.
    - Utiliza os campos definidos como padrão quando os mesmos não são
      informados durante a instanciação.
    """

    __defaults__: tuple[OpenAPIDefaults, ...] = (
        OpenAPIDefaults(
            status_code=status.HTTP_200_OK,
            description='Requisição concluída com sucesso.',
        ),
        OpenAPIDefaults(
            status_code=status.HTTP_201_CREATED,
            description='Recurso criado com sucesso.',
        ),
        OpenAPIDefaults(
            status_code=status.HTTP_202_ACCEPTED,
            description='Solicitação recebida com processamento pendente.',
        ),
        OpenAPIDefaults(
            status_code=status.HTTP_204_NO_CONTENT,
            description='Requisição concluída com sucesso sem resposta.',
            model=None,
        ),
        OpenAPIDefaults(
            status_code=status.HTTP_400_BAD_REQUEST,
            description='Solicitação inválida.',
            model=None,
        ),
        OpenAPIDefaults(
            status_code=status.HTTP_404_NOT_FOUND,
            description='Página ou recurso não encontrado.',
            model=None,
        ),
        OpenAPIDefaults(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            description='Método não permitido para a rota informada.',
            model=None,
        ),
        OpenAPIDefaults(
            status_code=status.HTTP_409_CONFLICT,
            description='Conflito com o atual estado do recurso.',
            model=None,
        ),
        OpenAPIDefaults(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            description='Erro durante validação dos dados fornecidos para a '
                        'requisição.',
            model=RequestValidationErrorModel,
        ),
    )
    "Tupla contendo os padrões de resposta por status."

    @classmethod
    def _get_defaults(cls, status_code: int) -> OpenAPIDefaults:
        for d in cls.__defaults__:
            if d.status_code == status_code:
                return d
        raise ValueError(f'{status_code} não tem um schema padrão.')

    def __init__(
            self,
            status_code: int,
            description: Optional[str] = UNDEFINED,
            model: Optional[BaseModel] = UNDEFINED,
            **kwargs,
    ):
        super().__init__()
        self.status_code = status_code

        default = self._get_defaults(status_code)

        def _add_to_schema(key: str, value: Any):
            if value != UNDEFINED:
                self[key] = value
            elif getattr(default, key, UNDEFINED) != UNDEFINED:
                self[key] = getattr(default, key)

        _add_to_schema('description', description)
        _add_to_schema('model', model)


class OpenAPISchemaFactory:
    """
    Classe que utiliza um conceito similar ao "factory method".

    Recebe múltiplos argumentos posicionais durante a instanciação, que podem
    ser do tipo `int` (referente ao status_code), `dict` (contendo os kwargs
    de instanciação de um `OpenAPISchema`) ou `OpenAPISchema`;

    Retorna um dict contendo a correlação do `status_code` com a instância de
    `OpenAPISchema` recebida (ou convertida a partir de qualquer outro tipo
    recebido) para cada argumento posicional recebido.

    - Feito especificamente para ser utilizado em conjunto com o parâmetro
      "responses" de uma instância de `FastAPI`, `APIRouter` (ou em conjunto
      com as rotas de uma classe `@cbv`);
    """

    def __new__(
            cls,
            *schemas: Union[int, dict, OpenAPISchema],
            **kwargs
    ) -> dict[int, OpenAPISchema]:
        openapi_schema = {}
        for schema in schemas:
            schema = cls._create_schema(schema)
            openapi_schema[schema.status_code] = schema
        return openapi_schema

    @staticmethod
    def _create_schema(schema: Union[int, dict, OpenAPISchema]) -> OpenAPISchema:
        if isinstance(schema, OpenAPISchema):
            return schema
        elif isinstance(schema, int):
            return OpenAPISchema(status_code=schema)
        elif isinstance(schema, dict):
            return OpenAPISchema(**schema)

        raise TypeError(schema)
