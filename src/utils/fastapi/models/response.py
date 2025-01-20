from pydantic import Field

from utils.pydantic import BaseModel, ObjectIdField, ListField, DictField

__all__ = 'ResponseModel', 'InsertResponseModel', "ResponseModelList", \
"ResponseModelDict"


class ResponseModel(BaseModel):
    """Model padrão para respostas das APIs."""
    sucesso: bool = Field(
        default=True,
        description='Indica se a requisição foi concluída com sucesso.',
    )
    detalhes: str = Field(
        description='Descrição da resposta da requisição.',
        examples=['Requisição concluída com sucesso!'],
    )


class ResponseModelList(BaseModel):
    message: str = Field(
        default="Sucesso",
        description='Traz a mensagem de falha ou sucesso da requisição.',
    )
    data: ListField = Field(
        description='Lista tratada da resposta.',
    )


class ResponseModelDict(BaseModel):
    message: str = Field(
        default="Sucesso",
        description='Traz a mensagem de falha ou sucesso da requisição.',
    )
    data: DictField = Field(
        description='Dicionário tratado da resposta.',
    )


class InsertResponseModel(ResponseModel):
    """Modelo padrão para respostas sobre inserção de registros."""
    id: ObjectIdField | None = Field(
        description="""
            Id do registro inserido ou None em caso de erro durante a inserção.
        """,
    )
