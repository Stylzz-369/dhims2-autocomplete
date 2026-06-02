# DHIMS2 Monthly Dataset Auto-Complete Script

> A Python automation script that marks all DHIS2 datasets as complete for every facility in your district — replacing manual, facility-by-facility clicks with a single double-click.

---

## Background

**DHIS2** (District Health Information Software 2) is the world's largest health management information system, used by governments and health ministries across Africa, Asia, and beyond. In Ghana, it is deployed as **DHIMS2** — the national platform for health facility reporting.

Each month, Health Information Officers (HIOs) are required to mark datasets as "complete" for every facility under their district. In large districts with dozens of facilities and multiple datasets each, this is a repetitive and time-consuming manual process.

This script automates it entirely.

---

## What It Does

1. **Authenticates** to DHIMS2 using your credentials
2. **Fetches** all org units (health facilities) at levels 4 and 5 under your district
3. **Marks every assigned dataset as complete** for the previous calendar month
4. **Prints a live progress report** and saves a log file for your records

---

## Example Output

```
=======================================================
   DHIMS2 Monthly Dataset Auto-Complete
=======================================================

🔐 Checking login credentials...
✅ Logged in as: John Mensah

📅 Target period: May 2026 (202605)

📍 Fetching facilities under your district...
   Level 4: Found 8 org units
   Level 5: Found 31 org units

🏥 Total facilities to process: 39

⏳ Starting completion process...

  [1/39]  ✅  Kintampo South CHPS — 3 completed, 0 failed
  [2/39]  ✅  Jema Health Centre — 5 completed, 0 failed
  [3/39]  ⚠️  Nkoranza Hospital — 4 completed, 1 failed
           FAILED: ANC Dataset — HTTP 409
  ...

=======================================================
   SUMMARY
=======================================================
  Period       : May 2026
  Facilities   : 39
  ✅ Completed : 187 dataset-registrations
  ⏭️  Skipped   : 2 facilities (no datasets)
  ❌ Failed    : 1 dataset-registrations
=======================================================

📄 Log saved to: dhims2_completion_log.txt
```

---

## Requirements

- Python 3.8 or higher — [download here](https://www.python.org/downloads/)
- Internet connection with access to your DHIMS2 instance
- A valid DHIMS2 user account with data entry rights for your district

---

## Installation

**1. Clone or download this repository**

```bash
git clone https://github.com/YOUR_USERNAME/dhims2-autocomplete.git
cd dhims2-autocomplete
```

Or download the ZIP from the green **Code** button above and extract it.

**2. Install dependencies**

```bash
pip install requests python-dateutil
```

> This only needs to be done once.

---

## Configuration

Open `dhims2_autocomplete.py` in any text editor (Notepad, VS Code, etc.) and fill in the three fields in the `CONFIGURATION` section near the top:

```python
DHIMS2_URL           = "https://dhims.chimgh.org/dhims"  # leave as-is for Ghana DHIMS2
USERNAME             = "YOUR_DHIMS2_USERNAME"
PASSWORD             = "YOUR_DHIMS2_PASSWORD"
DISTRICT_ORG_UNIT_ID = "YOUR_DISTRICT_UID"
```

### Finding Your District Org Unit ID

1. Log in to DHIMS2
2. Go to **Maintenance → Organisation Units**
3. Search for your district and click on it
4. Look at the browser address bar — the URL ends with something like:
   ```
   .../organisationUnits/bsSmUnCuJuZ
   ```
5. Copy that last segment (11 characters, letters and numbers) and paste it as your `DISTRICT_ORG_UNIT_ID`

---

## Usage

**Option A — Double-click**

Simply double-click `dhims2_autocomplete.py`. A terminal window will open and the script will run.

**Option B — Command line**

```bash
python dhims2_autocomplete.py
```

### When to Run

The script always targets the **previous calendar month** automatically — no date configuration needed. Run it any time before your district's monthly reporting deadline.

| Run in... | Completes datasets for... |
|-----------|--------------------------|
| June | May |
| July | June |
| August | July |

---

## Output & Logs

Each run appends a timestamped entry to `dhims2_completion_log.txt` in the same folder. Keep this file as a record of all completions.

| Symbol | Meaning |
|--------|---------|
| ✅ | All datasets completed for this facility |
| ⚠️ | Some completed, some failed — check the log |
| ⏭️ | Facility skipped — no datasets assigned in DHIMS2 |
| ❌ | Dataset could not be completed |

---

## Security Note

**Never commit your real credentials to GitHub.**

The configuration section uses placeholder values (`XXXXXXXX`) by default. Fill them in locally on your own machine only. If you accidentally commit real credentials, change your DHIMS2 password immediately and consider the old password compromised.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Script won't open on double-click | Right-click → Open with → Python |
| `Login failed / 401 error` | Check your USERNAME and PASSWORD |
| `No facilities found` | Verify your DISTRICT_ORG_UNIT_ID |
| `ModuleNotFoundError` | Run `pip install requests python-dateutil` |
| `python is not recognized` | Reinstall Python and tick **Add Python to PATH** |
| All datasets failing | Check that DHIMS2 is online and you have internet |

---

## Project Structure

```
dhims2-autocomplete/
├── dhims2_autocomplete.py   # Main script
├── README.md                # This file
└── dhims2_completion_log.txt  # Auto-generated on first run
```

---

## Context & Motivation

This script was built out of a practical need: manually completing datasets for 30+ facilities across multiple datasets every month is error-prone and inefficient. By automating the process via the DHIMS2 REST API, this tool saves significant time and ensures no facility is missed.

It was developed and tested against the Ghana DHIMS2 deployment (`dhims.chimgh.org`), but should work with any standard DHIS2 instance by updating the `DHIMS2_URL` value.

---

## Author

**Stephen Amartey**
Municipal Health Information Officer — Jomoro - Western Region, Ghana Health Service

---

## License

This project is open source and available under the [MIT License](LICENSE).
