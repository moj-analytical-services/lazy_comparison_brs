from .dialect_base import (
    DialectBase,
)

def regex_extract_sql(col_name, regex):
    return f"""
        regexp_extract({col_name}, '{regex}')
    """


class DuckDBBase(DialectBase):
    @property
    def _sql_dialect(self):
        return "duckdb"

    @property
    def _regex_extract_function(self):
        return regex_extract_sql

    @property
    def _damerau_levenshtein_name(self):
        return "damerau_levenshtein"
