"""
=============================================================================
  STORAGE CONFIG  --  where the multi-year history database lives
=============================================================================

By default the app keeps its history in a local 'data/history.db' next to the
program. To share ONE history across several staff, put the database on a shared
network drive everyone can reach, by setting FSS_DB_PATH below to that location.

Examples (uncomment and edit ONE):

# Windows shared drive:
# FSS_DB_PATH = r"S:\\FSS\\eligibility\\history.db"

# Windows UNC path (no mapped drive letter needed):
# FSS_DB_PATH = r"\\\\server\\FSS\\eligibility\\history.db"

# Mac / Linux mounted share:
# FSS_DB_PATH = "/Volumes/FSS/eligibility/history.db"

If the chosen location can't be reached when the app runs, it automatically falls
back to the local copy and shows a note, so it never fails just because the share
is temporarily offline.
"""

# Leave as None to use the local default. Set to a path string to use a shared DB.
FSS_DB_PATH = None
