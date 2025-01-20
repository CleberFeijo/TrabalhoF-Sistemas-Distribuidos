import regex as re

from fastapi.exceptions import RequestValidationError
from pydantic import Field
from typing import Optional

from common.classes import Undefined
from core.settings import env
from utils.pydantic import BaseModel, error_msg_map

from .response import ResponseModel

__all__ = 'RequestValidationErrorModel',


class ValidationErrorModel(BaseModel):
    """
    Objeto contendo o campo e a descrição do erro ocorrido durante a validação.
    """
    campo: str = Field(
        description='Campo incompleto ou inválido.',
        examples=['body'],
    )
    detalhes: str = Field(
        description='Detalhe do erro do campo.',
        examples=['Campo obrigatório sem valor informado.'],
    )
    erro: Optional[str] = Field(
        default_factory=Undefined if env.is_prod() else lambda: None,
        description='Tipo do erro ocorrido (Exceto em ambiente de prod.).',
        examples=['value_error.missing'],
    )


class RequestValidationErrorModel(ResponseModel):
    """
    Formato da resposta para erro de validação dos dados fornecidos para a
    requisição.
    """
    sucesso: bool = False
    detalhes: str = 'Dados da requisição incompletos e/ou inválidos.'
    erros: list[ValidationErrorModel]

    @classmethod
    def from_request_validation_error(cls, exc: RequestValidationError):
        """
        Cria uma instância desta classe, mantendo os atributos com valor
        padrão, preenchendo apenas o atributo "erros" com os dados extraídos
        da exceção informada.

        :param exc: Instância de "RequestValidationError" contendo as
            informações que serão remapeadas.
        """
        return cls(erros=cls._remap_errors(exc))

    # =========================== #
    # ~~~~| Private Methods |~~~~ #
    # =========================== #

    @classmethod
    def _remap_errors(cls, exc: RequestValidationError) -> list[ValidationErrorModel]:
        """
        Remapeia os erros contidos na exceção "RequestValidationError" informada
        para o formato adequado ao model "RequestValidationErrorModel".

        - Utiliza as mensagens mapeadas em "error_msg_templates", substituindo
          o "BaseSchema.Config.error_msg_templates" por não estar funcionando;

        :param exc: RequestValidationError ocorrida ao receber uma requisição;
        """
        errors: list[ValidationErrorModel] = []

        for error in exc.errors():
            err_msg = error.get('msg', '')
            err_type = error.get('type', '')

            errors.append(
                ValidationErrorModel(
                    # Ajusta o nome do campo, removendo o "__root__", para
                    # tornar a mensagem mais fácil de ser compreendida.
                    campo='.'.join([
                        str(x)
                        for x in error['loc']
                        if x != '__root__'
                    ]),
                    detalhes=cls._update_msg_from_ctx(
                        error_msg_map.get(err_type, err_msg),
                        error.get('ctx'),
                    ),
                    **({'erro': err_type} if not env.is_prod() else {}),
                )
            )
        return errors

    @staticmethod
    def _update_msg_from_ctx(err_msg: str, ctx: dict) -> str:
        """
        Converte os campos identificados na mensagem (entre chaves) para o
        respectivo valor encontrado no "ctx" do erro.

        - Aplica a lógica padrão do pydantic que aparentemente é removida
          quando a mensagem de erro é sobrescrita.
        """
        if not ctx:
            return err_msg

        # Para cada item encontrando no texto (entre chaves) contendo uma
        # informação no ctx, faz a conversão do texto para retornar o valor.
        for k, v in ctx.items():
            pattern = re.compile(r'\{' + str(k) + r'\}')

            # Se for um iterável de elementos, converte cada um deles pra string;
            if isinstance(v, (list, set, tuple)):
                v = [str(x) for x in v]

            err_msg = pattern.sub(str(v), err_msg)

        return err_msg
