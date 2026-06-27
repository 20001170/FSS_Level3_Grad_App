"""
=============================================================================
  STORAGE  --  multi-semester history in a SQLite database
=============================================================================

Stores each upload as a "batch", and every student row within it, so that:
  * each upload's own reports stay exactly as produced (we keep raw per-batch
    rows untouched);
  * a cross-period MASTER view can be built on demand by de-duplicating students
    across all batches, keeping each student's MOST-COMPLETE record (most credits,
    then most courses, then most recent upload).

WHERE THE DATABASE LIVES
  By default the DB sits next to the app in a local 'data' folder. To put it on a
  shared network drive so several staff share one history, set the path in
  engine/storage_config.py (FSS_DB_PATH), e.g.:
        FSS_DB_PATH = r"S:\\FSS\\eligibility\\history.db"
  If that path can't be reached, the app automatically falls back to the local
  copy (so it never crashes just because the share is offline) and tells the user.

CONCURRENCY NOTE
  SQLite on a shared drive is fine for occasional, one-at-a-time use (the normal
  registry workflow). It is not designed for many people writing at the very same
  instant. Reads are always safe.
"""
import os
import sys
import json
import sqlite3
import datetime


# --- locating the database --------------------------------------------------
def _app_base():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def configured_db_path():
    """Path from engine/storage_config.py if present, else local default."""
    try:
        from . import storage_config
        p = getattr(storage_config, "FSS_DB_PATH", None)
        if p:
            return p
    except Exception:
        pass
    return os.path.join(_app_base(), "data", "history.db")


def _local_fallback_path():
    return os.path.join(_app_base(), "data", "history.db")


def resolve_db_path():
    """
    Return (path, used_fallback, message). Tries the configured path; if its
    directory can't be created/written, falls back to the local data folder.
    """
    want = configured_db_path()
    try:
        os.makedirs(os.path.dirname(want), exist_ok=True)
        # write test
        testfile = os.path.join(os.path.dirname(want), ".write_test")
        with open(testfile, "w") as f:
            f.write("ok")
        os.remove(testfile)
        return want, False, ""
    except Exception as e:
        fb = _local_fallback_path()
        os.makedirs(os.path.dirname(fb), exist_ok=True)
        msg = (f"Configured database location was not reachable ({want}); "
               f"using the local copy instead. ({e})")
        return fb, True, msg


# --- schema -----------------------------------------------------------------
_SCHEMA = """
CREATE TABLE IF NOT EXISTS batches (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    uploaded_at  TEXT NOT NULL,
    source_file  TEXT,
    academic_year TEXT,
    n_students   INTEGER,
    n_eligible   INTEGER
);
CREATE TABLE IF NOT EXISTS student_rows (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id     INTEGER NOT NULL,
    student_id   TEXT,
    name         TEXT,
    programme    TEXT,
    department   TEXT,
    entry_year   TEXT,
    grad_year    TEXT,
    grad_semester TEXT,
    eligible     INTEGER,
    class_of_degree TEXT,
    weighted_gpa REAL,
    printed_gpa  REAL,
    total_credits INTEGER,
    n_courses    INTEGER,
    page         INTEGER,
    verdict      TEXT,
    FOREIGN KEY(batch_id) REFERENCES batches(id)
);
CREATE INDEX IF NOT EXISTS idx_rows_student ON student_rows(student_id);
CREATE INDEX IF NOT EXISTS idx_rows_batch ON student_rows(batch_id);
"""


def _connect():
    path, used_fallback, msg = resolve_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn, path, used_fallback, msg


# --- saving a batch ---------------------------------------------------------
def save_batch(results, students, source_file, academic_year):
    """
    Persist one upload. Returns dict with batch_id, db_path, used_fallback, message.
    `results` is the eligibility output (already enriched with department/grad_*).
    """
    by_id = {s["id"]: s for s in students}
    conn, path, used_fallback, msg = _connect()
    try:
        cur = conn.cursor()
        n_elig = sum(1 for r in results if r.get("verdict", "").startswith("ELIGIBLE"))
        cur.execute(
            "INSERT INTO batches (uploaded_at, source_file, academic_year, n_students, n_eligible)"
            " VALUES (?,?,?,?,?)",
            (datetime.datetime.now().isoformat(timespec="seconds"),
             source_file, academic_year, len(results), n_elig),
        )
        batch_id = cur.lastrowid
        rows = []
        for r in results:
            s = by_id.get(r["id"], {})
            n_courses = len(s.get("courses", []))
            rows.append((
                batch_id, r.get("id"), r.get("name"), r.get("programme"),
                r.get("department"), r.get("entry_year"),
                r.get("grad_year"), r.get("grad_semester"),
                1 if r.get("verdict", "").startswith("ELIGIBLE") else 0,
                r.get("class_of_degree") or "",
                r.get("weighted_gpa"), r.get("gpa"),
                r.get("total_credits_effective") or r.get("total_credits"),
                n_courses, r.get("page"), r.get("verdict"),
            ))
        cur.executemany(
            "INSERT INTO student_rows (batch_id, student_id, name, programme, department,"
            " entry_year, grad_year, grad_semester, eligible, class_of_degree, weighted_gpa,"
            " printed_gpa, total_credits, n_courses, page, verdict)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows,
        )
        conn.commit()
        return {"batch_id": batch_id, "db_path": path,
                "used_fallback": used_fallback, "message": msg}
    finally:
        conn.close()


# --- listing batches --------------------------------------------------------
def list_batches():
    conn, path, used_fallback, msg = _connect()
    try:
        cur = conn.execute(
            "SELECT id, uploaded_at, source_file, academic_year, n_students, n_eligible"
            " FROM batches ORDER BY id DESC")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def delete_batch(batch_id):
    conn, *_ = _connect()
    try:
        conn.execute("DELETE FROM student_rows WHERE batch_id=?", (batch_id,))
        conn.execute("DELETE FROM batches WHERE id=?", (batch_id,))
        conn.commit()
    finally:
        conn.close()


# --- master (deduped) view --------------------------------------------------
def master_rows():
    """
    Return one row per student across ALL batches, keeping the most-complete record
    (most total_credits, then most n_courses, then most recent batch_id).
    """
    conn, *_ = _connect()
    try:
        cur = conn.execute("SELECT * FROM student_rows")
        best = {}
        for r in cur.fetchall():
            sid = r["student_id"]
            key = (r["total_credits"] or 0, r["n_courses"] or 0, r["batch_id"])
            if sid not in best or key > best[sid][0]:
                best[sid] = (key, dict(r))
        return [v[1] for v in best.values()]
    finally:
        conn.close()


def master_stats():
    rows = master_rows()
    elig = [r for r in rows if r["eligible"]]
    return {"students": len(rows), "eligible": len(elig)}
