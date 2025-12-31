import os
import json
import pandas as pd
from datetime import datetime
import re

from ..repositories import seller_repository

# BASE_DIR = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), "..", "..", "contracts_data", "sellers")
# )
BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),  # app/services
        "..",                       # app
        "..",                       # project root
        "seller_data"               # ✅ NEW FOLDER NAME
    )
)

PENDING = os.path.join(BASE_DIR, "pending")
FAILED = os.path.join(BASE_DIR, "failed")
LOGS = os.path.join(BASE_DIR, "logs")
PROGRESS_FILE = os.path.join(BASE_DIR, "progress.json")
LOCK_FILE = os.path.join(BASE_DIR, ".lock")


# ----------------- helpers -----------------

def ensure_dirs():
    os.makedirs(PENDING, exist_ok=True)
    os.makedirs(FAILED, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)

def mark_idle():
    progress = load_progress()
    progress["_system"] = {
        "status": "idle",
        "message": "No pending seller files",
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_progress(progress)

def ensure_progress_file():
    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w") as f:
            json.dump({}, f)


def load_progress():
    ensure_progress_file()
    with open(PROGRESS_FILE) as f:
        return json.load(f)


def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def update_file_status(filename, status, inserted=0, failed=0):
    progress = load_progress()

    if filename not in progress:
        progress[filename] = {}

    progress[filename].update({
        "status": status,
        "inserted": inserted,
        "failed": failed,
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    })

    save_progress(progress)


def is_locked():
    return os.path.exists(LOCK_FILE)


def lock():
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def unlock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


# ----------------- core logic -----------------

def clean_column_name(c):
    c = c.strip().lower()
    c = c.replace(" ", "_")
    c = re.sub(r"[^\w]", "", c)
    return c


def process_excel(filepath):
    filename = os.path.basename(filepath)
    update_file_status(filename, "running")

    inserted = 0
    failed = 0

    try:
        df = pd.read_excel(filepath, engine="openpyxl")
        df.columns = [clean_column_name(c) for c in df.columns]

        seller_fields = [
            "contract_no", "generated_date", "category_name",
            "seller_id", "company_name", "contact_no",
            "email", "address", "msme_reg_no", "gstin"
        ]

        for _, row in df.iterrows():
            try:
                data = {f: row.get(f) for f in seller_fields}
                if seller_repository.add_or_update_seller(data):
                    inserted += 1
            except Exception:
                failed += 1

        update_file_status(filename, "completed", inserted, failed)
        os.remove(filepath)

    except Exception:
        update_file_status(filename, "failed", inserted, failed)
        os.rename(filepath, os.path.join(FAILED, filename))


def process_next_pending():
    ensure_dirs()
    ensure_progress_file()

    #  STOP if already running
    if is_locked():
        return "locked"

    files = [
        f for f in os.listdir(PENDING)
        if f.endswith((".xls", ".xlsx"))
    ]

    #  STOP when pending is empty
    if not files:
        mark_idle()
        print("NO PENDING FILES — PROCESS STOPPED")
        return "no_pending"

    lock()
    try:
        process_excel(os.path.join(PENDING, files[0]))
        return "processed"
    finally:
        unlock()



def retry_all_failed():
    ensure_dirs()
    ensure_progress_file()

    if is_locked():
        return

    files = sorted(f for f in os.listdir(FAILED) if f.endswith((".xls", ".xlsx")))
    if not files:
        return

    lock()
    try:
        for f in files:
            process_excel(os.path.join(FAILED, f))
    finally:
        unlock()
