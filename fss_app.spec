# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for the FSS Level 3 Eligibility app.
# Produces a single-file Windows executable that needs no Python install.
#
# Build with:  pyinstaller fss_app.spec    (or just run build_exe.bat)
#
import os

block_cipher = None

# Bundle data files: the HTML templates, and (if present) a poppler/ folder
# placed next to this spec so pdftotext travels inside the exe.
datas = [
    ("templates", "templates"),
]
if os.path.isdir("static"):
    datas.append(("static", "static"))
if os.path.isdir("poppler"):
    datas.append(("poppler", "poppler"))
if os.path.isdir("handbooks"):
    datas.append(("handbooks", "handbooks"))

# Make sure Flask/Jinja and the report libraries are fully pulled in.
hiddenimports = [
    "flask", "jinja2", "werkzeug",
    "openpyxl", "docx", "reportlab",
    "engine", "engine.parser", "engine.eligibility", "engine.weighted_gpa",
    "engine.requirements", "engine.programmes", "engine.reports", "engine.settings",
    "engine.department_map", "engine.analytics", "engine.summary_reports",
    "engine.storage", "engine.storage_config",
]

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy.tests"],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="FSS_Level3_Eligibility",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,          # keep a console window so messages/errors are visible
    disable_windowed_traceback=False,
    icon=None,
)
