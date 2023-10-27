from .dialect_bases.dialect_base import DialectBase

from .dialect_bases.duckdb_base import DuckDBBase
from .dialect_bases.postgres_base import PostgresBase


def _dialect_base_factory(dialect) -> DialectBase:
    """Constructs an exporter factory based on the user's preference."""

    factories = {
        "duckdb": DuckDBBase,
        "postgres": PostgresBase,
    }

    if dialect in factories:
        return factories[dialect]
    else:
        raise ValueError(
            "Dialect not recognised."
        )
