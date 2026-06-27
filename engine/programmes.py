"""
=============================================================================
  PROGRAMME REGISTRY  --  this is the file you edit to add programmes / years
=============================================================================

You do NOT need to touch the engine to add a new programme or a new handbook
era. Add an entry to PROGRAMME_RULES below following the template, and the app
will pick it up automatically.

------------------------------------------------------------------------------
HOW MATCHING WORKS
------------------------------------------------------------------------------
For each student the engine reads two things from the BOE record:
  * programme  -- the label exactly as printed on the BOE (e.g. "Mgmt Studies
                  (Special)", "Psychology (Special)", "Political Science & Law (CH)")
  * entry_year -- e.g. "2021/2022"

It then looks up PROGRAMME_RULES[programme]. That entry is a list of "eras",
each with a `years` set (the entry years it applies to) and the named-course
requirements for that era. The engine picks the era whose `years` contains the
student's entry_year. If a programme has only one era for all years, use
years="ALL".

------------------------------------------------------------------------------
TEMPLATE  --  copy this block, fill it in, paste into PROGRAMME_RULES
------------------------------------------------------------------------------
    "BOE Programme Label Exactly": [
        {
            "era": "short_name_for_this_era",           # any label you like
            "years": {"2022/2023", "2023/2024"},        # or "ALL"
            "level1_fixed": {                            # codes that MUST be passed
                "DEPT 1001", "DEPT 1002",
            },
            "level1_either_or": [                        # each inner set = "one of"
                {"FOUN 1008", "FOUN 1006"},
            ],
            "level23_named": {                           # Level II/III named courses
                "DEPT 2001", "DEPT 3001",
            },
            "notes": "Free-text note shown in the output for this programme/era.",
        },
        # ... more eras for the same programme ...
    ],

Codes are always "DEPT NNNN" with a single space. "Passing" a course, an
exemption with credit (EC), or an exemption (EX) all count as satisfying a
named requirement.
=============================================================================
"""

# ---------------------------------------------------------------------------
# Shared building blocks (re-used across several programmes). Edit freely.
# ---------------------------------------------------------------------------

# ---- Management (Special/Double) -------------------------------------------
MGMT_L1_FIXED = {"ECON 1001", "ECON 1005", "MGMT 1001", "ACCT 1002", "ACCT 1003"}
MGMT_L1_EITHER = [
    {"ECON 1003", "ECON 1004"},
    {"FOUN 1008", "FOUN 1006"},
]
# Options-era (entry 2017/18-2021/22): full FIXED Level II/III named list.
MGMT_OPTIONS_ERA_L23 = {
    "MGMT 2005", "MGMT 2008", "MGMT 2020", "MGMT 3024", "MKTG 2001",
    "MGMT 2006", "MGMT 2013", "MGMT 2021", "MGMT 2023", "MGMT 3017",
    "MGMT 3033", "MGMT 2026", "MGMT 3031",
}
# Fixed-9 era (entry 2022/23 onward, verified stable through 2025/26).
MGMT_FIXED9_ERA_L23 = {
    "MGMT 2006", "MGMT 2008", "MGMT 2012", "MGMT 2013", "MGMT 2021",
    "MGMT 2023", "MGMT 2026", "MGMT 3017", "MGMT 3031", "MKTG 2001",
}

# ---- Psychology (Special) --------------------------------------------------
PSYC_L1 = {"PSYC 1003", "PSYC 1004", "PSYC 1013", "PSYC 1012", "PSYC 1015",
           "MGMT 1000", "SOCI 1005"}
PSYC_L1_EITHER = [{"FOUN 1008", "FOUN 1006"}]
PSYC_L23 = {"PSYC 2022", "PSYC 2008", "PSYC 2009", "PSYC 2004", "PSYC 2003",
            "PSYC 2014", "PSYC 2002", "PSYC 2007", "PSYC 3024", "PSYC 3013",
            "PSYC 3014", "PSYC 3021"}

# ---- Political Science cores ----------------------------------------------
POLSCI_CORE_L23 = {"GOVT 2010", "GOVT 2014", "GOVT 2015", "GOVT 2016",
                   "GOVT 2024", "GOVT 2057", "GOVT 3015", "GOVT 3017",
                   "GOVT 3018", "SOCI 2006"}
POLSCI_SPECIAL_L1 = {"GOVT 1000", "GOVT 1011", "ECON 1002", "SOCI 1000",
                     "SOCI 1001", "SOCI 1005", "MGMT 1000"}
POLSCI_L1_EITHER = [{"FOUN 1008", "FOUN 1006"}, {"FOUN 1101", "FOUN 1201"}]

POLSCI_AND_LAW_L1 = {"GOVT 1000", "GOVT 1011", "LAW 1010", "LAW 1110",
                     "LAW 1020", "LAW 1231", "LAW 1232", "MGMT 1000", "SOCI 1005"}
POLSCI_AND_LAW_L1_EITHER = [{"FOUN 1008", "FOUN 1006"}, {"FOUN 1101", "FOUN 1201"},
                            {"SOCI 1001", "HIST 1004"}]
POLSCI_WITH_LAW_L1 = {"GOVT 1000", "GOVT 1011", "LAW 1010", "LAW 1020", "LAW 1110",
                      "LAW 1231", "LAW 1232", "MGMT 1000", "SOCI 1001", "SOCI 1005"}
POLSCI_AND_PHIL_L1 = {"GOVT 1000", "GOVT 1011", "MGMT 1000", "PHIL 1002",
                      "PHIL 1003", "PHIL 1300", "SOCI 1001", "SOCI 1005"}
POLSCI_AND_PSYC_L1 = {"GOVT 1000", "GOVT 1011", "MGMT 1000", "PSYC 1003",
                      "PSYC 1004", "SOCI 1001", "SOCI 1005"}
POLSCI_AND_PSYC_L23 = POLSCI_CORE_L23 | {"SOCI 2007", "PSYC 2002", "PSYC 2003",
                                         "PSYC 2009", "PSYC 2012", "PSYC 3021"}

OPTIONS_ERA_YEARS = {"2017/2018", "2018/2019", "2019/2020", "2020/2021", "2021/2022"}
FIXED9_ERA_YEARS = {"2022/2023", "2023/2024", "2024/2025", "2025/2026"}

# ---- Sociology family (Special + joint majors) -----------------------------
# Shared Sociology core: theory (2000 OR 2001), methods (2006 OR 2007), and
# Caribbean Social Problems (3035). Joint majors add the partner-discipline core.
SOCI_CORE_EITHER = [
    {"SOCI 2000", "SOCI 2001"},   # Classical OR Modern Social Theory
    {"SOCI 2006", "SOCI 2007"},   # Qualitative OR Survey methods
]
SOCI_CORE_FIXED = {"SOCI 3035"}   # Caribbean Social Problems

SOCI_SPECIAL_L1 = {"SOCI 1000", "SOCI 1002", "MGMT 1000"}
SOCI_L1_EITHER = [{"FOUN 1008", "FOUN 1006"}]

# ---- Economics (Major/Special) ---------------------------------------------
ECON_CORE = {
    "ECON 2000", "ECON 2001", "ECON 2002", "ECON 2003",
    "ECON 2025", "ECON 2026", "ECON 2029",
}
ECON_L1 = {"ECON 1001", "ECON 1002", "ECON 1005", "MGMT 1000"}
ECON_L1_EITHER = [{"ECON 1003", "ECON 1004"}, {"FOUN 1008", "FOUN 1006"}]

# ---- Econ & Accounting (joint) ---------------------------------------------
ECON_ACCT_L23 = {
    "ECON 2000", "ECON 2001", "ECON 2002", "ECON 2003",
    "ACCT 2014", "ACCT 2015", "ACCT 2017",
}

# ---- Management Innovation & Entrepreneurship ------------------------------
MGMT_INNOV_L23 = {
    "MGMT 2005", "MGMT 2006", "MGMT 2008", "MGMT 2012", "MGMT 2021",
    "MGMT 2026", "MGMT 3017", "MGMT 3031", "MKTG 2001",
}

# ---- Public Policy & Management --------------------------------------------
PUB_POL_L23 = {
    "GOVT 2057", "GOVT 3017", "MGMT 2008", "MGMT 3017", "MGMT 3031", "MGMT 3033",
}

# ---- International Relations (and Special) ----------------------------------
# GOVT-heavy international politics core (verified across the cohort).
INTL_REL_L1 = {"INRL 1000", "GOVT 1000", "GOVT 1011", "MGMT 1000"}
INTL_REL_L1_EITHER = [{"FOUN 1008", "FOUN 1006"}, {"FOUN 1101", "FOUN 1201"}]
INTL_REL_L23 = {
    "GOVT 2014", "GOVT 2047", "GOVT 3014", "GOVT 3015", "GOVT 3025", "GOVT 3049",
    "SOCI 2006", "SOCI 2007",
}

# ---- International Tourism Management --------------------------------------
INTL_TOUR_L1 = {"MGMT 1000", "MGMT 1001", "ECON 1001"}
INTL_TOUR_L1_EITHER = [{"FOUN 1008", "FOUN 1006"}]
INTL_TOUR_L23 = {
    "MGMT 2008", "MGMT 3017", "MGMT 3024", "MGMT 3031",
    "TOUR 2000", "TOUR 2002", "TOUR 3000",
}

# ---- Banking & Finance ----------------------------------------------------
BANK_FIN_L1 = {"ECON 1001", "ECON 1002", "ECON 1005", "MGMT 1000", "FINA 1001"}
BANK_FIN_L1_EITHER = [{"ECON 1003", "ECON 1004"}, {"FOUN 1008", "FOUN 1006"}]
BANK_FIN_L23 = {
    "ECON 2000", "ECON 2002", "FINA 2001", "FINA 2003", "FINA 2004", "FINA 2005",
    "MGMT 2023", "MGMT 3048", "MGMT 3049",
}

# ---- Psychology with Management -------------------------------------------
PSYC_MGMT_L1 = {"PSYC 1003", "PSYC 1004", "MGMT 1000", "MGMT 1001"}
PSYC_MGMT_L1_EITHER = [{"FOUN 1008", "FOUN 1006"}]
PSYC_MGMT_L23 = {
    "MGMT 2006", "MGMT 2008", "MGMT 3017",
    "PSYC 2002", "PSYC 2012", "PSYC 3014", "PSYC 3024",
    "SOCI 2006", "SOCI 2007",
}

# ---- Economics & Management -----------------------------------------------
ECON_MGMT_L1 = {"ECON 1001", "ECON 1002", "ECON 1004", "ECON 1005", "MGMT 1000", "MGMT 1001"}
ECON_MGMT_L1_EITHER = [{"FOUN 1008", "FOUN 1006"}]
ECON_MGMT_L23 = {
    "ECON 2000", "ECON 2001", "ECON 2002", "ECON 2003",
    "MGMT 2006", "MGMT 2008", "MGMT 2023", "MGMT 2026", "MGMT 3017", "MKTG 2001",
}

# ---- Social Work (Special) -------------------------------------------------
SOWK_L1 = {
    "SOWK 1001", "SOWK 1002", "SOWK 1000", "PSYC 1003",
}
SOWK_L1_EITHER = [
    {"FOUN 1008", "FOUN 1006"},
]
SOWK_L23 = {
    "SOWK 2000", "SOWK 2010", "SOWK 3009",
    "PSYC 2012", "PSYC 2002",
    "SOCI 2006", "SOCI 2007", "SOCI 3012", "SOCI 3013", "SOCI 3035",
    "SOWK 3004", "SOWK 3005", "SOWK 3006",
    # NOTE: SOWK 3008/3000 and the "any two approved" slots are examiner-confirmed.
}

# ---- B.Sc. Social Sciences (general) — minors-based ------------------------
# Students complete THREE minors (5 courses each) + 5 free electives. Each minor
# below lists its named/fixed Level II/III courses; minors also have an "any
# Level II/III course in X" slot which can't be verified by a fixed code, so a
# minor is counted as satisfied when its fixed named courses are all present.
# The engine requires at least THREE satisfied minors (plus the credit floors).
SOC_SCI_MINORS = {
    "Accounting":          {"ACCT 2014", "ACCT 2015", "ACCT 2017", "ACCT 3043"},
    "Criminology":         {"SOCI 3032", "SOCI 3017", "SOCI 3047", "SOCI 3036"},
    "Cultural Studies":    {"CLTR 2500", "CLTR 3100"},
    "Economics":           {"ECON 2000", "ECON 2001", "ECON 2002", "ECON 2003"},
    "Gender & Development": {"GEND 1103"},
    "International Relations": {"GOVT 3015", "GOVT 3049", "GOVT 3025", "GOVT 2047"},
    "Management":          {"MKTG 2001", "MGMT 2006", "MGMT 2008", "MGMT 3017", "MGMT 2023"},
    "Political Science":   {"GOVT 3017", "GOVT 3018", "GOVT 2014", "GOVT 2015"},
    "Psychology":          {"PSYC 2009", "PSYC 3050", "PSYC 2012", "PSYC 2002"},
    "Sociology":           {"SOCI 3035", "SOCI 3026"},
}
SOC_SCI_MIN_MINORS = 3  # must satisfy at least this many minors

# ---- Management (single Major, with concentrations) ------------------------
# The B.Sc. Management major (BOE label "Management") has concentrations
# (Marketing, Finance, HR, International Business, Project Mgmt, etc.). All
# concentrations share a common Level II/III Management core; the concentration
# courses + elective slots vary and are examiner-confirmed. MGMT 2013 is
# deliberately excluded from the required core (evidence from the cohort shows it
# is missing for the majority of otherwise-complete students, i.e. not universal).
MGMT_MAJOR_L1 = {
    "ECON 1001", "ECON 1005", "ACCT 1002", "MGMT 1000", "MGMT 1001",
}
MGMT_MAJOR_L1_EITHER = [
    {"ECON 1003", "ECON 1004"},
    {"FOUN 1008", "FOUN 1006"},
]
MGMT_MAJOR_L23 = {
    "MGMT 2006", "MGMT 2008", "MGMT 2012", "MGMT 2021", "MGMT 2023",
    "MGMT 2026", "MGMT 3017", "MGMT 3031", "MKTG 2001",
}

# ---- Accounting (Special) --------------------------------------------------
ACCT_SPEC_L1 = {
    "ACCT 1002", "ACCT 1003", "ECON 1001", "ECON 1005",
    "MGMT 1000", "MGMT 1001",
}
ACCT_SPEC_L1_EITHER = [
    {"ECON 1003", "ECON 1004"},
    {"FOUN 1008", "FOUN 1006"},
    {"FOUN 1101", "FOUN 1201"},
]
ACCT_SPEC_L23 = {
    # Level II core (universal)
    "ACCT 2014", "ACCT 2015", "ACCT 2017",
    "MGMT 2006", "MGMT 2008", "MGMT 2021", "MGMT 2023", "MKTG 2001",
    # Level III core (universal)
    "ACCT 3041", "ACCT 3043", "MGMT 3024", "MGMT 3033", "MGMT 3031",
    # NOTE: ACCT 3039/3044, MGMT 3096 (Taxation) and MGMT 2012 appear to belong to
    # the professional-accounting (ACCA) track / selection pools rather than being
    # universally required, so they are left to examiner confirmation. The "Approved
    # Level II/III elective" slots are likewise examiner-confirmed.
}

# ---- Economics & Finance ---------------------------------------------------
ECON_FIN_L1 = {
    "ECON 1001", "ECON 1002", "ECON 1004", "ECON 1005",
    "MGMT 1000", "MGMT 1001", "FINA 1001",
}
ECON_FIN_L1_EITHER = [
    {"FOUN 1008", "FOUN 1006"},
]
ECON_FIN_L23 = {
    # Economics core (mandatory across the programme)
    "ECON 2000", "ECON 2001", "ECON 2002", "ECON 2003",
    "ECON 2025", "ECON 2026", "ECON 2029",
    # Finance core
    "FINA 2001", "MGMT 2023",
    # NOTE: the FINA 2003/2004/2005, ACCT 2019, ECON 3007/3008/3010/3049/3075
    # items plus the approved-elective slots appear to be selection pools, so
    # they are left to examiner confirmation rather than hard-required.
}

# ---- Accounting & Finance --------------------------------------------------
ACCT_FIN_L1 = {
    "ECON 1001", "ECON 1005", "ACCT 1002", "ACCT 1003",
    "MGMT 1000", "MGMT 1001", "FINA 1001",
}
ACCT_FIN_L1_EITHER = [
    {"ECON 1003", "ECON 1004"},
    {"FOUN 1008", "FOUN 1006"},
]
ACCT_FIN_L23 = {
    # Management core (mandatory)
    "MGMT 2006", "MGMT 2008", "MGMT 2012", "MGMT 2021", "MGMT 3031", "MKTG 2001",
    # Accounting core (mandatory)
    "ACCT 2014", "ACCT 2015", "ACCT 2017", "ACCT 3040", "ACCT 3041", "ACCT 3043",
    # Financial Management I is required across the business programmes
    "MGMT 2023",
    # NOTE: the wider Finance menu (FINA 2001, MGMT 3048/3049/3053/3076) and the
    # remaining Management-core items appear to be a selection pool rather than all
    # mandatory, so they are left to examiner confirmation rather than hard-required.
}


# ---------------------------------------------------------------------------
# THE REGISTRY  --  add / edit programmes here
# ---------------------------------------------------------------------------
PROGRAMME_RULES = {
    "Sociology (Special)": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": SOCI_SPECIAL_L1, "level1_either_or": SOCI_L1_EITHER,
         "level23_named": SOCI_CORE_FIXED, "level23_either_or": SOCI_CORE_EITHER,
         "notes": "BSc Sociology (Special): theory + methods + Caribbean Social Problems core; the programme is elective-heavy, so the remaining slots are examiner-confirmed."},
    ],
    "Soci with Criminology": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": SOCI_SPECIAL_L1, "level1_either_or": SOCI_L1_EITHER,
         "level23_named": SOCI_CORE_FIXED | {"SOCI 3032", "SOCI 3017"},
         "level23_either_or": SOCI_CORE_EITHER,
         "notes": "Sociology with Criminology: Sociology core + criminology courses; elective slots examiner-confirmed."},
    ],
    "Sociology with Law": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": SOCI_SPECIAL_L1, "level1_either_or": SOCI_L1_EITHER,
         "level23_named": SOCI_CORE_FIXED, "level23_either_or": SOCI_CORE_EITHER,
         "notes": "Sociology with Law: Sociology core + approved Law courses (count, examiner-confirmed)."},
    ],
    "Sociology & Law": "ALIAS:Sociology with Law",
    "Sociology & Psych": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": SOCI_SPECIAL_L1, "level1_either_or": SOCI_L1_EITHER,
         "level23_named": SOCI_CORE_FIXED | {"PSYC 2002", "PSYC 2012"},
         "level23_either_or": SOCI_CORE_EITHER,
         "notes": "Sociology & Psychology (joint): Sociology core + Psychology courses; electives examiner-confirmed."},
    ],
    "Psychology wth Sociology": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": {"PSYC 1003", "PSYC 1004", "SOCI 1002", "MGMT 1000"},
         "level1_either_or": SOCI_L1_EITHER,
         "level23_named": {"PSYC 2002", "PSYC 2012", "PSYC 3024", "SOCI 2006", "SOCI 2007"},
         "notes": "Psychology with Sociology: Psychology core + Sociology methods; electives examiner-confirmed."},
    ],
    "Economics": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": ECON_L1, "level1_either_or": ECON_L1_EITHER,
         "level23_named": ECON_CORE,
         "notes": "BSc Economics (Major): intermediate micro/macro + statistics/research core; electives examiner-confirmed."},
    ],
    "Econ & Accounting": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": {"ECON 1001", "ECON 1005", "ACCT 1002", "ACCT 1003", "MGMT 1000"},
         "level1_either_or": ECON_L1_EITHER,
         "level23_named": ECON_ACCT_L23,
         "notes": "Economics & Accounting (joint): Economics core + Accounting core; electives examiner-confirmed."},
    ],
    "Mgmt Innovation Entrep": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": MGMT_MAJOR_L1, "level1_either_or": MGMT_MAJOR_L1_EITHER,
         "level23_named": MGMT_INNOV_L23,
         "notes": "Management, Innovation & Entrepreneurship: Management core; innovation/entrepreneurship electives examiner-confirmed."},
    ],
    "Public Policy & Mgmt": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": {"GOVT 1000", "GOVT 1011", "MGMT 1000", "MGMT 1001"},
         "level1_either_or": [{"FOUN 1008", "FOUN 1006"}],
         "level23_named": PUB_POL_L23,
         "notes": "Public Policy & Management: GOVT/MGMT core; electives examiner-confirmed."},
    ],
    "International Relations": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": INTL_REL_L1, "level1_either_or": INTL_REL_L1_EITHER,
         "level23_named": INTL_REL_L23,
         "notes": "International Relations: GOVT international-politics core; elective slots examiner-confirmed."},
    ],
    "International Rel (Spec)": "ALIAS:International Relations",
    "International Tourism Mgmt": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": INTL_TOUR_L1, "level1_either_or": INTL_TOUR_L1_EITHER,
         "level23_named": INTL_TOUR_L23,
         "notes": "International Tourism Management: TOUR/MGMT core; elective/abroad slots examiner-confirmed."},
    ],
    "Banking & Finance": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": BANK_FIN_L1, "level1_either_or": BANK_FIN_L1_EITHER,
         "level23_named": BANK_FIN_L23,
         "notes": "Banking & Finance: ECON/FINA/MGMT core; FINA menu and electives examiner-confirmed."},
    ],
    "Psychology with Mgmt": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": PSYC_MGMT_L1, "level1_either_or": PSYC_MGMT_L1_EITHER,
         "level23_named": PSYC_MGMT_L23,
         "notes": "Psychology with Management: PSYC + MGMT core; elective slots examiner-confirmed."},
    ],
    "Management with Psychology": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": {"MGMT 1000", "MGMT 1001", "PSYC 1003", "PSYC 1004"},
         "level1_either_or": [{"FOUN 1008", "FOUN 1006"}],
         "level23_named": {"MGMT 2006", "MGMT 2008", "MGMT 3017",
                           "PSYC 2002", "PSYC 2012"},
         "notes": "Management with Psychology (major/minor): MGMT core + PSYC minor courses; electives examiner-confirmed."},
    ],
    "Economics & Management": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": ECON_MGMT_L1, "level1_either_or": ECON_MGMT_L1_EITHER,
         "level23_named": ECON_MGMT_L23,
         "notes": "Economics & Management (joint): ECON + MGMT core; elective slots examiner-confirmed."},
    ],
    "Economics with Management": "ALIAS:Economics & Management",
    "Social Work (Special)": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": SOWK_L1, "level1_either_or": SOWK_L1_EITHER,
         "level23_named": SOWK_L23,
         "notes": ("BSc Social Work (Special): SOWK/PSYC/SOCI core + field instruction. "
                   "Field-integrative and approved-elective slots are examiner-confirmed.")},
    ],
    "Management": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": MGMT_MAJOR_L1, "level1_either_or": MGMT_MAJOR_L1_EITHER,
         "level23_named": MGMT_MAJOR_L23,
         "notes": ("BSc Management (Major): shared Level II/III Management core. The "
                   "concentration courses (Marketing, Finance, HR, etc.) and elective "
                   "slots are examiner-confirmed; MGMT 2013 is not treated as universally "
                   "required.")},
    ],
    "Major in Management": "ALIAS:Management",
    "Management Studies": "ALIAS:Management",
    "Accounting (Special)": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": ACCT_SPEC_L1, "level1_either_or": ACCT_SPEC_L1_EITHER,
         "level23_named": ACCT_SPEC_L23,
         "notes": ("BSc Accounting (Special): Level I core + Level II/III Accounting/Management "
                   "core. Approved-elective slots are examiner-confirmed.")},
    ],
    "Economics & Finance": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": ECON_FIN_L1, "level1_either_or": ECON_FIN_L1_EITHER,
         "level23_named": ECON_FIN_L23,
         "notes": ("BSc Economics and Finance: Level I core + Economics/Finance L2/3 core. "
                   "The FINA/ACCT/ECON-3xxx menus and elective slots are examiner-confirmed.")},
    ],
    "Accounting & Finance": [
        {"era": "stable", "years": "ALL",
         "level1_fixed": ACCT_FIN_L1, "level1_either_or": ACCT_FIN_L1_EITHER,
         "level23_named": ACCT_FIN_L23,
         "notes": ("BSc Accounting and Finance: Level I core + Management/Accounting L2/3 core. "
                   "The wider Finance menu and elective slots are examiner-confirmed (selection "
                   "pools, not all mandatory).")},
    ],
    "Mgmt Studies (Special)": [
        {"era": "options_era", "years": OPTIONS_ERA_YEARS,
         "level1_fixed": MGMT_L1_FIXED, "level1_either_or": MGMT_L1_EITHER,
         "level23_named": MGMT_OPTIONS_ERA_L23,
         "notes": ("Options-era structure (entry <=2021/22): fixed Level II/III named "
                   "courses checked here; the Level III 'Management Options' menu and "
                   "elective slots are examiner-confirmed.")},
        {"era": "fixed9_era", "years": FIXED9_ERA_YEARS,
         "level1_fixed": MGMT_L1_FIXED, "level1_either_or": MGMT_L1_EITHER,
         "level23_named": MGMT_FIXED9_ERA_L23,
         "notes": ("Fixed-9 structure (entry >=2022/23, stable through 2025/26): 9 named "
                   "Management/Marketing L2/3 courses + a 30-credit-Management / "
                   "30-credit-elsewhere split for the remaining L2/3 credits (split is "
                   "examiner-confirmed).")},
    ],
    "Mgmt Studies (Double)": "ALIAS:Mgmt Studies (Special)",

    "Psychology (Special)": [
        {"era": "stable_all_years", "years": "ALL",
         "level1_fixed": PSYC_L1, "level1_either_or": PSYC_L1_EITHER,
         "level23_named": PSYC_L23,
         "notes": ("Course-CODE list stable across all handbook years (titles changed, "
                   "codes did not). Elective slots not checked here.")},
    ],

    "Political Sci (Special)": [
        {"era": "stable_all_years", "years": "ALL",
         "level1_fixed": POLSCI_SPECIAL_L1, "level1_either_or": POLSCI_L1_EITHER,
         "level23_named": POLSCI_CORE_L23,
         "notes": "Political Science (Special): GOVT/SOCI core; elective slots examiner-confirmed."},
    ],
    "Political Science & Law (CH)": [
        {"era": "polsci_law", "years": "ALL",
         "level1_fixed": POLSCI_AND_LAW_L1, "level1_either_or": POLSCI_AND_LAW_L1_EITHER,
         "level23_named": POLSCI_CORE_L23,
         "notes": ("Political Science and Law (joint): named LAW Level I block + GOVT/SOCI "
                   "core; 10 approved Law L2/3 electives examiner-confirmed (count, not code).")},
    ],
    "Political Sci with Law": [
        {"era": "polsci_with_law", "years": "ALL",
         "level1_fixed": POLSCI_WITH_LAW_L1, "level1_either_or": POLSCI_L1_EITHER,
         "level23_named": POLSCI_CORE_L23,
         "notes": "Political Science with Law (major/minor): named LAW L1 block + GOVT/SOCI core."},
    ],
    "Political Sci & Philosophy": [
        {"era": "polsci_phil", "years": "ALL",
         "level1_fixed": POLSCI_AND_PHIL_L1, "level1_either_or": POLSCI_L1_EITHER,
         "level23_named": POLSCI_CORE_L23,
         "notes": "Political Science and Philosophy (joint): GOVT/PHIL L1 block + GOVT/SOCI core."},
    ],
    "Pol Sci & Psych": [
        {"era": "polsci_psyc", "years": "ALL",
         "level1_fixed": POLSCI_AND_PSYC_L1, "level1_either_or": POLSCI_L1_EITHER,
         "level23_named": POLSCI_AND_PSYC_L23,
         "notes": "Political Science and Psychology (joint): GOVT/PSYC L1 block + GOVT/SOCI/PSYC core."},
    ],
    # --- Small joint/variant programmes: share a parent departmental core ---
    "Sociology with Pol Sci": "ALIAS:Sociology (Special)",
    "Sociology & Pol Science": "ALIAS:Sociology (Special)",
    "Sociology with Psych": "ALIAS:Sociology & Psych",
    "Sociology with History": "ALIAS:Sociology (Special)",
    "Soci with Cult Studs": "ALIAS:Sociology (Special)",
    "Soci with Gend & Dev Stu": "ALIAS:Sociology (Special)",
    "Economics with Maths": "ALIAS:Economics",
    "Economics & Mathematics": "ALIAS:Economics",
    "Economics with Acct": "ALIAS:Econ & Accounting",
    "Economics with Law": "ALIAS:Economics",
    "Economics & Law": "ALIAS:Economics",

    # --- B.Sc. Social Sciences: minors-based named check --------------------
    # Flexible degree: 3 minors of 5 courses each + 5 electives. Checked by
    # counting satisfied minors (see SOC_SCI_MINORS) against the credit floors.
    "Social Sciences": "MINORS",
    # --- Programmes screened on CREDIT FLOORS ONLY --------------------------
    # Small, specialised, or structurally idiosyncratic programmes (often with
    # off-campus / professional / language components) for which a fixed named-
    # course list cannot be reliably derived. Screened on the 90/30/60 credit
    # floors and clearly flagged for examiner named-course confirmation, so no
    # student is silently passed OR wrongly failed.
    "Hospitality & Tour Mgmt": "CREDIT_ONLY",
    "Labour & Employ Relations": "CREDIT_ONLY",
    "Specially Admitted SS": "CREDIT_ONLY",
    "Aviation Mgmt w Pilot L": "CREDIT_ONLY",
    "Mgmt & Discipline": "CREDIT_ONLY",
    "Intl Bus with Chinese": "CREDIT_ONLY",
    "Intl Bus with French": "CREDIT_ONLY",
    "Intl Bus with Spanish": "CREDIT_ONLY",
    "Intl Tour Mgmt with Span": "CREDIT_ONLY",
    "Management with Chinese": "CREDIT_ONLY",
    "Mgmt with Spanish": "CREDIT_ONLY",
    "Pol Sci with Sociology": "CREDIT_ONLY",
    "Political Science": "CREDIT_ONLY",
}


def _year_key(y):
    """'2026/2027' -> 2026 for comparison. Returns None if unparseable."""
    try:
        return int(str(y).split("/")[0])
    except (ValueError, AttributeError, IndexError):
        return None


def _era_matches(years_spec, entry_year):
    """
    True if entry_year falls in an era's `years` specification. Supports:
      "ALL"                      -> always
      a set/list of years        -> membership, e.g. {"2022/2023","2023/2024"}
      "<=2026/2027" / ">=2027/2028" / "<2027/2028" / ">2026/2027"
      "2022/2023"                -> exactly that year
    """
    if years_spec == "ALL":
        return True
    if isinstance(years_spec, (set, list, tuple)):
        return entry_year in years_spec
    if isinstance(years_spec, str):
        ek = _year_key(entry_year)
        s = years_spec.strip()
        for op in ("<=", ">=", "<", ">"):
            if s.startswith(op):
                bound = _year_key(s[len(op):].strip())
                if ek is None or bound is None:
                    return False
                if op == "<=":
                    return ek <= bound
                if op == ">=":
                    return ek >= bound
                if op == "<":
                    return ek < bound
                if op == ">":
                    return ek > bound
        # plain single year string
        return entry_year == s
    return False


def lookup(programme, entry_year):
    """
    Return the requirement dict for (programme, entry_year), or one of the
    sentinels:  None  (programme unknown -> credit-only),
                "CREDIT_ONLY"  (explicitly credit-floors-only).
    """
    rule = PROGRAMME_RULES.get(programme)
    if rule is None:
        return None
    if rule == "CREDIT_ONLY":
        return "CREDIT_ONLY"
    if rule == "MINORS":
        return {"type": "minors", "minors": SOC_SCI_MINORS,
                "min_minors": SOC_SCI_MIN_MINORS}
    if isinstance(rule, str) and rule.startswith("ALIAS:"):
        return lookup(rule.split("ALIAS:", 1)[1], entry_year)

    chosen = None
    for era in rule:
        if _era_matches(era["years"], entry_year):
            chosen = era
            break
    if chosen is None:
        # entry year falls outside known eras -> use the most recent era, flagged
        chosen = rule[-1]
        note = chosen.get("notes", "")
        chosen = dict(chosen)
        chosen["notes"] = (note + f"  NOTE: entry {entry_year} outside encoded eras; "
                           "closest available era used \u2014 confirm.")
    return {
        "era": chosen["era"],
        "level1_fixed": set(chosen.get("level1_fixed", set())),
        "level1_either_or": [set(g) for g in chosen.get("level1_either_or", [])],
        "level23_named": set(chosen.get("level23_named", set())),
        "level23_either_or": [set(g) for g in chosen.get("level23_either_or", [])],
        "notes": chosen.get("notes", ""),
    }
