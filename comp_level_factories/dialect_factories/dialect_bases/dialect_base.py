# defines default values for dialect-dependent properties
# used by comparisons and comparison levels
# individual dialects subclass this and overwrite relevant properties
# dialect-specific comparisons and comparison levels then inherit from
# the relevant subclass in splink/{dialect}/{dialect}_base.py


# Doesn't necessarily need to be an ABC
class DialectBase:
    @property
    def _sql_dialect(self):
        raise NotImplementedError("No SQL dialect specified")

    @property
    def _regex_extract_function(self):
        raise NotImplementedError(
            "Regex extract option not defined for " "the SQL backend being used.  "
        )

    @property
    def _damerau_levenshtein_name(self):
        raise NotImplementedError(
            "Demerau lev not available for given backend."
        )