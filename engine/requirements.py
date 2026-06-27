"""
Thin adapter between the eligibility engine and the editable programme registry
(engine/programmes.py). To add or change a programme/year, edit programmes.py,
NOT this file.
"""
from .programmes import lookup


def get_requirements(programme, entry_year):
    """
    Returns one of:
      * a dict with a named rule set (level1_fixed, level1_either_or,
        level23_named, era, notes);
      * a dict {"type":"minors", ...} for a minors-based programme;
      * the string "CREDIT_ONLY" for a credit-floors-only programme;
      * None for an unknown programme (no rule set encoded yet).
    """
    res = lookup(programme, entry_year)
    if res == "CREDIT_ONLY":
        return "CREDIT_ONLY"
    if res is None:
        return None
    return res
