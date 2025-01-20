from copy import deepcopy
from pydantic import (
    BaseModel as PydanticBaseModel,
    ConfigDict as PydanticConfigDict,
    model_validator,
)
from pydantic.fields import FieldInfo  # noqa

from common.classes import Undefined
from common.serializers import JSONEncoder, Decoder
from common.typealiases import *

__all__ = 'BaseModel', 'ConfigDict',

encoder = JSONEncoder()
"Instância de *encoding*."

decoder = Decoder()
"Instância de *decoding*."

# Type Aliases
AbstractSetIntOrStrT: TypeAlias = AbstractSet[int | str]
MappingIntOrStrT: TypeAlias = Mapping[int | str, Any]
SetOrMappingT: TypeAlias = Union[AbstractSetIntOrStrT, MappingIntOrStrT]


# noinspection PydanticTypeChecker
class _BaseModelMeta(type(PydanticBaseModel)):

    def __new__(cls, *args, **kwargs):

        # name, bases, attrs
        name, _, attrs = args

        # Adiciona um root validator padrão.
        attrs['__root_json_decoder'] = \
            model_validator(mode='before')(cls._root_json_decoder)

        new_type = super().__new__(cls, *args, **kwargs)

        # Captura a lista de campos a serem removidos do model_config.
        config = attrs.get('model_config', None)

        # Caso exista algum campo definido em "inherit_from_schema", cada campo
        # encontrado únicamente numa superclasse que não está listada em
        # "inherit_from_schema" será removido.
        inherit_from_schema = config.get('inherit_from_schema') or []
        cls._inherit_from_schema(new_type, inherit_from_schema)

        # Para cada campo definido em "exclude_from_schema", irá remover toda
        # referência para este campo, removendo-o completamente da nova classe.
        exclude_from_schema = config.get('exclude_from_schema') or []
        cls._exclude_from_schema(new_type, exclude_from_schema)

        # Para cada campo definido em "optional_fields" (ou todos se o valor
        # for True), irá alterar o typehint e o model para determinar o campo
        # como opcional.
        optional_fields = config.get('optional_fields') or []
        cls._optional_fields(new_type, optional_fields)

        return new_type

    @classmethod
    def _inherit_from_schema(cls, new_type, inherit_from_schema: list[str]):
        if not inherit_from_schema:
            return

        remove_fields = []
        "Lista de campos que serão removidos do model."

        for f in new_type.model_fields:
            if f in inherit_from_schema:
                continue

            # Se alguma super classe tiver o campo, ele será removido por não
            # estar na lista de heranças.
            if any([f in getattr(scls, 'model_fields', []) for scls in new_type.__mro__]):
                remove_fields.append(f)

        cls._exclude_from_schema(new_type, remove_fields)

    @staticmethod
    def _exclude_from_schema(new_type, exclude_from_schema: list[str]):
        for field in exclude_from_schema:
            for f in ('__annotations__', 'model_fields'):
                getattr(new_type, f, {}).pop(field, None)

    @staticmethod
    def _optional_fields(new_type, optional_fields: list[str] | Literal[True]):
        if optional_fields is True:
            optional_fields = getattr(new_type, 'model_fields', None)

        for field in (optional_fields or []):
            a_type = new_type.model_fields[field].annotation

            # Checa se o campo já é opcional.
            if get_origin(a_type) is Union and type(None) in get_args(a_type):
                continue

            # Atualiza o typehint.
            new_type.__annotations__[field] = Optional[a_type]

            # Cria um novo "FieldInfo" com base no antigo.
            new_info = deepcopy(new_type.model_fields[field])
            new_info.default = None
            new_info.annotation = Optional[field.annotation]
            new_type.model_fields[field] = new_info

    @staticmethod
    def _root_json_decoder(cls, values: dict):
        decoders: dict[type, Callable[[Any, type], Any]] = \
            getattr(cls, 'model_config', {}).get('json_decoders', {})

        # Se nenhum decoder for informado, retorna os valores padrão.
        if not decoders:
            return values

        # Função auxiliar de chamada recursiva para realizar decoding de
        # anotações aninhadas
        def _decode(_v, *_annotations):
            for _annotation in _annotations:
                _origin = get_origin(_annotation) or _annotation

                if _origin in decoders:
                    return decoders[_origin](_v, _origin)

                try:
                    # Tratativa para "dict-like".
                    if issubclass(_origin, Mapping) and isinstance(_v, Mapping):
                        args = get_args(_annotation)
                        key_type = args[0] if args else Any
                        value_type = args[1] if len(args) >= 2 else Any
                        return {
                            _decode(k, key_type): _decode(v, value_type)
                            for k, v in _v.items()
                        }

                    # Tratativa para "list-like".
                    if issubclass(_origin, Iterable) \
                            and not issubclass(_annotation, str) \
                            and isinstance(_v, Iterable) \
                            and not isinstance(_v, str):
                        return _origin(_decode(v, *get_args(_annotation)) for v in _v)  # noqa

                except TypeError:
                    pass

                # Se o tipo anotado possuir um subtipo com mesmo método __init__,
                # tenta checar se há um decoder para o mesmo.
                # Se sim, realiza o decode utilizando o decoder da superclasse.

                # noinspection PyBroadException
                try:
                    for _superclass in _origin.__mro__:
                        if _superclass in decoders and (_superclass.__init__ is _origin.__init__):
                            return decoders[_superclass](_v, _origin)
                except Exception:
                    pass

            return _v

        # Itera sobre os campos contidos em model_fields (contém os campos herdados).
        model_fields: dict[str, FieldInfo] = getattr(cls, 'model_fields', {})

        if isinstance(values, MutableMapping):
            for name, info in model_fields.items():
                if name in values:
                    pass
                elif info.alias and info.alias in values:
                    name = info.alias
                else:
                    continue
                values[name] = _decode(values[name], info.annotation)

        return values


class ConfigDict(PydanticConfigDict, total=False):
    """
    Subclasse de `pydantic.ConfigDict`, adicionando configurações comumente
    utilizadas no projeto, incrementando as funcionalidades da Modelagem do
    pydantic.
    """
    inherit_from_schema: Iterable[str]
    """
    Determina que esta classe irá herdar **APENAS** os atributos da(s)
    superclasse(s) que estiverem aqui listados - Não deve ser usado em conjunto
    com "exclude_from_schema".
    """

    exclude_from_schema: Iterable[str]
    """
    Determina que esta classe irá herdar todos os atributos da(s)
    superclasse(s) **EXCETO** os que estiverem aqui listados - Não deve ser
    usado em conjunto com "inherit_from_schema".
    """

    optional_fields: Iterable[str] | Literal[True]
    """
    Determina que os atributos herdados da(s) superclasse(s) aqui listados
    serão definidos como `Optional`, com valor default igual a None.

    Em caso de valor `True`, aplica este efeito a todos os atributos.
    """

    json_decoders: dict[Type[T], Callable[[Any, Type[T]], T]]
    """
    Permite que os atributos anotados com o tipo contido na chave do dict
    informado possam ser previamente tratados/convertidos pela função contida
    no valor do dict informado (que recebe dois parâmetros, sendo o primeiro
    o valor de input e o segundo o tipo igual à chave do dict e que deve
    retornar uma instância do tipo informado) antes da validação do pydantic

    Ex.:
        - Converter str para ObjectId;
        - Converter str no formato "%d/%m/%Y" para date;
    """


class BaseModel(PydanticBaseModel, metaclass=_BaseModelMeta):
    """
    Subclasse de `pydantic.BaseModel`, adicionando configurações comumente
    utilizadas no projeto.
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        coerce_numbers_to_str=True,
        extra='forbid',
        json_decoders={
            t: decoder.load
            for t in decoder.decoding_types()
            if isinstance(t, type)
        },
        json_encoders={
            t: encoder.dump
            for t in encoder.encoding_types()
            if isinstance(t, type)
        },
        populate_by_name=True,
    )

    def model_dump(
            self,
            *,
            mode: Literal['json', 'python'] | str = 'python',
            include: SetOrMappingT | None = None,
            exclude: SetOrMappingT | None = None,
            context: Any | None = None,
            by_alias: bool = True,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            exclude_undefined: bool = True,
            round_trip: bool = False,
            warnings: Literal['none', 'warn', 'error'] | bool = True,
            serialize_as_any: bool = False
    ) -> dict[str, Any]:
        return {
            k: v
            for k, v in super().model_dump(
                mode=mode,
                include=include,
                exclude=exclude,
                context=context,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                round_trip=round_trip,
                warnings=warnings,
                serialize_as_any=serialize_as_any,
            ).items()

            if not (exclude_undefined and isinstance(v, Undefined))
        }
