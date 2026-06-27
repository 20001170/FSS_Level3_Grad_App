# Get the Windows .exe without installing anything (GitHub cloud build)

This produces a real Windows `.exe` using GitHub's free build servers. **Nobody installs
Python** — not you, not your staff. You upload these files once, click a button, wait a
few minutes, and download the finished `.exe`. After that, staff just double-click it.

You need a free GitHub account. That's the only requirement.

---

## One-time: put the app on GitHub

### Step 1 — Make a free GitHub account
Go to **https://github.com** and sign up (free). Verify your email.

### Step 2 — Create an empty repository ("repo" = a project folder on GitHub)
1. Click the **+** in the top-right of GitHub → **New repository**.
2. Give it a name, e.g. `fss-eligibility`.
3. Leave everything else as-is. You can choose **Private** (only you can see it) — the
   build still works on private repos.
4. Click **Create repository**.

### Step 3 — Upload the app files
1. On the new repo's page, click **uploading an existing file** (the link in the
   "Quick setup" box), or go to **Add file → Upload files**.
2. Open the `fss_app` folder on your computer, select **everything inside it**
   (the `engine` folder, `templates` folder, `.github` folder, `app.py`, etc.) and drag
   it all into the GitHub upload area.
   - **Important:** make sure the hidden **`.github`** folder is included — that's the
     part that tells GitHub how to build. If you don't see it in your file explorer,
     turn on "show hidden files," or use **Add file → Upload files** and drag the whole
     `fss_app` contents in.
3. Scroll down and click **Commit changes**.

---

## Build the .exe (this is the part you repeat whenever the app changes)

### Step 4 — Run the build
1. In your repo, click the **Actions** tab (top of the page).
2. If GitHub asks to enable workflows, click the green **"I understand... enable"** button.
3. On the left, click **Build Windows EXE**.
4. Click the **Run workflow** button on the right → then the green **Run workflow** in the
   little dropdown.
5. Wait. A yellow dot becomes a green check in about 3–5 minutes (refresh if needed).

### Step 5 — Download the .exe
1. Click into the finished run (the row with the green check).
2. Scroll to the bottom to the **Artifacts** section.
3. Click **FSS_Level3_Eligibility_Windows** — it downloads a `.zip`.
4. Unzip it. Inside is **`FSS_Level3_Eligibility.exe`**. That's your app.

---

## Give it to staff

Send them just the one `FSS_Level3_Eligibility.exe` file (email, shared drive, USB —
anything). They **double-click it** — a small black window opens (that's the app; leave
it open) and their browser opens to the app. They upload a BOE PDF and download the
report. Closing the black window stops it.

Nothing else is installed on their machines. Poppler (the PDF reader) is built **inside**
the `.exe` automatically by the cloud build.

---

## First-run note for staff

The first time someone opens the `.exe`, Windows SmartScreen may say *"Windows protected
your PC"* because the file isn't code-signed (normal for in-house tools). Tell staff to
click **More info → Run anyway**. It only asks once per machine.

---

## When you change the app later (e.g. add a programme or change GPA bands)

1. Edit the file on GitHub (or re-upload it via **Add file → Upload files**).
2. Go to **Actions → Build Windows EXE → Run workflow** again.
3. Download the new `.exe` from Artifacts.

That's it — no Python, ever.
