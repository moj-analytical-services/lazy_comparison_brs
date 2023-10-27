import os
os.chdir("../")

from dataclasses import dataclass
import sqlglot
from splink.sql_transform import add_quotes_and_table_prefix


class BlockingRule:
    def __init__(
        self,
        blocking_rule,
        salting_partitions=1,
        sqlglot_dialect: str = None,
    ):

        self._sql_dialect = sqlglot_dialect

        self._blocking_rule = blocking_rule
        self.preceding_rules = []
        self.salting_partitions = salting_partitions

    @property
    def blocking_rule(self):
        return self._blocking_rule

    @property
    def sql_dialect(self):
        return getattr(self, "_sql_dialect", None)

    @sql_dialect.setter
    def sql_dialect(self, dialect):
        self._sql_dialect = dialect
        # setup our raw SQL strign
        self.generate_sql

    @property
    def generate_sql(self):
        # This doesn't need to do anything in the
        # underlying BR class...
        pass


@dataclass
class exact_match_rule(BlockingRule):

    col_name: str
    salting_partitions: int = 1

    @property
    def generate_sql(self):
        if self._sql_dialect:
            syntax_tree = sqlglot.parse_one(self.col_name, read=self._sql_dialect)

            l_col = add_quotes_and_table_prefix(syntax_tree, "l").sql(self._sql_dialect)
            r_col = add_quotes_and_table_prefix(syntax_tree, "r").sql(self._sql_dialect)

            blocking_rule = f"{l_col} = {r_col}"
            self._description = "Exact match"

            super().__init__(
                blocking_rule,
                salting_partitions=self.salting_partitions,
            )
        else:
            raise ValueError("No SQL dialect found. Please ensure you supply a dialect.")

    def __repr__(self):
        if not hasattr(self, "blocking_rule"):
            sql = f"l.{self.col_name} = r.{self.col_name}"
        else:
            sql = self.blocking_rule
        return f"<Exact match blocking on '{sql}'>"


t = exact_match_rule("test")
t.sql_dialect # blank

# Set the dialect to "duckdb"
t.sql_dialect = "duckdb"
t.blocking_rule
t

# Dynamically change the sql
t.sql_dialect = "spark"
t.blocking_rule
