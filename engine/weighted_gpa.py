"""
Compute the WEIGHTED GPA per Faculty regulation for class-of-degree:
- Level I courses carry weight ZERO (excluded)
- Levels II and III only
- Uses PASSED courses (credit-earning attempts); failed attempts that were later
  passed are excluded (the passing attempt is what counts toward the award GPA).

The grade-point scale and the class-of-degree bands both come from
engine/settings.py -- edit that file to change them.
"""
from .settings import GRADE_POINTS as GP
from .settings import classify  # re-exported so existing imports keep working


def level_of(code):
    return code.split()[1][0]


def weighted_gpa_l23(student):
    """Passed-only, Levels II & III, by letter grade. Returns (gpa, credits)."""
    tot_qp = 0.0
    tot_cr = 0
    for c in student["courses"]:
        lv = level_of(c["code"])
        if lv not in ("2", "3"):
            continue
        if c["status"] != "passed":
            continue
        g = c["grade"]
        if g in GP:
            cr = c["credits_earned"] or c["credits_attempted"]
            tot_qp += GP[g] * cr
            tot_cr += cr
    return (tot_qp / tot_cr if tot_cr else 0.0), tot_cr
