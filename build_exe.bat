@echo off
REM ===========================================================================
REM  Build the standalone Windows executable for the FSS Level 3 Eligibility app.
REM
REM  Run this ONCE on a Windows PC that has Python installed. It produces:
REM        dist\FSS_Level3_Eligibility.exe
REM  which then runs on any Windows PC with NO Python needed.
REM
REM  The window stays open at the end so you can read the result.
REM ===========================================================================
cd /d "%~dp0"
echo.
echo ==========================================================
echo   Building FSS Level 3 Eligibility .exe
echo ==========================================================
echo.

REM --- 1. Check Python is available -----------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
  echo [X] Python was not found.
  echo     Install it from https://www.python.org/downloads/ and make sure you
  echo     tick "Add python.exe to PATH" during setup, then run this again.
  echo.
  pause
  exit /b 1
)
echo [OK] Python found:
python --version
echo.

REM --- 2. Install build + app dependencies ----------------------------------
echo Installing build tools and dependencies (first time only)...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install --quiet pyinstaller flask openpyxl python-docx reportlab
if errorlevel 1 (
  echo [X] Could not install dependencies. Check your internet connection.
  echo.
  pause
  exit /b 1
)
echo [OK] Dependencies ready.
echo.

REM --- 3. Bundle Poppler if it is present ------------------------------------
if exist "poppler\bin\pdftotext.exe" (
  echo [OK] Poppler found in poppler\bin - it will be bundled into the .exe.
) else (
  echo [!] NOTE: no poppler\bin\pdftotext.exe found.
  echo     The app reads PDFs using Poppler's pdftotext. To bundle it so the .exe
  echo     is fully self-contained:
  echo       1. Download poppler-windows from
  echo          https://github.com/oschwartz10612/poppler-windows/releases
  echo       2. Unzip it, and copy its inner "Library" folder contents so that
  echo          this path exists:   %~dp0poppler\bin\pdftotext.exe
  echo       3. Run this build again.
  echo     You can still build now; users would then need Poppler on their PATH.
  echo.
  choice /m "Continue building without bundling Poppler"
  if errorlevel 2 (
    echo Build cancelled.
    echo.
    pause
    exit /b 1
  )
)
echo.

REM --- 4. Build -------------------------------------------------------------
echo Building the executable (this can take a couple of minutes)...
pyinstaller --clean --noconfirm fss_app.spec
if errorlevel 1 (
  echo.
  echo [X] The build failed. Scroll up to read the error.
  echo.
  pause
  exit /b 1
)

echo.
echo ==========================================================
echo   DONE.
echo   Your app is here:   dist\FSS_Level3_Eligibility.exe
echo   Double-click it to run. No Python needed from now on.
echo ==========================================================
echo.
pause
