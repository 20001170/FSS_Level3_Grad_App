"""
=============================================================================
  DEPARTMENT MAP  --  edit here to change which department a programme sits in
=============================================================================

Maps each BOE programme label to one of the four departments/areas:
  "School of Business", "Economics", "GSSP", "BSc Social Sciences"

GSSP = Government, Sociology, Social Work & Psychology.

Any programme not listed falls back to DEFAULT_DEPARTMENT and is flagged so it
can be added here.
"""

DEFAULT_DEPARTMENT = "Unassigned (add to department_map.py)"

PROGRAMME_DEPARTMENT = {
    # ---- School of Business ----
    "Accounting & Finance": "School of Business",
    "Accounting (Special)": "School of Business",
    "Banking & Finance": "School of Business",
    "Aviation Mgmt w Pilot L": "School of Business",
    "Hospitality & Tour Mgmt": "School of Business",
    "International Tourism Mgmt": "School of Business",
    "Intl Tour Mgmt with Span": "School of Business",
    "Major in Management": "School of Business",
    "Management": "School of Business",
    "Management Studies": "School of Business",
    "Management with Chinese": "School of Business",
    "Management with Psychology": "School of Business",
    "Mgmt & Discipline": "School of Business",
    "Mgmt Innovation Entrep": "School of Business",
    "Mgmt Studies (Double)": "School of Business",
    "Mgmt Studies (Special)": "School of Business",
    "Mgmt with Spanish": "School of Business",
    "Intl Bus with Chinese": "School of Business",
    "Intl Bus with French": "School of Business",
    "Intl Bus with Spanish": "School of Business",

    # ---- Economics ----
    "Economics": "Economics",
    "Econ & Accounting": "Economics",
    "Economics & Finance": "Economics",
    "Economics & Law": "Economics",
    "Economics & Management": "Economics",
    "Economics & Mathematics": "Economics",
    "Economics with Acct": "Economics",
    "Economics with Law": "Economics",
    "Economics with Management": "Economics",
    "Economics with Maths": "Economics",

    # ---- GSSP (Government, Sociology, Social Work & Psychology) ----
    "International Rel (Spec)": "GSSP",
    "International Relations": "GSSP",
    "Pol Sci & Psych": "GSSP",
    "Pol Sci with Sociology": "GSSP",
    "Political Sci & Philosophy": "GSSP",
    "Political Sci (Special)": "GSSP",
    "Political Sci with Law": "GSSP",
    "Political Science": "GSSP",
    "Political Science & Law (CH)": "GSSP",
    "Psychology (Special)": "GSSP",
    "Psychology with Mgmt": "GSSP",
    "Psychology wth Sociology": "GSSP",
    "Public Policy & Mgmt": "GSSP",
    "Labour & Employ Relations": "GSSP",
    "Social Work (Special)": "GSSP",
    "Soci with Criminology": "GSSP",
    "Soci with Cult Studs": "GSSP",
    "Soci with Gend & Dev Stu": "GSSP",
    "Sociology & Law": "GSSP",
    "Sociology & Pol Science": "GSSP",
    "Sociology & Psych": "GSSP",
    "Sociology (Special)": "GSSP",
    "Sociology with History": "GSSP",
    "Sociology with Law": "GSSP",
    "Sociology with Pol Sci": "GSSP",
    "Sociology with Psych": "GSSP",

    # ---- BSc Social Sciences (general) ----
    "Social Sciences": "BSc Social Sciences",
    "Specially Admitted SS": "BSc Social Sciences",
}

# Display order for departments in reports
DEPARTMENT_ORDER = ["School of Business", "Economics", "GSSP", "BSc Social Sciences"]


def department_of(programme):
    return PROGRAMME_DEPARTMENT.get(programme, DEFAULT_DEPARTMENT)
