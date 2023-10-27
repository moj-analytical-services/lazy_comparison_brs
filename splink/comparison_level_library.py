from __future__ import annotations

import warnings

from .comparison_level import ComparisonLevel
from .input_column import InputColumn


class NullLevelBase(ComparisonLevel):
    def __init__(
        self,
        col_name,
        valid_string_pattern: str = None,
        invalid_dates_as_null: bool = False,
        valid_string_regex: str = None,
    ) -> ComparisonLevel:
        # TODO: Remove this compatibility code in a future release once we drop
        # support for "valid_string_regex". Deprecation warning added in 3.9.6
        if valid_string_pattern is not None and valid_string_regex is not None:
            # user supplied both
            raise TypeError("Just use valid_string_pattern")
        elif valid_string_pattern is not None:
            # user is doing it correctly
            pass
        elif valid_string_regex is not None:
            # user is using deprecated argument
            warnings.warn(
                "valid_string_regex is deprecated; use valid_string_pattern",
                DeprecationWarning,
                stacklevel=2,
            )
            valid_string_pattern = valid_string_regex

        col = InputColumn(col_name, sql_dialect=self._sql_dialect)
        col_name_l, col_name_r = col.name_l(), col.name_r()

        if invalid_dates_as_null:
            col_name_l = self._valid_date_function(col_name_l, valid_string_pattern)
            col_name_r = self._valid_date_function(col_name_r, valid_string_pattern)
            sql = f"""{col_name_l} IS NULL OR {col_name_r} IS NULL OR
                      {col_name_l}=='' OR {col_name_r} ==''"""
        elif valid_string_pattern:
            col_name_l = self._regex_extract_function(col_name_l, valid_string_pattern)
            col_name_r = self._regex_extract_function(col_name_r, valid_string_pattern)
            sql = f"""{col_name_l} IS NULL OR {col_name_r} IS NULL OR
                      {col_name_l}=='' OR {col_name_r} ==''"""
        else:
            sql = f"{col_name_l} IS NULL OR {col_name_r} IS NULL"

        level_dict = {
            "sql_condition": sql,
            "label_for_charts": "Null",
            "is_null_level": True,
        }
        super().__init__(level_dict, sql_dialect=self._sql_dialect)


class ExactMatchLevelBase(ComparisonLevel):
    def __init__(
        self,
        col_name,
        regex_extract: str = None,
        set_to_lowercase: bool = False,
        m_probability=None,
        term_frequency_adjustments=False,
        include_colname_in_charts_label=False,
        manual_col_name_for_charts_label=None,
    ) -> ComparisonLevel:

        col = InputColumn(col_name, sql_dialect=self._sql_dialect)

        if include_colname_in_charts_label:
            label_suffix = f" {col_name}"
        elif manual_col_name_for_charts_label:
            label_suffix = f" {manual_col_name_for_charts_label}"
        else:
            label_suffix = ""

        col_name_l, col_name_r = col.name_l(), col.name_r()

        if set_to_lowercase:
            col_name_l = f"lower({col_name_l})"
            col_name_r = f"lower({col_name_r})"

        if regex_extract:
            col_name_l = self._regex_extract_function(col_name_l, regex_extract)
            col_name_r = self._regex_extract_function(col_name_r, regex_extract)

        sql_cond = f"{col_name_l} = {col_name_r}"
        level_dict = {
            "sql_condition": sql_cond,
            "label_for_charts": f"Exact match{label_suffix}",
        }
        if m_probability:
            level_dict["m_probability"] = m_probability
        if term_frequency_adjustments:
            level_dict["tf_adjustment_column"] = col_name

        super().__init__(level_dict, sql_dialect=self._sql_dialect)


class ElseLevelBase(ComparisonLevel):
    def __init__(
        self,
        m_probability=None,
    ) -> ComparisonLevel:
        if isinstance(m_probability, str):
            raise ValueError(
                "You provided a string for the value of m probability when it should "
                "be numeric.  Perhaps you passed a column name.  Note that you do "
                "not need to pass a column name into the else level."
            )
        level_dict = {
            "sql_condition": "ELSE",
            "label_for_charts": "All other comparisons",
        }
        if m_probability:
            level_dict["m_probability"] = m_probability
        super().__init__(level_dict)


class DistanceFunctionLevelBase(ComparisonLevel):
    def __init__(
        self,
        col_name: str,
        distance_function_name: str,
        distance_threshold: int | float,
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
            f"{distance_function_name.capitalize()}{label_suffix} {operator} "
            f"{distance_threshold}"
        )

        level_dict = {
            "sql_condition": sql_cond,
            "label_for_charts": chart_label,
        }
        if m_probability:
            level_dict["m_probability"] = m_probability

        super().__init__(level_dict, sql_dialect=self._sql_dialect)

    @property
    def _distance_level(self):
        raise NotImplementedError("Distance function not supported in this dialect")


class DamerauLevenshteinLevelBase(DistanceFunctionLevelBase):
    def __init__(
        self,
        col_name: str,
        distance_threshold: int,
        regex_extract: str = None,
        set_to_lowercase=False,
        include_colname_in_charts_label=False,
        manual_col_name_for_charts_label=None,
        m_probability=None,
    ) -> ComparisonLevel:
        super().__init__(
            col_name,
            distance_function_name=self._damerau_levenshtein_name,
            distance_threshold=distance_threshold,
            regex_extract=regex_extract,
            set_to_lowercase=set_to_lowercase,
            higher_is_more_similar=False,
            include_colname_in_charts_label=include_colname_in_charts_label,
            m_probability=m_probability,
        )
