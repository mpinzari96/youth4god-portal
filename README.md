# Youth for God – Conference Dashboard

A simple Streamlit dashboard for viewing and filtering conference registration data.

---

## 📁 Files in this repo

```
your-repo/
├── app.py               ← the dashboard
├── requirements.txt     ← Python dependencies
└── registrations.csv    ← the registration data (rename your CSV to this)
```

---

## 🚀 How to Deploy on Streamlit Community Cloud (Free)

### Step 1 – Create a GitHub repo

1. Go to [github.com](https://github.com) and sign in (or create a free account).
2. Click **"New repository"** → give it a name like `yfg-dashboard`.
3. Set it to **Private** (keeps your attendee data off public internet).
4. Click **Create repository**.

### Step 2 – Upload the files

In your new repo, click **"Add file → Upload files"** and drag in:
- `app.py`
- `requirements.txt`
- Your CSV file — **rename it to `registrations.csv`** before uploading

Commit the upload.

### Step 3 – Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.
2. Click **"New app"**.
3. Pick your repo (`yfg-dashboard`), branch (`main`), and set **Main file path** to `app.py`.
4. Click **Deploy!** — it usually takes about 60 seconds.
5. You'll get a public URL like `https://your-app-name.streamlit.app` to share with leaders.

---

## 🔄 How to Update When New Registrations Come In

### Option A – Replace the CSV directly on GitHub (easiest)

1. Open your GitHub repo.
2. Click on `registrations.csv`.
3. Click the **pencil/edit icon** → then **"Upload a file"** (or use the GitHub web editor).
4. Upload your new CSV (still named `registrations.csv`).
5. Commit the change.
6. Streamlit Cloud **auto-detects the change and redeploys in ~30 seconds** — no action needed.

### Option B – Use the in-app uploader (no GitHub needed)

The dashboard has a **"Upload updated CSV"** button in the left sidebar.
- Any leader with access to the app URL can upload a fresh CSV on the fly.
- This is session-only (not permanent), but great for quick checks.

---

## 🔒 Keeping Data Private

- Keep the GitHub repo **Private**.
- On Streamlit Cloud, go to your app settings → **"Sharing"** → choose **"Only specific people"** and invite leaders by email.
- This way only your team can see the attendee data.

---

## 🗂️ Column Mapping (what the CSV columns mean in the app)

| App Column | CSV Column |
|---|---|
| Full Name | First name + Last name |
| Email | Email |
| Phone | Phone number |
| Church | What church are you from? |
| Ticket Type | Ticket type |
| Price | Ticket price |
| Payment Status | Payment status (`success` = paid, `transfer pending` = yellow row) |
| Primary Contact | Primary Contact Name |
| Primary Email | Primary Contact Email |
| Party Size | Auto-calculated from Party ID |

---

## 🛠️ Troubleshooting

**"File not found" error on deploy:**
Make sure your CSV is named exactly `registrations.csv` in the repo root.

**State dropdown shows duplicates:**
The app normalises states automatically (e.g. "California", "CA", "Ca" → all become "CA"). If you see a new odd value, add it to the `STATE_MAP` dictionary in `app.py`.

**App shows blank / no rows:**
The raw CSV has sub-rows (group total rows with blank First name). The app filters those out automatically — this is expected.
