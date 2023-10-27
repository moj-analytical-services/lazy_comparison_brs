import sys
sys.path.append("../")

from dataclasses import dataclass

from splink.input_column import InputColumn
# from comparisons.distance_fn import DistanceFunctionLevelBase
from comp_level_factories.dialect_factories.dialect_base_classes import _dialect_base_factory


class ComparisonLevel:
    def __init__(
        self,
        level_dict,
        comparison=None,
        # sql_dialect=None,
    ):
        # Protected, because we don't want to modify the original dict
        self._level_dict = level_dict
        self.comparison = comparison

        # This breaks downstream inheritance.
        # Specifically when we create a new class with:
        # DamerauLevenshteinLevel and Base Class.
        # SQL dialect has already been set, so throws this.
        # self._sql_dialect = sql_dialect

    @property
    def sql_dialect(self):
        return getattr(self, "_sql_dialect", None)

    @sql_dialect.setter
    def sql_dialect(self, dialect):
        self._sql_dialect = dialect
        # setup our raw SQL string
        self._generate_sql

    @property
    def is_null_level(self):
        return self._is_null_level

    @property
    def sql_condition(self):
        return self._sql_condition


class DistanceFunctionLevelBase(ComparisonLevel):
    def __init__(
        self,
        col_name: str,
        distance_function_name: str,
        distance_threshold,
        regex_extract: str = None,
        set_to_lowercase=False,
        higher_is_more_similar: bool = True,
        include_colname_in_charts_label=False,
        manual_col_name_for_charts_label=None,
        m_probability=None,
    ) -> ComparisonLevel:

        col = InputColumn(col_name, sql_dialect=self._sql_dialect)

        if higher_is_more_similar:
            operator = ">="
        else:
            operator = "<="

        col_name_l, col_name_r = col.name_l(), col.name_r()

        if set_to_lowercase:
            col_name_l = f"lower({col_name_l})"
            col_name_r = f"lower({col_name_r})"

        if regex_extract:
            col_name_l = self._regex_extract_function(col_name_l, regex_extract)
            col_name_r = self._regex_extract_function(col_name_r, regex_extract)

        sql_cond = (
            f"{distance_function_name}({col_name_l}, {col_name_r}) "
            f"{operator} {distance_threshold}"
        )

        if include_colname_in_charts_label:
            if manual_col_name_for_charts_label:
                col_name = manual_col_name_for_charts_label

            label_suffix = f" {col_name}"
        else:
            label_suffix = ""

        chart_label = (
        #     f"{distance_function_name.capitalize()}{label_suffix} {operator} "
            f"{distance_function_name}{label_suffix} {operator} "
            f"{distance_threshold}"
        )

        level_dict = {
            "sql_condition": sql_cond,
            "label_for_charts": chart_label,
        }
        if m_probability:
            level_dict["m_probability"] = m_probability

        super().__init__(level_dict)

    @property
    def _distance_level(self):
        raise NotImplementedError("Distance function not supported in this dialect")


@dataclass
class DamerauLevenshteinLevel(DistanceFunctionLevelBase):

    col_name: str
    distance_threshold: int
    regex_extract: str = None
    set_to_lowercase=False
    include_colname_in_charts_label=False
    manual_col_name_for_charts_label=None
    m_probability: float = None
    # sql_dialect: str = None  # do we want this as an arg?

    def __post_init__(self):
        # If the dialect has already been set,
        # run the function as normal.

        # This should only be in cases where the base class has been set.
        # All other instances should trigger the _sql_dialect setter.
        if hasattr(self, "_sql_dialect"):
            self._generate_sql

    @property
    def _generate_sql(self):

        # Dialect is set by the setter -> triggers this...
        base_class = _dialect_base_factory(self.sql_dialect)()
        # We could also try some Type magic here...

        super().__init__(
            self.col_name,
            distance_function_name=base_class._damerau_levenshtein_name,
            distance_threshold=self.distance_threshold,
            regex_extract=self.regex_extract,
            set_to_lowercase=self.set_to_lowercase,
            higher_is_more_similar=False,
            include_colname_in_charts_label=self.include_colname_in_charts_label,
            m_probability=self.m_probability,
        )


# _dialect_base_factory("duckdb")._damerau_levenshtein_name # works
# _dialect_base_factory("postgres")._damerau_levenshtein_name # errors


t = DamerauLevenshteinLevel("help", 3)
t.sql_dialect # blank

# Set the dialect to "duckdb"
t.sql_dialect = "duckdb"
t.comparison
t  # constructs our cll

# errors...
# t.sql_dialect = "postgres"
# t.comparison


class ComparisonImportsFactory:
    # Will house ALL potential levels. We can then
    # lazily evaluate them and assess if they can be
    # used in the Splink model.

    def __init__(self, sql_dialect):
        # Dynamically sets the base class - e.g. DuckDBBase
        self.base = _dialect_base_factory(sql_dialect)

    @property
    def _damerau_levenshtein_level(self):
        return type(
            "DamerauLevenshteinLevel",
            (self.base, DamerauLevenshteinLevel,),
            {}
        )


# Creates the class needed to use the dam lev level
# They're not being triggered...
# Shouldn't the setter be working its magic???
ComparisonImportsFactory(
    "duckdb")._damerau_levenshtein_level(
    "help", 3
)._sql_dialect

# This errors...
ComparisonImportsFactory(
    "postgres")._damerau_levenshtein_level(
    "help", 3
)
