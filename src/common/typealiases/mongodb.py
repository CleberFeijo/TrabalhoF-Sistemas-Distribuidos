from pymongo.operations import (
    DeleteOne,
    DeleteMany,
    InsertOne,
    ReplaceOne,
    UpdateOne,
    UpdateMany,
)
from typing import Any, Iterable, Sequence, TypeAlias

__all__ = (
    'QueryT',
    'QueriesT',
    'QueryOrQueriesT',
    'ProjectionT',
    'PipelineStageT',
    'PipelineT',
    'FindSortT',
    'AggregateSortT',
    'HintT',
    'MongoDocumentT',
    'BulkWriteOperationT',
    'UpdateT',
)

QueryT: TypeAlias = dict[str, Any]
"""Alias para query usada pelo mongodb."""

QueriesT: TypeAlias = Iterable[QueryT]
"""Alias para iterável contendo múltiplas queries."""

QueryOrQueriesT: TypeAlias = QueryT | QueriesT
"""Alias para possibilidade de uma única query ou múltiplas queries."""

ProjectionT: TypeAlias = dict[str, bool]
"""Alias para projection usada pelo mongodb."""

PipelineStageT: TypeAlias = dict[str, str | int | dict[str, Any]]
"""Alias para um etapa de uma pipeline de uma aggregation mongodb."""

PipelineT: TypeAlias = list[PipelineStageT]
"""Alias para uma pipeline de uma aggregation mongodb."""

FindSortT: TypeAlias = Sequence[tuple[str, int]]
"""
Alias para ordenação (sort) do método `.find` mongodb;

- O valor inteiro deverá ser 1 (Ascending) ou -1 (Descending);
"""

AggregateSortT: TypeAlias = dict[str, int]
"""
Alias para dict de um estágio $sort de uma pipeline de `.aggregation` do
mongodb.

- O valor inteiro deverá ser 1 (Ascending) ou -1 (Descending);
"""

HintT: TypeAlias = str | Sequence[tuple[str, int | str | dict[str, Any]]]
"""
Alias para o hint de qual índice deve ser utilizado durante o método `.find`
ou `.aggregate`.
"""

MongoDocumentT: TypeAlias = dict[str, Any]
"""Alias para os documentos retornados de consultas diretas no mongodb."""

BulkWriteOperationT: TypeAlias = InsertOne | UpdateOne | UpdateMany | ReplaceOne | DeleteOne | DeleteMany
"""
Alias para qualquer tipo de operação utilizada durante o método "bulk_write"
de uma collection mongodb.
"""

UpdateT: TypeAlias = dict[str, dict[str, Any]]
"""
Alias para um dict que representa uma operação de atualização de um registro do
mongodb.

- Como chave, utilize uma das seguintes opções: "$set", "$unset",
  "$setOnInsert", "$push", "$addToSet", etc.
"""
