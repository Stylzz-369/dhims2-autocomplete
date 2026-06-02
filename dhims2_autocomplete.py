"""
DHIMS2 Monthly Dataset Auto-Complete Script
============================================
This script automatically marks all datasets as complete
for all facilities under your district in DHIMS2.

HOW TO USE:
1. Fill in your details in the CONFIGURATION section below
2. Double-click this file to run (after installing Python)
3. Check the summary report printed at the end

REQUIREMENTS:
- Python 3.8 or higher (https://www.python.org/downloads/)
- Run this once in terminal/cmd to install dependencies:
    pip install requests
"""

import requests
import json
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# ============================================================
#   CONFIGURATION — Fill in your details here
# ============================================================

DHIMS2_URL      = "https://dhims.chimgh.org/dhims"   # Do not add trailing slash
USERNAME        = "XXXXXXXX"            # Your DHIMS2 username
PASSWORD        = "XXXXXXXX"            # Your DHIMS2 password
DISTRICT_ORG_UNIT_ID = "XXXXXXXXXXX"    # Your district UID (see instructions below)

# ============================================================
#   HOW TO FIND YOUR DISTRICT ORG UNIT ID:
#   1. Log into DHIMS2
#   2. Go to: Maintenance > Organisation Units
#   3. Search for your district
#   4. Click on it — the URL will show something like:
#      .../organisationUnits/AbCdEfGhIjK
#   5. Copy that last part (e.g. AbCdEfGhIjK) and paste above
# ============================================================

# ============================================================
#   ADVANCED SETTINGS (no need to change these)
# ============================================================

FACILITY_LEVELS = [4, 5]          # Sub-district and Facility levels
LOG_FILE        = "dhims2_completion_log.txt"

# ============================================================
#   SCRIPT — Do not edit below this line
# ============================================================

session = requests.Session()
session.auth = (USERNAME, PASSWORD)
session.headers.update({"Content-Type": "application/json"})

BASE = DHIMS2_URL + "/api"


def get_last_month_period():
    """Returns last month in DHIMS2 format e.g. 202504"""
    today = date.today()
    first_of_this_month = today.replace(day=1)
    last_month = first_of_this_month - relativedelta(months=1)
    return last_month.strftime("%Y%m")


def get_facilities():
    """Fetch all org units at levels 4 and 5 under the district"""
    print("\n📍 Fetching facilities under your district...")
    all_facilities = []
    for level in FACILITY_LEVELS:
        url = (
            f"{BASE}/organisationUnits"
            f"?filter=path:like:{DISTRICT_ORG_UNIT_ID}"
            f"&filter=level:eq:{level}"
            f"&fields=id,name,level,dataSets[id,name]"
            f"&paging=false"
        )
        resp = session.get(url)
        resp.raise_for_status()
        units = resp.json().get("organisationUnits", [])
        all_facilities.extend(units)
        print(f"   Level {level}: Found {len(units)} org units")
    return all_facilities


def mark_complete(dataset_id, org_unit_id, period):
    """Mark a single dataset complete for an org unit and period"""
    url = f"{BASE}/completeDataSetRegistrations"
    payload = {
        "completeDataSetRegistrations": [
            {
                "dataSet": dataset_id,
                "organisationUnit": org_unit_id,
                "period": period,
                "completed": True
            }
        ]
    }
    resp = session.post(url, data=json.dumps(payload))
    if resp.status_code in [200, 201, 204]:
        return True, None
    else:
        try:
            error = resp.json()
            msg = error.get("message") or error.get("description") or str(error)
        except Exception:
            msg = f"HTTP {resp.status_code}"
        return False, msg


def run():
    print("=" * 55)
    print("   DHIMS2 Monthly Dataset Auto-Complete")
    print("=" * 55)

    # --- Validate login ---
    print("\n🔐 Checking login credentials...")
    me = session.get(f"{BASE}/me")
    if me.status_code == 401:
        print("❌ Login failed. Please check your username and password.")
        input("\nPress Enter to exit...")
        return
    user_info = me.json()
    print(f"✅ Logged in as: {user_info.get('displayName', USERNAME)}")

    # --- Determine period ---
    period = get_last_month_period()
    period_display = datetime.strptime(period, "%Y%m").strftime("%B %Y")
    print(f"\n📅 Target period: {period_display} ({period})")

    # --- Fetch facilities ---
    facilities = get_facilities()
    if not facilities:
        print("\n⚠️  No facilities found. Please check your DISTRICT_ORG_UNIT_ID.")
        input("\nPress Enter to exit...")
        return

    total_facilities = len(facilities)
    print(f"\n🏥 Total facilities to process: {total_facilities}")

    # --- Mark complete ---
    print("\n⏳ Starting completion process...\n")

    success_count = 0
    skip_count = 0
    fail_count = 0
    log_lines = [f"DHIMS2 Auto-Complete Log — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                 f"Period: {period_display}", "=" * 55]

    for i, facility in enumerate(facilities, 1):
        fname = facility.get("name", "Unknown")
        fid   = facility["id"]
        datasets = facility.get("dataSets", [])

        if not datasets:
            print(f"  [{i}/{total_facilities}] ⏭️  {fname} — no datasets assigned, skipping")
            log_lines.append(f"SKIP | {fname} | No datasets")
            skip_count += 1
            continue

        fac_success = 0
        fac_fail = 0
        fail_details = []
        for ds in datasets:
            ok, err = mark_complete(ds["id"], fid, period)
            if ok:
                fac_success += 1
                success_count += 1
            else:
                fac_fail += 1
                fail_count += 1
                fail_details.append(f"    FAILED: {ds['name']} — {err}")

        status = "✅" if fac_fail == 0 else "⚠️ "
        print(f"  [{i}/{total_facilities}] {status} {fname} — {fac_success} completed, {fac_fail} failed")
        for detail in fail_details:
            print(detail)
        log_lines.append(f"{'OK' if fac_fail==0 else 'PARTIAL'} | {fname} | {fac_success} ok, {fac_fail} failed")
        for detail in fail_details:
            log_lines.append(detail)

    # --- Summary ---
    print("\n" + "=" * 55)
    print("   SUMMARY")
    print("=" * 55)
    print(f"  Period       : {period_display}")
    print(f"  Facilities   : {total_facilities}")
    print(f"  ✅ Completed : {success_count} dataset-registrations")
    print(f"  ⏭️  Skipped   : {skip_count} facilities (no datasets)")
    print(f"  ❌ Failed    : {fail_count} dataset-registrations")
    print("=" * 55)

    # --- Save log ---
    log_lines += [
        "",
        f"Total facilities : {total_facilities}",
        f"Completed        : {success_count}",
        f"Skipped          : {skip_count}",
        f"Failed           : {fail_count}",
    ]
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n\n")
    print(f"\n📄 Log saved to: {LOG_FILE}")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    # Check for dateutil
    try:
        from dateutil.relativedelta import relativedelta
    except ImportError:
        print("Installing required package (python-dateutil)...")
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dateutil"])
        from dateutil.relativedelta import relativedelta

    run()
