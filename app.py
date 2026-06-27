"""
FSS Level 3 Graduation Eligibility — local web app.

Run:  python app.py
Then open http://127.0.0.1:5000 in your browser, upload a BOE PDF, and download
the eligibility report as .docx, .pdf, or the .xlsx review sheet.

Everything runs locally on your machine; no data leaves the computer.
"""
import os
import io
import sys
import json
import uuid
import tempfile
import datetime

from flask import (Flask, request, render_template, send_file, redirect,
                   url_for, flash, session, jsonify)

from engine.parser import parse_boe_pdf
from engine.eligibility import check_all, summarize
from engine.reports import build_xlsx, build_docx, build_pdf
from engine.summary_reports import build_summary_docx, build_summary_xlsx
from engine import analytics as analytics
from engine import storage as storage


def _resource_base():
    """Folder that holds templates/ and bundled tools.

    When running as a normal script this is the app folder. When bundled by
    PyInstaller into a single .exe, data files are unpacked to sys._MEIPASS.
    """
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


_BASE = _resource_base()

# If a Poppler 'bin' folder was bundled (or sits next to the exe), put it on PATH
# so pdftotext is found without the user installing anything.
for _cand in (
    os.path.join(_BASE, "poppler", "bin"),
    os.path.join(os.path.dirname(sys.executable), "poppler", "bin"),
):
    if os.path.isdir(_cand):
        os.environ["PATH"] = _cand + os.pathsep + os.environ.get("PATH", "")
        break

app = Flask(
    __name__,
    template_folder=os.path.join(_BASE, "templates"),
    static_folder=os.path.join(_BASE, "static") if os.path.isdir(os.path.join(_BASE, "static")) else None,
)
app.secret_key = "fss-local-app"  # local-only; not security-sensitive
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024  # 60 MB cap

# Where uploaded PDFs and generated files live for the session.
WORK_DIR = os.path.join(tempfile.gettempdir(), "fss_eligibility")
os.makedirs(WORK_DIR, exist_ok=True)

# In-memory cache of the most recent run per session token.
RUNS = {}


def _human_pct(part, whole):
    return f"{(100.0 * part / whole):.0f}%" if whole else "0%"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process():
    file = request.files.get("pdf")
    if not file or file.filename == "":
        flash("Please choose a BOE PDF file to upload.")
        return redirect(url_for("index"))
    if not file.filename.lower().endswith(".pdf"):
        flash("That doesn't look like a PDF. Please upload the BOE PDF file.")
        return redirect(url_for("index"))

    token = uuid.uuid4().hex[:12]
    run_dir = os.path.join(WORK_DIR, token)
    os.makedirs(run_dir, exist_ok=True)
    pdf_path = os.path.join(run_dir, "boe.pdf")
    file.save(pdf_path)

    try:
        students = parse_boe_pdf(pdf_path)
    except Exception as e:
        flash(f"Could not read that PDF: {e}")
        return redirect(url_for("index"))

    if not students:
        flash("No student records were found in that PDF. Is it a Board of Examiners "
              "academic-record export (with 'Degree GPA' and 'Level N Credits Earned' lines)?")
        return redirect(url_for("index"))

    results = check_all(students)
    summary = summarize(results)

    # Build all deliverables now so downloads are instant.
    stamp = datetime.datetime.now().strftime("%Y%m%d")
    paths = {
        "xlsx": os.path.join(run_dir, f"Level3_Eligibility_Review_{stamp}.xlsx"),
        "docx": os.path.join(run_dir, f"Level3_Eligibility_Report_{stamp}.docx"),
        "pdf": os.path.join(run_dir, f"Level3_Eligibility_Report_{stamp}.pdf"),
        "summary_docx": os.path.join(run_dir, f"Level3_Summary_Report_{stamp}.docx"),
        "summary_xlsx": os.path.join(run_dir, f"Level3_Summary_Tables_{stamp}.xlsx"),
    }
    build_xlsx(results, paths["xlsx"])
    build_docx(summary, paths["docx"])
    build_pdf(summary, paths["pdf"], docx_path=paths["docx"])
    # Summary reports (department/programme roll-ups, First Class lists, band/semester tables)
    build_summary_docx(results, students, paths["summary_docx"])
    build_summary_xlsx(results, students, paths["summary_xlsx"])

    # Persist this upload to the multi-year history (results are now enriched with
    # department + grad_year/grad_semester by the summary builders). Each upload is
    # stored separately; the master/cross-period view dedupes on demand only.
    save_note = ""
    try:
        cy = analytics.current_academic_year(students)
        info = storage.save_batch(results, students, source_file=file.filename, academic_year=cy)
        if info.get("used_fallback"):
            save_note = info.get("message", "")
    except Exception as e:
        save_note = f"History not saved this run ({e})."

    RUNS[token] = {"summary": summary, "results": results, "paths": paths}
    session["token"] = token

    # Build a lightweight, unrecognized-programme notice
    credit_only = [r for r in results if r.get("checked") == "credit_only"]
    return render_template(
        "results.html",
        token=token,
        c=summary["counts"],
        eligible=summary["eligible"],
        critical=summary["critical"],
        near=summary["near"],
        credit_only=credit_only,
        pct_eligible=_human_pct(summary["counts"]["eligible"], summary["counts"]["total"]),
    )


@app.route("/download/<token>/<kind>")
def download(token, kind):
    run = RUNS.get(token)
    if not run or kind not in run["paths"]:
        flash("That download has expired. Please upload the PDF again.")
        return redirect(url_for("index"))
    path = run["paths"][kind]
    if not os.path.exists(path):
        flash("File not found — please re-run.")
        return redirect(url_for("index"))
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/history")
def history():
    try:
        batches = storage.list_batches()
        stats = storage.master_stats()
        db_path, used_fallback, msg = storage.resolve_db_path()
    except Exception as e:
        batches, stats, db_path, used_fallback, msg = [], {"students": 0, "eligible": 0}, "", False, str(e)
    return render_template("history.html", batches=batches, stats=stats,
                           db_path=db_path, used_fallback=used_fallback, msg=msg)


@app.route("/history/cross_period.xlsx")
def cross_period():
    from engine.summary_reports import build_master_summary_xlsx
    rows = storage.master_rows()
    if not rows:
        flash("No stored history yet. Upload at least one BOE record first.")
        return redirect(url_for("history"))
    out = os.path.join(WORK_DIR, "Cross_Period_Summary.xlsx")
    build_master_summary_xlsx(rows, out)
    return send_file(out, as_attachment=True, download_name="Cross_Period_Summary.xlsx")


@app.route("/history/delete/<int:batch_id>", methods=["POST"])
def history_delete(batch_id):
    try:
        storage.delete_batch(batch_id)
        flash("Upload removed from history.")
    except Exception as e:
        flash(f"Could not remove that upload ({e}).")
    return redirect(url_for("history"))


if __name__ == "__main__":
    import webbrowser
    import threading

    url = "http://127.0.0.1:5000"
    print("\n" + "=" * 60)
    print("  FSS Level 3 Graduation Eligibility App")
    print("  Open your browser to:  " + url)
    print("  (Press CTRL+C here to stop the app.)")
    print("=" * 60 + "\n")
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
