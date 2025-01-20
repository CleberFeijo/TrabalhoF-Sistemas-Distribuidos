from abc import abstractmethod
from fastapi import Request
from fastapi.responses import JSONResponse

from common.classes import GenericMeta
from common.typealiases import Generic, Type, ExceptionT

__all__ = 'ExceptionHandler',


class _ExceptionHandlerMeta(GenericMeta):
    def __new__(mcs, name, bases, attrs, **kwargs):
        if Generic not in bases:
            if not attrs.get('__exc_type__'):
                attrs['__exc_type__'] = mcs._get_generic_param(attrs)

            if attrs['__exc_type__'] is None:
                raise NotImplementedError(
                    f'Atributo de classe "__exc_type__"  da classe {name} deve '
                    f'ser implementado ou definido pela classe genérica.'
                )
            elif not issubclass(attrs['__exc_type__'], BaseException):
                raise ValueError(
                    f'Atributo de classe "__exc_type__" da classe {name} deve ser '
                    f'uma subclasse de "BaseException".'
                )
        return super().__new__(mcs, name, bases, attrs, **kwargs)


class ExceptionHandler(Generic[ExceptionT], metaclass=_ExceptionHandlerMeta):
    """
    Classe abstrata responsável por conter uma exceção e sua respectiva
    tratativa em caso de sua ocorrência durante uma requisição para a
    aplicação fastapi.

    - O atributo de classe `__exc_type__` pode ser definido explicitamente
      ou através do tipo anotado pela classe genérica.
    """
    __exc_type__: Type[ExceptionT]

    @staticmethod
    @abstractmethod
    def handler(request: Request, exc: ExceptionT) -> JSONResponse:
        """
        Método responsável por tratar a exceção ocorrida e convertê-la
        para um JSONResponse válido.

        Possui a assinatura utilizada pelos "exception_handlers" do FastAPI.

        :param request: Requisição recebida;
        :param exc: Instância da exceção mapeada no campo "exc_type";
        """
        pass

    @classmethod
    def dict(cls):
        return {cls.__exc_type__: cls.handler}
