# Keeping the app current when handbooks change

This guide explains how to update programme rules for future entry years. It is
written for a non-programmer: every change is a small, copy-and-paste edit to one
file, and the app's entry-year logic does the rest.

---

## The key idea: students are held to their ENTRY-YEAR rules

The app already records each student's year of entry and checks them against the
rules in force **for that year**. So when a programme changes for a new intake,
you don't rewrite anything — you **add** a new rule "era" for the new entry years,
and leave the old one in place for students who entered earlier.

You have already seen this work: the First Class threshold changed from 3.60 to
3.70 for students entering 2026/2027, and both rules coexist.

There are two files you might edit, both in the `engine` folder:

- **`settings.py`** — GPA bands, credit floors, grade scale (entry-year aware).
- **`programmes.py`** — each programme's required courses (entry-year aware).

The bundled handbooks (in the `handbooks` folder) are your reference when doing
this — open the relevant year to confirm what changed.

---

## Example A — a GPA band changes for a future year

Already done for First Class 3.70. To add another future change, open
`settings.py`, find `GPA_BAND_RULES`, and add a block like:

```python
{
    "from_entry_year": "2028/2029",   # applies to entry 2028/29 and later
    "label": "2028/29 onward",
    "bands": [
        {"min": 3.70, "label": "First Class Honours"},
        {"min": 3.00, "label": "Upper Second Class Honours"},
        {"min": 2.50, "label": "Lower Second Class Honours"},
        {"min": 2.00, "label": "Pass"},
    ],
},
```

Save, restart the app. Students entering 2028/29+ use the new bands; everyone else
keeps theirs.

---

## Example B — a programme's required courses change for a future intake

Say the handbook for 2027/2028 changes the Accounting & Finance core. Open
`programmes.py`, find the `"Accounting & Finance"` entry. Today it looks like:

```python
"Accounting & Finance": [
    {"era": "stable", "years": "ALL",
     "level1_fixed": ACCT_FIN_L1, "level1_either_or": ACCT_FIN_L1_EITHER,
     "level23_named": ACCT_FIN_L23, "notes": "..."},
],
```

To introduce a change for 2027/28 entrants while keeping the old rule for everyone
before, split the single "ALL" era into two year-bounded eras:

```python
"Accounting & Finance": [
    {"era": "pre-2027", "years": "<=2026/2027",
     "level1_fixed": ACCT_FIN_L1, "level1_either_or": ACCT_FIN_L1_EITHER,
     "level23_named": ACCT_FIN_L23, "notes": "Original structure."},
    {"era": "2027 onward", "years": ">=2027/2028",
     "level1_fixed": ACCT_FIN_L1_2027, "level1_either_or": ACCT_FIN_L1_EITHER,
     "level23_named": ACCT_FIN_L23_2027, "notes": "Revised per 2027/28 handbook."},
],
```

…where `ACCT_FIN_L1_2027` / `ACCT_FIN_L23_2027` are new course sets you define
just above (copy the existing ones and edit the courses that changed).

The `years` field accepts:
- `"ALL"` — applies to every entry year (the default for unchanging programmes)
- `"<=2026/2027"` — that year and earlier
- `">=2027/2028"` — that year and later
- `"2022/2023"` — exactly that year

---

## Adding a brand-new programme

Copy any existing programme block, give it the new BOE label as its key, define its
Level I / Level II-III course sets, and (if it belongs to a department) add it to
`engine/department_map.py`. The template at the top of `programmes.py` shows every
available option (fixed courses, either/or groups, minors, credit-only).

---

## The honest part: why this is a manual edit, not an automatic import

The course requirements in this app were not simply copied out of the handbook —
they were **derived and validated** against hundreds of real student records, to
tell genuinely-required courses apart from "choose some of these" pools, catch
two-column layout scrambles, and make sure complete students were never wrongly
failed. An automatic "import this handbook" button would produce plausible-looking
but subtly wrong rules — exactly the risk you want to avoid for a live tool.

So the reliable workflow when a programme changes is:
1. Open the new handbook (bundled in `handbooks/`) and the affected programme.
2. Identify what actually changed (usually one or two courses, for a few programmes).
3. Add a year-bounded era as in Example B, and save.
4. Run a known record and confirm the affected students still resolve sensibly.

In practice this is a small job a few programmes at a time, not a yearly rewrite of
all 58. If handbook changes ever become frequent enough to justify it, a
"draft-and-confirm" import helper (that proposes changes for a human to approve)
can be added later — but the manual era-addition above is what keeps the answers
correct.
