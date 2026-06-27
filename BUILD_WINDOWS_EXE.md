# Building the standalone Windows .exe

This makes a single `FSS_Level3_Eligibility.exe` that runs on any Windows PC with
**no Python and no setup**. You build it once; after that you (and colleagues) just
double-click the `.exe`.

You only need Python for the **build** step — not for running the finished `.exe`.

---

## What you need once, to build

1. **Python** installed (tick *"Add python.exe to PATH"* in the installer).
2. **Poppler for Windows** (optional but recommended — it lets the `.exe` read PDFs
   with nothing else installed). Steps below.

---

## Step 1 — (Recommended) add Poppler so it's bundled inside the .exe

1. Download the latest Poppler build for Windows:
   **https://github.com/oschwartz10612/poppler-windows/releases**
   (download the file named like `Release-24.08.0-0.zip`).
2. Unzip it. Inside you'll find a folder structure ending in `...\Library\bin`
   that contains `pdftotext.exe`.
3. In **this** app folder (the one with `build_exe.bat`), create a folder called
   `poppler`, and inside it a folder called `bin`, and copy everything from Poppler's
   `Library\bin` into it. The result must be:

   ```
   fss_app\
     poppler\
       bin\
         pdftotext.exe
         (and the .dll files that came with it)
   ```

   If you skip this, the `.exe` still builds, but each PC that runs it will need
   Poppler installed and on its PATH.

## Step 2 — Build

Double-click **`build_exe.bat`** (or run it from a Command Prompt). It will:

- check Python is present,
- install the build tool (PyInstaller) and the app's libraries,
- bundle the app + Python + (if present) Poppler,
- produce **`dist\FSS_Level3_Eligibility.exe`**.

The window stays open at the end and tells you where the file is.

## Step 3 — Use it

Double-click **`dist\FSS_Level3_Eligibility.exe`**. A small black console window opens
(that's the app running — leave it open), and your browser opens to the app. Upload a
BOE PDF, review, and download the report. Close the console window to stop the app.

To share it with a colleague, send them just that one `.exe` file. If you bundled
Poppler, they need nothing else.

---

## Notes

- The first time you run the `.exe`, Windows SmartScreen may warn that it's from an
  unknown publisher (because it isn't code-signed). Click **More info → Run anyway**.
  This is normal for in-house tools.
- Antivirus software occasionally flags freshly-built PyInstaller `.exe` files. If that
  happens, allow/whitelist it — it's a false positive common to all PyInstaller apps.
- The `.exe` is larger (tens of MB) than the source folder because it carries Python
  and the libraries inside it. That's expected and is what makes it self-contained.
