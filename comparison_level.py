from copy import copy
from comparison_level_creator import ComparisonLevelCreator


level1 = {
    "sql_condition": "first_name_l IS NULL OR first_name_r IS NULL",
    # "label_for_charts": "Comparison includes null",
    "is_null_level": True,
}

level2 = {
    "sql_condition": "first_name_l = first_name_r",
    "label_for_charts": "Exact match",
    "m_probability": 0.7,
    "u_probability": 0.1,
    "tf_adjustment_column": "first_name",
    "tf_adjustment_weight": 0.6,
}

level3 = {
    "sql_condition": "first_name_l IS NULL OR first_name_r IS NULL",
}

# Inheritance is only needed to gain access to the 'configure' method...
class ComparisonLevel(ComparisonLevelCreator):

    def __init__(
        self,
        sql_condition: str,
        label_for_charts: str = None,
        # sql_dialect: str = None,
    ):
        self.sql_condition = sql_condition

        if label_for_charts is None:
            self.label_for_charts = sql_condition
        else:
            self.label_for_charts = label_for_charts

    def create_sql(self) -> str:
        return self.sql_condition

    def create_label_for_charts(self) -> str:
        return self.label_for_charts

    @classmethod
    def with_level_dict(cls, level_dict: dict):
        """Alternate constructor. Used if a dictionary has been
        supplied.
        """

        # Not necessarily required, but pop alters the original object
        level_dict = copy(level_dict)

        # a series of get calls + configure...
        # Popped for easier demo'ing...
        sql_condition = level_dict.pop("sql_condition")  # error if not provided...
        label_for_charts = level_dict.pop("label_for_charts", None)

        return cls(sql_condition, label_for_charts).configure(**level_dict)

    def __repr__(self):
        return f"Hello, I'm a comparison level for '{self.sql_condition}'"


# Deserialise dictionaries
display(ComparisonLevel.with_level_dict(level1))
display(ComparisonLevel.with_level_dict(level2))
display(ComparisonLevel.with_level_dict(level3))

# Construct directly with a ComparisonLevel and arg names...
display(ComparisonLevel(sql_condition="my_col_l = my_col_r"))

ComparisonLevel(sql_condition="my_col_l = my_col_r")
