"""
Analytics for the summary reports: department + graduating-semester derivation,
and the summary tables requested (degree-band by programme, semester by programme,
First Class lists, department roll-ups).

These operate on the list of eligibility `results` plus the parsed `students`
(which carry the course terms needed to derive graduating semester).
"""
from collections import defaultdict, Counter
from .department_map import department_of, DEPARTMENT_ORDER

BANDS_ORDER = ["First Class Honours", "Upper Second Class Honours",
               "Lower Second Class Honours", "Pass"]


# --- term / semester / year helpers ----------------------------------------
def _term_semester(term):
    """YYYYTT -> 'Semester 1' / 'Semester 2' / 'Summer'."""
    tt = term[-2:]
    return {"10": "Semester 1", "20": "Semester 2", "30": "Summer"}.get(tt, "Other")


def _term_year(term):
    """YYYYTT -> 'YYYY/YYYY+1' academic year."""
    y = int(term[:4])
    return f"{y}/{y + 1}"


def grad_term(student):
    """The student's latest course term (proxy for when they complete)."""
    terms = [c["term"] for c in student.get("courses", []) if c.get("term")]
    return max(terms) if terms else None


def grad_semester(student):
    t = grad_term(student)
    return _term_semester(t) if t else "Unknown"


def grad_year(student):
    t = grad_term(student)
    return _term_year(t) if t else "Unknown"


def current_academic_year(students):
    """The most common graduating year across the cohort = 'current' year."""
    years = Counter(grad_year(s) for s in students if grad_term(s))
    return years.most_common(1)[0][0] if years else None


def last_n_years(current_year, n=3):
    """List of the last n academic years ending in current_year, oldest first."""
    if not current_year:
        return []
    start = int(current_year.split("/")[0])
    return [f"{y}/{y + 1}" for y in range(start - n + 1, start + 1)]


# --- enrichment -------------------------------------------------------------
def enrich(results, students):
    """Attach department, grad_year, grad_semester to each ELIGIBLE result."""
    by_id = {s["id"]: s for s in students}
    for r in results:
        s = by_id.get(r["id"])
        r["department"] = department_of(r["programme"])
        if s:
            r["grad_year"] = grad_year(s)
            r["grad_semester"] = grad_semester(s)
        else:
            r["grad_year"] = "Unknown"
            r["grad_semester"] = "Unknown"
    return results


def _is_eligible(r):
    return r.get("verdict", "").startswith("ELIGIBLE")


# --- the summary tables -----------------------------------------------------
def first_class_by_programme(results):
    """{department: {programme: [ {name,id,gpa,page} ... ]}} for First Class eligibles."""
    out = defaultdict(lambda: defaultdict(list))
    for r in results:
        if _is_eligible(r) and r.get("class_of_degree") == "First Class Honours":
            out[r["department"]][r["programme"]].append({
                "name": r["name"], "id": r["id"],
                "gpa": r.get("weighted_gpa"), "printed_gpa": r.get("gpa"),
                "page": r.get("page"),
            })
    return out


def bands_by_programme(results, years):
    """
    {department: {programme: {band: count}}} for ELIGIBLE students whose grad_year
    is within `years`. Restricted to eligible students.
    """
    out = defaultdict(lambda: defaultdict(lambda: Counter()))
    for r in results:
        if _is_eligible(r) and r.get("grad_year") in years:
            band = r.get("class_of_degree")
            if band in BANDS_ORDER:
                out[r["department"]][r["programme"]][band] += 1
    return out


def semester_by_programme(results, years):
    """
    {department: {programme: {semester: count}}} for ELIGIBLE students within `years`.
    """
    out = defaultdict(lambda: defaultdict(lambda: Counter()))
    for r in results:
        if _is_eligible(r) and r.get("grad_year") in years:
            out[r["department"]][r["programme"]][r.get("grad_semester")] += 1
    return out


def first_class_by_department(results):
    """{department: count} of First Class eligibles."""
    c = Counter()
    for r in results:
        if _is_eligible(r) and r.get("class_of_degree") == "First Class Honours":
            c[r["department"]] += 1
    return c


def current_year_semester_bands(results, current_year):
    """
    {semester: {band: count}} for ELIGIBLE students graduating in the current year.
    """
    out = defaultdict(lambda: Counter())
    for r in results:
        if _is_eligible(r) and r.get("grad_year") == current_year:
            band = r.get("class_of_degree")
            if band in BANDS_ORDER:
                out[r.get("grad_semester")][band] += 1
    return out


# ===========================================================================
# Cross-period helpers (operate on stored MASTER rows = list of dicts from SQLite)
# ===========================================================================
def master_first_class_by_department(rows):
    c = Counter()
    for r in rows:
        if r.get("eligible") and r.get("class_of_degree") == "First Class Honours":
            c[r.get("department")] += 1
    return c


def master_bands_by_year(rows):
    """{grad_year: {band: count}} for eligible students."""
    out = defaultdict(lambda: Counter())
    for r in rows:
        if r.get("eligible") and r.get("class_of_degree") in BANDS_ORDER:
            out[r.get("grad_year")][r["class_of_degree"]] += 1
    return out


def master_eligible_by_year_dept(rows):
    """{grad_year: {department: count}} for eligible students."""
    out = defaultdict(lambda: Counter())
    for r in rows:
        if r.get("eligible"):
            out[r.get("grad_year")][r.get("department")] += 1
    return out
