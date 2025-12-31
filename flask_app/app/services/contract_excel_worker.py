import os
import json
import time
import pandas as pd
from datetime import datetime
from ..repositories import contract_repository
from ..repositories.contract_repository import get_unique_items

BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "contracts_data"
)

PENDING = os.path.join(BASE_DIR, "pending")
FAILED = os.path.join(BASE_DIR, "failed")
LOGS = os.path.join(BASE_DIR, "logs")
PROGRESS_FILE = os.path.join(BASE_DIR, "progress.json")
LOCK_FILE = os.path.join(BASE_DIR, ".lock")

def ensure_progress_file():
    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w") as f:
            json.dump({}, f)
def ensure_dirs():
    os.makedirs(PENDING, exist_ok=True)
    os.makedirs(FAILED, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)

def mark_idle():
    progress = load_progress()
    progress["_system"] = {
        "status": "idle",
        "message": "No pending contract files",
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_progress(progress)

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return {}
    with open(PROGRESS_FILE) as f:
        return json.load(f)


def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)

from datetime import datetime

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


def process_excel(filepath):
    filename = os.path.basename(filepath)
    update_file_status(filename, "running")

    inserted = 0
    failed = 0

    try:
        df = pd.read_excel(filepath, engine="openpyxl")
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        contract_fields = [
            'contract_id', 'status', 'organization_type', 'ministry',
            'department', 'organization_name', 'office_zone', 'location',
            'buyer_designation', 'buying_mode', 'bid_number',
            'contract_date', 'total'
        ]

        item_fields = [
            'service', 'category_name', 'product',
            'brand', 'model', 'hsn_code',
            'ordered_quantity', 'price'
        ]

        contract_map = {}

        for _, row in df.iterrows():
            cid = row['contract_id']
            if cid not in contract_map:
                contract_map[cid] = {f: row.get(f) for f in contract_fields}
                contract_map[cid]['items'] = []

            contract_map[cid]['items'].append(
                {f: row.get(f) for f in item_fields}
            )

        for cid, data in contract_map.items():
            try:
                data['items'] = get_unique_items(data['items'])
                if contract_repository.add_contract(data):
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

    # 🔴 STOP if already running
    if is_locked():
        return "locked"

    files = [
        f for f in os.listdir(PENDING)
        if f.endswith((".xls", ".xlsx"))
    ]

    # 🔴 STOP when pending is empty
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
    if is_locked():
        return

    files = sorted(f for f in os.listdir(FAILED) if f.endswith(".xlsx"))
    if not files:
        return

    lock()
    try:
        for f in files:
            process_excel(os.path.join(FAILED, f))
    finally:
        unlock()




# import os
# import json
# import time
# import pandas as pd
# from datetime import datetime
# from ..repositories import contract_repository
# from ..repositories.contract_repository import get_unique_items

# def ensure_directories():
#     os.makedirs(BASE_DIR, exist_ok=True)
#     os.makedirs(PENDING, exist_ok=True)
#     os.makedirs(FAILED, exist_ok=True)
#     os.makedirs(LOGS, exist_ok=True)


# BASE_DIR = "contracts_data"
# PENDING = f"{BASE_DIR}/pending"
# FAILED = f"{BASE_DIR}/failed"
# LOGS = f"{BASE_DIR}/logs"
# LOCK_FILE = f"{BASE_DIR}/.lock"


# def _locked():
#     return os.path.exists(LOCK_FILE)


# def _lock():
#     with open(LOCK_FILE, "w") as f:
#         f.write(str(os.getpid()))


# def _unlock():
#     if os.path.exists(LOCK_FILE):
#         os.remove(LOCK_FILE)


# def _write_log(name, log):
#     path = os.path.join(LOGS, name)
#     with open(path, "w") as f:
#         json.dump(log, f, indent=2)


# def _process_excel(filepath, source):
#     filename = os.path.basename(filepath)
#     log_name = f"{filename}_{source}_{int(time.time())}.json"

#     log = {
#         "file": filename,
#         "source": source,
#         "started_at": str(datetime.utcnow()),
#         "status": "running",
#         "inserted": 0,
#         "failed": []
#     }

#     try:
#         df = pd.read_excel(filepath, engine="openpyxl")
#         df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

#         contract_fields = [
#             'contract_id', 'status', 'organization_type', 'ministry',
#             'department', 'organization_name', 'office_zone', 'location',
#             'buyer_designation', 'buying_mode', 'bid_number',
#             'contract_date', 'total'
#         ]

#         item_fields = [
#             'service', 'category_name', 'product',
#             'brand', 'model', 'hsn_code',
#             'ordered_quantity', 'price'
#         ]

#         contract_map = {}

#         for _, row in df.iterrows():
#             cid = row['contract_id']
#             if cid not in contract_map:
#                 contract_map[cid] = {f: row.get(f) for f in contract_fields}
#                 contract_map[cid]['items'] = []

#             contract_map[cid]['items'].append(
#                 {f: row.get(f) for f in item_fields}
#             )

#         for cid, data in contract_map.items():
#             try:
#                 data['items'] = get_unique_items(data['items'])
#                 if contract_repository.add_contract(data):
#                     log["inserted"] += 1
#             except Exception as e:
#                 log["failed"].append({
#                     "contract_id": cid,
#                     "error": str(e)
#                 })

#         log["status"] = "completed"
#         log["ended_at"] = str(datetime.utcnow())
#         _write_log(log_name, log)

#         # ✅ SUCCESS → DELETE FILE
#         os.remove(filepath)

#     except Exception as e:
#         log["status"] = "failed"
#         log["error"] = str(e)
#         _write_log(log_name, log)


# def process_next_pending():
#     ensure_directories()
#     if _locked():
#         return "locked"

#     files = sorted(f for f in os.listdir(PENDING) if f.endswith((".xlsx", ".xls")))
#     if not files:
#         return "no_pending"

#     _lock()
#     try:
#         _process_excel(os.path.join(PENDING, files[0]), "pending")
#         return "done"
#     finally:
#         _unlock()


# def process_next_failed():
#     ensure_directories()
#     if _locked():
#         return "locked"

#     files = sorted(f for f in os.listdir(FAILED) if f.endswith((".xlsx", ".xls")))
#     if not files:
#         return "no_failed"

#     _lock()
#     try:
#         _process_excel(os.path.join(FAILED, files[0]), "failed")
#         return "reprocessed"
#     finally:
#         _unlock()
