"""
=============================================================================
  SETTINGS  --  edit this file to change GPA bands, credit floors, or the
                letter-grade -> grade-point scale.
=============================================================================

You can change these values without touching any engine code. Save the file
and restart the app; every report, the on-screen results, and the spreadsheet
will use the new values automatically.

-----------------------------------------------------------------------------
1. CLASS-OF-DEGREE GPA BANDS  (entry-year aware)
-----------------------------------------------------------------------------
Bands can differ by the student's YEAR OF ENTRY. Each rule below has:
  * "from_entry_year": the first entry year it applies to (e.g. "2026/2027").
                       Use None for "applies to the earliest cohorts".
  * "bands": the (minimum GPA, label) list for that era, highest to lowest.

The engine picks, for each student, the rule with the latest from_entry_year
that is <= the student's entry year. So a student is always classified on the
bands in force in their year of entry -- which is what the regulations require.

CURRENT RULE SET
  * Entry 2026/2027 and later : First Class Honours floor is 3.70
  * Entry 2025/2026 and earlier: First Class Honours floor is 3.60
    (the 3.60 floor stays with these cohorts as they graduate, through 2031/32)

TO ADD A FUTURE CHANGE
  Add another dict to GPA_BAND_RULES with the new "from_entry_year" and "bands".
  Keep the list ordered however you like; the engine sorts by entry year.

TO CHANGE A SINGLE THRESHOLD
  Edit the relevant "min" number in the relevant era's "bands".
"""

GPA_BAND_RULES = [
    {
        # Older cohorts: First Class at 3.60. Applies to everyone up to and
        # including entry year 2025/2026.
        "from_entry_year": None,            # earliest cohorts
        "label": "pre-2026/27 (First Class 3.60)",
        "bands": [
            {"min": 3.60, "label": "First Class Honours"},
            {"min": 3.00, "label": "Upper Second Class Honours"},
            {"min": 2.50, "label": "Lower Second Class Honours"},
            {"min": 2.00, "label": "Pass"},
        ],
    },
    {
        # New rule for students entering from August 1, 2026 (entry year
        # 2026/2027 onward): First Class floor rises to 3.70.
        "from_entry_year": "2026/2027",
        "label": "2026/27 onward (First Class 3.70)",
        "bands": [
            {"min": 3.70, "label": "First Class Honours"},
            {"min": 3.00, "label": "Upper Second Class Honours"},
            {"min": 2.50, "label": "Lower Second Class Honours"},
            {"min": 2.00, "label": "Pass"},
        ],
    },
]

# Label used when a GPA falls below the lowest band's minimum.
BELOW_LOWEST_LABEL = "Below Pass (review)"


# -----------------------------------------------------------------------------
# 2. CREDIT FLOORS (graduation minimums)
# -----------------------------------------------------------------------------
# Change these if the Faculty ever revises the credit requirements.
CREDIT_FLOORS = {
    "total": 90,      # minimum total credits
    "level1": 30,     # minimum Level I credits
    "level23": 60,    # minimum Levels II + III credits (combined)
}
CREDITS_PER_COURSE = 3   # used to estimate "courses outstanding" from a credit shortfall


# -----------------------------------------------------------------------------
# 3. LETTER-GRADE -> GRADE-POINT SCALE (for the weighted GPA)
# -----------------------------------------------------------------------------
# The points awarded per letter grade. Edit if the grading scale changes.
# Grades not listed here (P, EX, EC, IP, LW, etc.) do not enter the GPA.
GRADE_POINTS = {
    "A+": 4.3, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0,
}


# -----------------------------------------------------------------------------
# Helpers (used by the engine; you normally don't need to edit below here)
# -----------------------------------------------------------------------------
def _entry_year_key(entry_year):
    """Sortable key from an entry year like '2026/2027' -> 2026. None -> -1."""
    if not entry_year:
        return -1
    try:
        return int(str(entry_year).split("/")[0])
    except (ValueError, IndexError):
        return -1


def bands_for_entry_year(entry_year):
    """Return the (bands, era_label) in force for a given entry year."""
    student_key = _entry_year_key(entry_year)
    # rules sorted oldest-first; choose the latest whose from_entry_year <= student
    applicable = None
    for rule in sorted(GPA_BAND_RULES, key=lambda r: _entry_year_key(r["from_entry_year"])):
        rule_key = _entry_year_key(rule["from_entry_year"])
        if rule_key <= student_key:
            applicable = rule
    if applicable is None:
        # student entry earlier than every rule's start; use the earliest rule
        applicable = min(GPA_BAND_RULES, key=lambda r: _entry_year_key(r["from_entry_year"]))
    return applicable["bands"], applicable.get("label", "")


def classify(gpa, entry_year=None):
    """
    Return the class-of-degree label for a GPA, using the bands in force for the
    student's entry year. entry_year may be omitted (uses the earliest/base bands)
    for callers that don't have it.
    """
    if gpa is None:
        return "—"
    bands, _ = bands_for_entry_year(entry_year)
    for band in bands:
        if gpa >= band["min"]:
            return band["label"]
    return BELOW_LOWEST_LABEL


def bands_description(entry_year=None, dash="-"):
    """
    Human-readable description of the bands in force for an entry year, e.g.
    'First Class Honours >=3.70; Upper Second... 3.00-3.69; ... Pass 2.00-2.49'.
    """
    bands, _ = bands_for_entry_year(entry_year)
    parts = []
    for i, band in enumerate(bands):
        lo = band["min"]
        if i == 0:
            parts.append(f"{band['label']} >={lo:.2f}")
        else:
            upper = bands[i - 1]["min"] - 0.01
            parts.append(f"{band['label']} {lo:.2f}{dash}{upper:.2f}")
    return "; ".join(parts)


def all_band_eras():
    """List of (label, description) for every era, for report footnotes."""
    out = []
    for rule in sorted(GPA_BAND_RULES, key=lambda r: _entry_year_key(r["from_entry_year"])):
        # build a description from this rule's own bands
        bands = rule["bands"]
        parts = []
        for i, band in enumerate(bands):
            lo = band["min"]
            if i == 0:
                parts.append(f"{band['label']} >={lo:.2f}")
            else:
                upper = bands[i - 1]["min"] - 0.01
                parts.append(f"{band['label']} {lo:.2f}-{upper:.2f}")
        out.append((rule.get("label", ""), "; ".join(parts)))
    return out
