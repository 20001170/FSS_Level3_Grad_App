# FSS Level 3 Graduation Eligibility — Local App

A local web app for the UWI Cave Hill Faculty of Social Sciences. Upload a Board of
Examiners (BOE) academic-record PDF; the app determines, for each Level 3 student,
whether they are eligible to graduate, what is outstanding for those who are not, and
the class of degree for those who are — then produces a downloadable report.

> **Multi-year history.** Every upload is saved to a small database so you can keep
> several years of data. Each upload's own reports always reflect just that file; a
> separate **cross-period summary** (on the History page) merges all uploads, keeping
> each student's most-complete record. To share one history across staff, point the
> app at a network drive in `engine/storage_config.py` (see that file). 

> **Future handbooks.** Requirements are entry-year aware: students are always held to
> their year-of-entry rules. When a programme changes for a future intake, add a
> year-bounded "era" — see **HANDBOOK_UPDATES.md**. The handbooks themselves are
> bundled in the `handbooks/` folder for reference.

Everything runs on your own computer. No data is sent anywhere.

> **Coverage:** all 58 programme labels in the Faculty Level 3 record are mapped —
> 27 with full named-course checks, 17 aliased to a parent programme, 1 minors-based
> (B.Sc. Social Sciences), and 13 small/specialised programmes screened on credit
> floors and clearly flagged for examiner confirmation. No student is left
> uncategorised: every record returns eligible, missing-a-named-course, short-on-
> credits, or credit-floors-met-pending-examiner-confirmation.

> **Want a one-click app with no Python install?** Two ways to get a standalone Windows
> `.exe` that needs nothing else:
> - **No installs anywhere (recommended):** build it on GitHub's free servers — see
>   **GET_THE_EXE_VIA_GITHUB.md**. Nobody installs Python; you click a button and download
>   the finished `.exe`.
> - **On a Windows PC that has Python:** see **BUILD_WINDOWS_EXE.md**.
> Either way, the finished `.exe` runs on any Windows PC on its own.

---

## What it checks

For each student, against the **handbook edition matching their year of entry**:

1. **Credit floors** — ≥ 90 total credits, ≥ 30 at Level I, ≥ 60 at Levels II/III.
   Exemptions-with-credit (**EC**) count toward these floors.
2. **Named courses** — the specific required courses for the student's programme and
   entry-year era (e.g. Management options-era vs fixed-9 era).
3. **Class of degree** — on the **weighted GPA** (Level I weighted zero; Levels II & III,
   passed courses), per the Faculty regulation. The printed Degree GPA is shown alongside;
   where the two give different classes, the case is flagged for registry confirmation.

Outputs: **Word (.docx)**, **PDF**, and an **Excel** review sheet (full per-student detail).

---

## Requirements

- **Python 3.9+**
- **`pdftotext`** (from Poppler) on your PATH — used to read the PDF.
  - macOS:  `brew install poppler`
  - Ubuntu/Debian:  `sudo apt install poppler-utils`
  - Windows:  install Poppler and add its `bin` folder to PATH
- *(Optional)* **LibreOffice** — if installed, the PDF download is rendered from the Word
  document for identical layout. If not installed, the app falls back to a built-in PDF
  generator (ReportLab) automatically.

---

## Setup

```bash
cd fss_app
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Your browser opens at **http://127.0.0.1:5000**. Upload the BOE PDF, review the on-screen
summary, and download the report in your preferred format. Press `CTRL+C` in the terminal
to stop the app.

---

## Adding programmes or handbook years

You do **not** need to touch the engine. Open **`engine/programmes.py`** and add an entry
to `PROGRAMME_RULES`, following the template at the top of that file. Each programme can
have multiple "eras" keyed by the entry years they apply to. Save and restart the app.

Programmes without a named rule set are screened on credit floors only and clearly flagged
in the output, so nothing is silently passed.

---

## Changing the GPA bands, credit floors, or grade scale

All of these live in one place: **`engine/settings.py`**. Edit the values, save, and restart
the app — every report, the on-screen results, and the spreadsheet update automatically.

- **GPA bands** (class of degree) are **entry-year aware**, edited in `GPA_BAND_RULES`. Each
  rule has a `from_entry_year` and its own `bands` list. A student is classified on the bands
  in force in their year of entry. The app currently ships with two eras:
  First Class Honours is **3.60** for entry up to 2025/2026, and **3.70** for entry from
  **2026/2027** onward (per the regulation change effective August 1, 2026). To add a future
  change, add another rule with a new `from_entry_year`; to adjust a single threshold, edit the
  relevant `min` value. The band-range text in the reports is derived automatically.
- **Credit floors**: edit `CREDIT_FLOORS` (total / Level I / Level II–III minimums).
- **Letter-grade → grade-point scale** (used for the weighted GPA): edit `GRADE_POINTS`.

---

## What it does NOT decide

This is necessary-condition screening to support the examiner, not a replacement for sign-off.
It does not adjudicate: elective-slot counts, the Management 30-credit-Management / 30-elsewhere
split, EX-exemption validity, rate-of-progress limits, BOE annotations, or course
substitutions/waivers. Final determination remains with the Board of Examiners.

---

## Project layout

```
fss_app/
  app.py                 # the web app (run this)
  requirements.txt
  engine/
    parser.py            # reads the BOE PDF into structured records
    programmes.py        # << EDIT to add programmes / years
    settings.py          # << EDIT to change GPA bands, credit floors, grade scale
    requirements.py      # adapter to the registry
    eligibility.py       # credit floors, named-course check, weighted GPA
    weighted_gpa.py      # weighted-GPA computation
    reports.py           # builds the .docx / .pdf / .xlsx
  templates/
    index.html           # upload page
    results.html         # results + downloads
```
