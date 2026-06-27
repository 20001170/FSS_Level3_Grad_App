"""
Eligibility engine.

Applies, per student:
  1. Credit floors (>=90 total, >=30 Level I, >=60 Level II/III), with EC exemptions
     counted toward the floors (an 'EC' grade earns the requirement-credit even though
     it shows 0 quality-point credit in the printed total).
  2. Named-course requirements from the handbook era matching the student's entry year
     (see engine/requirements.py).
  3. Class of degree on the WEIGHTED GPA (Level I weight zero; Levels II & III, passed
     courses) per the Faculty regulation, with the printed Degree GPA carried alongside.

Returns one result dict per student.
"""
from .requirements import get_requirements
from .weighted_gpa import weighted_gpa_l23, classify as classify_weighted
from .settings import classify as _class_from_printed, CREDIT_FLOORS, CREDITS_PER_COURSE


def _passed_codes(student):
    codes = set()
    for c in student["courses"]:
        if c["status"] in ("passed", "exempted"):
            codes.add(c["code"])
    return codes


def _ec_credits_by_level(student):
    ec = {"1": 0, "2": 0, "3": 0}
    for c in student["courses"]:
        if c.get("grade") == "EC":
            parts = c["code"].split()
            if len(parts) >= 2:
                lv = parts[1][0]
                if lv in ec:
                    ec[lv] += c.get("credits_attempted", 0)
    return ec


def check_student(s):
    total = s["total_credits"] or 0
    lvl1 = s["levels"].get("level1", {}).get("earned", 0)
    lvl2 = s["levels"].get("level2", {}).get("earned", 0)
    lvl3 = s["levels"].get("level3", {}).get("earned", 0)

    ec = _ec_credits_by_level(s)
    lvl1_eff = lvl1 + ec["1"]
    lvl23 = (lvl2 + ec["2"]) + (lvl3 + ec["3"])
    total_eff = total + ec["1"] + ec["2"] + ec["3"]
    ec_total = ec["1"] + ec["2"] + ec["3"]

    credits_short = max(0, CREDIT_FLOORS["total"] - total_eff)
    l1_short = max(0, CREDIT_FLOORS["level1"] - lvl1_eff)
    l23_short = max(0, CREDIT_FLOORS["level23"] - lvl23)
    numeric_ok = (credits_short == 0 and l1_short == 0 and l23_short == 0)

    req = get_requirements(s["programme"], s["entry_year"])

    base = {
        "name": s["name"], "id": s["id"], "programme": s["programme"],
        "entry_year": s["entry_year"], "page": s.get("page"),
        "gpa": s["gpa"], "total_credits": total,
        "total_credits_effective": total_eff,
        "ec_credits": {"level1": ec["1"], "level2": ec["2"], "level3": ec["3"]},
        "ec_total": ec_total,
        "level1_earned": lvl1_eff, "level23_earned": lvl23,
    }

    if isinstance(req, dict) and req.get("type") == "minors":
        # Minors-based programme (B.Sc. Social Sciences): student must satisfy at
        # least `min_minors` minors (have all the fixed named courses of each) AND
        # clear the credit floors. The "any Level II/III in X" slots and the 5 free
        # electives are examiner-confirmed.
        passed = _passed_codes(s)
        satisfied = []
        for minor_name, courses in req["minors"].items():
            if courses and courses <= passed:
                satisfied.append(minor_name)
        n_min = req["min_minors"]
        minors_ok = len(satisfied) >= n_min
        ey = s.get("entry_year")
        wgpa = None; cls_w = ""; cls_p = ""; differs = False
        if numeric_ok and minors_ok:
            wg, _ = weighted_gpa_l23(s)
            wgpa = round(wg, 3)
            cls_w = classify_weighted(wg, ey)
            cls_p = _class_from_printed(s["gpa"], ey)
            differs = (cls_w != cls_p)
            verdict = (f"ELIGIBLE ({len(satisfied)} minors satisfied: "
                       f"{', '.join(satisfied)})")
        elif numeric_ok and not minors_ok:
            verdict = (f"NOT ELIGIBLE — only {len(satisfied)} of {n_min} required minors "
                       f"complete ({', '.join(satisfied) or 'none'}); credit floors met")
        else:
            est = -(-max(credits_short, l1_short, l23_short) // CREDITS_PER_COURSE)
            verdict = (f"NOT ELIGIBLE — ~{est} course(s) short numerically; "
                       f"{len(satisfied)} of {n_min} minors complete")
        base.update({
            "checked": "minors", "era": None,
            "missing_level1": [], "missing_level23_named": [],
            "minors_satisfied": satisfied,
            "numeric_ok": numeric_ok, "named_ok": minors_ok,
            "verdict": verdict,
            "notes": ("B.Sc. Social Sciences: requires 3 completed minors (fixed named "
                      "courses checked) + credit floors; elective slots examiner-confirmed."),
            "weighted_gpa": wgpa, "class_of_degree": cls_w,
            "class_printed_gpa": cls_p, "class_differs": differs,
        })
        return base

    if req == "CREDIT_ONLY":
        # Programme is, by design, screened on credit floors only (e.g. the flexible
        # B.Sc. Social Sciences degree, where students choose minors freely). If the
        # floors clear, the student is eligible and gets a class of degree; the named
        # internal structure (minors) is examiner-confirmed.
        wgpa = None
        cls_w = ""
        cls_p = ""
        differs = False
        if numeric_ok:
            ey = s.get("entry_year")
            wg, _ = weighted_gpa_l23(s)
            wgpa = round(wg, 3)
            cls_w = classify_weighted(wg, ey)
            cls_p = _class_from_printed(s["gpa"], ey)
            differs = (cls_w != cls_p)
            verdict = ("ELIGIBLE on credit floors (flexible-structure programme; "
                       "minor/elective composition is examiner-confirmed)")
        else:
            est = -(-max(credits_short, l1_short, l23_short) // CREDITS_PER_COURSE)
            verdict = f"NOT ELIGIBLE — ~{est} course(s) short numerically"
        base.update({
            "checked": "credit_only_by_design", "era": None,
            "missing_level1": [], "missing_level23_named": [],
            "numeric_ok": numeric_ok, "named_ok": numeric_ok or None,
            "verdict": verdict,
            "notes": ("Flexible-structure programme: screened on the 90/30/60 credit "
                      "floors; minor/elective composition is examiner-confirmed."),
            "weighted_gpa": wgpa, "class_of_degree": cls_w,
            "class_printed_gpa": cls_p, "class_differs": differs,
        })
        return base

    if req is None:
        # Unknown programme: no named rule set encoded yet. Apply credit floors but do
        # NOT certify as eligible -- flag for the examiner / for encoding.
        if numeric_ok:
            verdict = ("CREDIT FLOORS MET — named-course rule set not encoded for this "
                       "programme; refer to examiner for named-course confirmation")
        else:
            est = -(-max(credits_short, l1_short, l23_short) // CREDITS_PER_COURSE)
            verdict = (f"NOT ELIGIBLE — ~{est} course(s) short numerically "
                       "(named-course rule set not encoded for this programme)")
        base.update({
            "checked": "credit_only", "era": None,
            "missing_level1": [], "missing_level23_named": [],
            "numeric_ok": numeric_ok, "named_ok": None,
            "verdict": verdict,
            "notes": "Named-course rule set not yet encoded; credit floors applied only.",
            "weighted_gpa": None, "class_of_degree": "",
            "class_printed_gpa": "", "class_differs": False,
        })
        return base

    passed = _passed_codes(s)
    l1_fixed_missing = sorted(req["level1_fixed"] - passed)
    l1_eitheror_missing = []
    for group in req.get("level1_either_or", []):
        if not (group & passed):
            l1_eitheror_missing.append(" or ".join(sorted(group)))
    l23_missing = sorted(req["level23_named"] - passed)
    l23_eitheror_missing = []
    for group in req.get("level23_either_or", []):
        if not (group & passed):
            l23_eitheror_missing.append(" or ".join(sorted(group)))

    all_named_missing = (l1_fixed_missing + l1_eitheror_missing
                         + l23_missing + l23_eitheror_missing)
    named_ok = len(all_named_missing) == 0

    ec_note = ""
    if ec_total:
        ec_note = (f" (incl. {ec_total} EC-exemption credit(s): "
                   f"L1+{ec['1']}, L2+{ec['2']}, L3+{ec['3']})")

    # Weighted GPA + class of degree (only meaningful for eligible students)
    wgpa = None
    cls_w = ""
    cls_p = ""
    differs = False

    if numeric_ok and named_ok:
        verdict = "ELIGIBLE (numeric + named-course checks both clear)" + ec_note
        wg, _ = weighted_gpa_l23(s)
        wgpa = round(wg, 3)
        ey = s.get("entry_year")
        cls_w = classify_weighted(wg, ey)
        cls_p = _class_from_printed(s["gpa"], ey)
        differs = (cls_w != cls_p)
    elif numeric_ok and not named_ok:
        verdict = (f"NOT ELIGIBLE — numeric OK but missing named course(s): "
                   f"{all_named_missing}" + ec_note)
    else:
        est = -(-max(credits_short, l1_short, l23_short) // CREDITS_PER_COURSE)
        gap = all_named_missing or "none beyond numeric shortfall"
        verdict = (f"NOT ELIGIBLE — ~{est} course(s) short numerically; "
                   f"named gaps: {gap}" + ec_note)

    base.update({
        "checked": True, "era": req.get("era"),
        "missing_level1": l1_fixed_missing + l1_eitheror_missing,
        "missing_level23_named": l23_missing + l23_eitheror_missing,
        "numeric_ok": numeric_ok, "named_ok": named_ok,
        "verdict": verdict, "notes": req.get("notes", ""),
        "weighted_gpa": wgpa, "class_of_degree": cls_w,
        "class_printed_gpa": cls_p, "class_differs": differs,
    })
    return base


def check_all(students):
    return [check_student(s) for s in students]


def summarize(results):
    eligible = [r for r in results if r["verdict"].startswith("ELIGIBLE")]
    critical = [r for r in results if "numeric OK but missing" in r["verdict"]]
    import re
    near = []
    for r in results:
        if r["verdict"].startswith("NOT ELIGIBLE — ~") and r.get("named_ok"):
            m = re.search(r"~(\d+) course", r["verdict"])
            n = int(m.group(1)) if m else 99
            if n <= 2:
                near.append({"n": n, **r})
    near.sort(key=lambda x: (x["n"], x["name"]))
    return {
        "total": len(results),
        "eligible": sorted(eligible, key=lambda x: -(x["weighted_gpa"] or 0)),
        "critical": critical,
        "near": near,
        "counts": {
            "total": len(results),
            "eligible": len(eligible),
            "critical": len(critical),
            "near": len(near),
        },
    }
