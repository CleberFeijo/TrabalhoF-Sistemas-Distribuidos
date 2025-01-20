from common.classes import UNDEFINED
from common.typealiases import Any, Generic, Iterator, Literal, TypeAlias, T

from .base import BaseModel

__all__ = 'RootListModel',

IncExT: TypeAlias = set[int] | set[str] | dict[int, Any] | dict[str, Any] | None
"Alias para os parâmetros 'include' e 'exclude' do método de json dump."


class RootListModel(BaseModel, Generic[T]):
    """
    Subclasse de `utils.pydantic.BaseModel` que implementa uma lógica similar
    a de `pydantic.RootModel`, porém mais específica para listas de dados.
    """
    root: list[T]

    def __init__(self, *args, root=UNDEFINED):
        if root != UNDEFINED:
            super().__init__(root=root)
        elif args:
            if len(args) == 1 and isinstance(args[0], (list, set, tuple)):
                super().__init__(root=args[0])
            else:
                super().__init__(root=args)
        else:
            super().__init__(root=[])

    def __str__(self):
        return super().__str__().replace('root=', '')

    def __iter__(self) -> Iterator[T]:
        return iter(self.root)

    def __len__(self):
        return len(self.root)

    def __getitem__(self, item) -> T:
        return self.root[item]

    def __setitem__(self, key, value):
        self.root[key] = value

    def __eq__(self, other):
        return self.root == other

    def model_dump_json(
        self,
        *,
        indent: int | None = None,
        include: IncExT = None,
        exclude: IncExT = None,
        context: Any | None = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool | Literal['none', 'warn', 'error'] = True,
        serialize_as_any: bool = False,
    ) -> str:
        jsons: str = super().model_dump_json(
            indent=indent,
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
        )
        return jsons[8:-1]  # Converte '{"root": <valor>}' para '<valor>'
