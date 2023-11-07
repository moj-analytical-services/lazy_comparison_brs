from copy import copy


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

class ComparisonLevel:

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

    # Feels more natural to have this on here. We can also inherit and this will work as expected...
    def configure(
        self,
        *,
        m_probability: float = None,
        u_probability: float = None,
        tf_adjustment_column: str = None,
        tf_adjustment_weight: float = None,
        tf_minimum_u_value: float = None,
        is_null_level: bool = None,
    ) -> "ComparisonLevel":
        """
        Configure the comparison level with options which are common to all
        comparison levels.  The options align to the keys in the json
        specification of a comparison level.  These options are usually not
        needed, but are available for advanced users.


        Args:
            m_probability (float, optional): The m probability for this
                comparison level. Defaults to None, meaning it is not set.
            u_probability (float, optional): The u probability for this
                comparison level. Defaults to None, meaning it is not set.
            tf_adjustment_column (str, optional): Make term frequency adjustments for
                this comparison level using this input column. Defaults to None,
                meaning term-frequency adjustments will not be applied for this level.
            tf_adjustment_weight (float, optional): Make term frequency adjustments
                for this comparison level using this weight. Defaults to None,
                meaning term-frequency adjustments are fully-weighted if turned on.
            tf_minimum_u_value (float, optional): When term frequency adjustments are
                turned on, where the term frequency adjustment implies a u value below
                this value, use this minimum value instead. Defaults to None, meaning
                no minimum value.
            is_null_level (bool, optional): If true, m and u values will not be
                estimated and instead the match weight will be zero for this column.
                Defaults to None, equivalent to False.

        Returns:
            ComparisonLevelCreator: The instance of the ComparisonLevelCreator class
                with the updated configuration.
        """
        args = locals()
        del args["self"]
        for k, v in args.items():
            if v is not None:
                setattr(self, k, v)

        return self

    def __repr__(self):
        return f"Hello, I'm a comparison level for '{self.sql_condition}'"


# Deserialise dictionaries
comp_level1 = ComparisonLevel.with_level_dict(level1)
comp_level2 = ComparisonLevel.with_level_dict(level2)
comp_level3 = ComparisonLevel.with_level_dict(level3)

print(comp_level1)
print(comp_level2)
print(comp_level3)

# Additional args constructed from depacking dict...
comp_level1.is_null_level
comp_level2.m_probability

# Construct directly with a ComparisonLevel and arg names...
# Allows a more user friendly building experience...
display(ComparisonLevel(sql_condition="my_col_l = my_col_r"))

ComparisonLevel(sql_condition="my_col_l = my_col_r").configure(
    m_probability=0.8,
    tf_adjustment_column="my_col"
)
