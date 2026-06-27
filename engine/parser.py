"""
BOE academic-record parser.

Takes the raw text of a Board of Examiners PDF (extracted with `pdftotext -layout`)
and returns a list of structured student records. Splits on each student's name-ID
line (NOT on page headers) so that two students sharing a physical page are kept apart.

Each student dict has:
  name, id, programme, entry_year, entry_sem, gpa (printed Degree GPA),
  total_credits (printed), levels {level1/2/3: {earned, attempted}}, page, courses[]

Each course dict has:
  term, code ("DEPT NNNN"), grade, credits_earned, credits_attempted, status
  status in {passed, exempted, failed_or_other, in_progress}
"""
import re
import subprocess
import tempfile
import os


# ---- regexes -------------------------------------------------------------

NAME_ID_RE = re.compile(
    r"^([A-Z][A-Za-z\u00C0-\u00ff'\.\-, ]+?)\s*-\s*(\d{6,9})\s+(.+?)\s*$",
    re.MULTILINE,
)
META_RE = re.compile(r"Entry:\s*(\d{4}/\d{4})\s*Semester\s*(\w+)")
GPA_RE = re.compile(r"Degree GPA:\s*([\d.]+)\s+Total Credits:\s*(\d+)")
PAGE_RE = re.compile(r"Page (\d+) of \d+")
LEVEL_LINE_RE = re.compile(
    r"Level (\d) Credits Earned:\s*(\d+)\s*/\s*Attempted:\s*(\d+)"
)
COURSE_PAT = re.compile(
    r"(\d{6})\s+([A-Z]{2,4}\s?\d{4})\s+(?:(\d{1,3})\s+)?"
    r"([A-Z0-9+\-]{1,3}|EX|EC|LW|AM|IP|DNS|NA)\s*([\d.]*)\s*(\d+)/(\d+)"
)
INPROGRESS_PAT = re.compile(r"(\d{6})\s+([A-Z]{2,4}\s?\d{4})\s+/(\d+)(?!/)")

NOISE_PATTERNS = [
    r"^.*THE UNIVERSITY OF THE WEST INDIES.*$",
    r"^\s*CAVE HILL CAMPUS\s*$",
    r"^\s*ACADEMIC RECORD\s*$",
    r"^\s*Cave Hill\s*$",
    r"^\s*Cave Hill Campus\s*$",
    r"^\s*Social Sciences\s*$",
    r"^\s*Term Course Code Grade QP Credits.*$",
    r"^\s*\w+,\s+\d+\s+\w+\s+\d{4}.*$",   # date stamp line e.g. "Tuesday, 2 June 2026"
    r"^\s*Page \d+ of \d+\s*$",
]


# ---- helpers -------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> str:
    """Run pdftotext -layout and return the text."""
    import shutil
    if shutil.which("pdftotext") is None:
        raise RuntimeError(
            "The 'pdftotext' tool (Poppler) was not found. If you are running the "
            "packaged .exe, make sure the 'poppler' folder sits next to it. If you are "
            "running from source, install Poppler and add its 'bin' folder to PATH."
        )
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        out_path = tmp.name
    try:
        subprocess.run(
            ["pdftotext", "-layout", pdf_path, out_path],
            check=True, capture_output=True,
        )
        with open(out_path, encoding="utf-8", errors="replace") as f:
            return f.read()
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)


def _parse_courses(block: str):
    courses = []
    for m in COURSE_PAT.finditer(block):
        term, code, score, grade, qp, earned, attempted = m.groups()
        code = re.sub(r"\s+", " ", code.strip())
        earned_i = int(earned)
        if grade == "IP":
            status = "in_progress"
        elif grade in ("EX", "EC"):
            status = "exempted"
        elif earned_i > 0:
            status = "passed"
        else:
            status = "failed_or_other"
        courses.append({
            "term": term, "code": code, "grade": grade,
            "credits_earned": earned_i, "credits_attempted": int(attempted),
            "status": status,
        })
    for m in INPROGRESS_PAT.finditer(block):
        term, code, attempted = m.groups()
        code = re.sub(r"\s+", " ", code.strip())
        courses.append({
            "term": term, "code": code, "grade": None,
            "credits_earned": 0, "credits_attempted": int(attempted),
            "status": "in_progress",
        })
    return courses


def _page_map(original_text: str):
    """Map student id -> page number (the page footer that follows the header)."""
    page_of = {}
    pending = []
    for line in original_text.splitlines():
        nm = re.match(r"^([A-Z][A-Za-z\u00C0-\u00ff'\.\-, ]+?)\s*-\s*(\d{6,9})", line)
        if nm:
            pending.append(nm.group(2))
        pm = PAGE_RE.search(line)
        if pm:
            for sid in pending:
                page_of[sid] = int(pm.group(1))
            pending = []
    return page_of


# ---- main entry point ----------------------------------------------------

def parse_boe_text(text: str):
    """Parse raw BOE text into a list of student records."""
    original_text = text

    # Fix the long-name line-wrap quirk: NAME -\nID -> NAME - ID
    text = re.sub(
        r"(^[A-Z][A-Za-z\u00C0-\u00ff'\.\-, ]+?\s*-\s+)([A-Za-z].*?)\n(\d{6,9})\n",
        r"\1\3 \2\n",
        text,
        flags=re.MULTILINE,
    )

    # Strip page-header/footer noise so a record isn't interrupted mid-stream
    clean = text
    for pat in NOISE_PATTERNS:
        clean = re.sub(pat, "", clean, flags=re.MULTILINE)

    page_of = _page_map(original_text)

    matches = list(NAME_ID_RE.finditer(clean))
    students = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(clean)
        block = clean[start:end]

        name = m.group(1).strip()
        sid = m.group(2)
        raw_prog = m.group(3).strip()
        # Capture a concentration if present (e.g. "... Concentration: Marketing")
        concentration = None
        cm = re.search(r"Concentration:\s*(.+?)\s*$", raw_prog)
        if cm:
            concentration = cm.group(1).strip()
            raw_prog = raw_prog[:cm.start()].strip()
        # Strip degree tags (BSC C, BSC, BBA C, BBA) and collapse internal whitespace
        programme = re.sub(r"\s+(BSC|BBA)(\s+C)?\s*$", "", raw_prog).strip()
        programme = re.sub(r"\s{2,}", " ", programme).strip()

        meta = META_RE.search(block)
        entry_year, entry_sem = (meta.group(1), meta.group(2)) if meta else (None, None)
        gpa_m = GPA_RE.search(block)
        gpa, total_credits = (
            (float(gpa_m.group(1)), int(gpa_m.group(2))) if gpa_m else (None, None)
        )

        # Independent per-level parse, first occurrence of each level wins
        levels = {
            "level1": {"earned": 0, "attempted": 0},
            "level2": {"earned": 0, "attempted": 0},
            "level3": {"earned": 0, "attempted": 0},
        }
        seen = set()
        for lvl, earned, att in LEVEL_LINE_RE.findall(block):
            key = f"level{lvl}"
            if key in levels and lvl not in seen:
                levels[key] = {"earned": int(earned), "attempted": int(att)}
                seen.add(lvl)
            if len(seen) == 3:
                break
        if not seen:
            levels = {}

        courses = _parse_courses(block)

        # Only keep genuine records (must have a GPA + total + level summary)
        if gpa is None or total_credits is None or not levels:
            continue

        students.append({
            "name": name, "id": sid, "programme": programme,
            "concentration": concentration,
            "entry_year": entry_year, "entry_sem": entry_sem,
            "gpa": gpa, "total_credits": total_credits,
            "levels": levels, "page": page_of.get(sid),
            "courses": courses,
        })

    return students


def parse_boe_pdf(pdf_path: str):
    """Convenience: extract text from a PDF path and parse it."""
    return parse_boe_text(extract_text_from_pdf(pdf_path))
