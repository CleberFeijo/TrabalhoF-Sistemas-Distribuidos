from dataclasses import dataclass
from inspect import Parameter, Signature, signature
from pydantic import create_model

from common.typealiases import Any, Callable, Iterable, Iterator, Optional, T

from ..models import BaseModel, ConfigDict

__all__ = 'decode_parameters',


def decode_parameters(*args):
    """
    Decorator responsável por validar e converter os valores dos parâmetros
    da função decorada de acordo com os tipos anotados.

    Pode ser usado como ``@decode_parameters`` ou ``@decode_parameters()`` -
    sendo possível, no segundo caso, especificar os campos que devem ser
    validados/convertidos.
    """
    _func = args[0] if len(args) == 1 and isinstance(args[0], Callable) else None
    _args_to_decode = None if _func else args

    def decorator(func):
        def wrapper(*args_, **kwargs_):
            pd = _ParameterDecoder(function=func, args_to_decode=_args_to_decode)
            return pd.decode_and_run(*args_, **kwargs_)

        return wrapper

    return decorator(_func) if _func else decorator


@dataclass
class _ParameterDecoder:
    """
    Classe auxiliar responsável por realizar o decode dos parâmetros de uma função
    de acordo com o tipo anotado.
    """
    function: Callable[..., T]
    "Função de base para a criação do model."

    args_to_decode: Optional[Iterable[str]] = None
    "Determina o nome dos parâmetros que podem/devem receber o decode."

    _signature: Signature = None

    def __post_init__(self):
        self._signature = signature(self.function, follow_wrapped=True)

    class _ParameterDecoderBaseModel(BaseModel):
        """Classe de base para a criação do model temporário."""
        model_config = ConfigDict(extra='ignore')

    # ============================ #
    # ~~~~| Instance Methods |~~~~ #
    # ============================ #

    def decode_and_run(self, *args, **kwargs) -> T:
        args_ = []
        kwargs_ = {}

        ParameterDecoderBaseModel = self._create_parameter_model(*args, **kwargs)
        model = ParameterDecoderBaseModel(**self._signature.bind(*args, **kwargs).arguments)
        model_dict = model.model_dump(exclude_unset=True)

        for arg, value in self._it_args(*args, **kwargs):
            value = model_dict.get(arg, value)

            # Seta o valor como arg ou kwarg.
            kind = self._signature.parameters[arg].kind

            if kind == Parameter.KEYWORD_ONLY:
                kwargs_[arg] = value
            elif kind == Parameter.VAR_KEYWORD:
                kwargs_.update(value)
            elif kind == Parameter.VAR_POSITIONAL:
                args_.extend(value)
            else:
                args_.append(value)

        return self.function(*args_, **kwargs_)

    # =========================== #
    # ~~~~| Private Methods |~~~~ #
    # =========================== #

    def _create_parameter_model(self, *args, **kwargs):
        model_params = {}

        for i, (arg, _) in enumerate(self._it_args(*args, **kwargs)):
            if self.args_to_decode and arg not in self.args_to_decode:
                continue

            # Remove "self" do model em caso da função ser "__init__".
            elif i == 0 and self.function.__name__ == '__init__':
                continue

            annotation = self._signature.parameters[arg].annotation
            kind = self._signature.parameters[arg].kind

            # Define o tipo vinculado ao valor informado.
            if kind == Parameter.VAR_KEYWORD:
                model_params[arg] = (Optional[dict[str, Any]], None)
            elif kind == Parameter.VAR_POSITIONAL:
                model_params[arg] = (Optional[tuple], None)
            elif annotation == Parameter.empty:
                model_params[arg] = (Any, ...)
            else:
                model_params[arg] = (annotation, ...)

        # Cria o model temporário.
        return create_model(
            'ParameterDecoderBaseModel',
            **model_params,
            __base__=self._ParameterDecoderBaseModel,
        )

    def _it_args(self, *args, **kwargs) -> Iterator[tuple[str, Any]]:
        yield from self._signature.bind(*args, **kwargs).arguments.items()
