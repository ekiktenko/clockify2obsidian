# ------------------------- DEPENDENCIES -------------------------
import requests
import os
import re
import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo  # Requires Python 3.9+
# ---------------------------------------------------------------

# ------------------------- LOAD CONFIG -------------------------
# Reads user configuration from a local JSON file.
# This allows adjusting behavior without editing the code.
with open('clockify_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

API_KEY = config['api_key']              # Clockify API key
VAULT_PATH = config['vault_path']        # Path to daily Obsidian files
DAYS_BACK = config['days_back']          # How many past days to process
TIME_ZONE = config['time_zone']          # IANA time zone (e.g., Europe/Moscow)
# ---------------------------------------------------------------


# ---------- Utility: Convert local day to UTC time window ----------
def get_utc_params_for_day(date_str: str, tz_name: str = TIME_ZONE) -> dict:
    """Returns UTC 'start' and 'end' timestamps for a given local date."""
    local_tz = ZoneInfo(tz_name)
    day_start = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=local_tz)
    day_end = day_start + timedelta(days=1) - timedelta(seconds=1)
    return {
        "start": day_start.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "end": day_end.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


# ---------- Utility: Parse ISO8601 duration to hh:mm:ss ----------
def parse_duration(duration_str: str) -> str:
    """Converts ISO 8601 duration like 'PT1H7M23S' to '01:07:23'."""
    if not duration_str:
        return "00:00:00"
    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if not match:
        return duration_str
    h, m, s = (int(x) if x else 0 for x in match.groups())
    return f"{h:02d}:{m:02d}:{s:02d}"


# ---------- Get user and workspace ID from API key ----------
def get_clockify_ids(api_key: str) -> tuple:
    """Fetches user_id and active workspace_id from Clockify account."""
    headers = {"X-Api-Key": api_key}
    resp = requests.get("https://api.clockify.me/api/v1/user", headers=headers)
    if resp.status_code != 200:
        raise Exception("❌ Invalid API key or network issue.")
    data = resp.json()
    return data["id"], data["activeWorkspace"]


# ---------- Init Clockify session ----------
USER_ID, WORKSPACE_ID = get_clockify_ids(API_KEY)
HEADERS = {"X-Api-Key": API_KEY}

# ---------- Load project and task names ----------
projects_url = f"https://api.clockify.me/api/v1/workspaces/{WORKSPACE_ID}/projects"
project_resp = requests.get(projects_url, headers=HEADERS)
project_names = {p["id"]: p["name"] for p in project_resp.json()}

task_names = {}
for project_id in project_names:
    task_url = f"https://api.clockify.me/api/v1/workspaces/{WORKSPACE_ID}/projects/{project_id}/tasks"
    task_resp = requests.get(task_url, headers=HEADERS)
    if task_resp.status_code == 200:
        for task in task_resp.json():
            task_names[task["id"]] = task["name"]

# ---------- Process each day ----------
now = datetime.now(ZoneInfo(TIME_ZONE))
for i in range(DAYS_BACK):
    day = now - timedelta(days=i)
    date_str = day.strftime("%Y-%m-%d")
    local_day = day.strftime("%d.%m.%Y")
    filename = os.path.join(VAULT_PATH, f"{date_str}.md")

    # Ensure parent directories exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Get entries for the day
    params = get_utc_params_for_day(date_str)
    url = f"https://api.clockify.me/api/v1/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries"
    response = requests.get(url, headers=HEADERS, params=params)
    entries = response.json()

    if not entries:
        continue  # Skip if no entries

    # ---------- Format Clockify block ----------
    block_lines = ["> [!clockify] Clockify time log"]
    total_duration = timedelta()

    for entry in entries:
        project = project_names.get(entry.get("projectId"), "No project")
        task = task_names.get(entry.get("taskId"), "No task")
        raw_duration = entry.get("timeInterval", {}).get("duration") or ""
        duration = parse_duration(raw_duration)
        comment = entry.get("description", "").strip()

        # Accumulate total time
        match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", raw_duration)
        if match:
            h, m, s = (int(x) if x else 0 for x in match.groups())
            total_duration += timedelta(hours=h, minutes=m, seconds=s)

        # Convert start time to local timezone
        start = entry.get("timeInterval", {}).get("start")
        if start:
            start_utc = datetime.fromisoformat(start.replace("Z", "+00:00")).replace(tzinfo=timezone.utc)
            dt = start_utc.astimezone(ZoneInfo(TIME_ZONE))
            time_str = dt.strftime("%H:%M")
        else:
            time_str = "??:??"

        line = f"> {project} - {task}: {duration} ({time_str}"
        if comment:
            line += f"|{comment}"
        line += ")"
        block_lines.append(line)

    # ---------- Inject block into Obsidian file ----------
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = f"# {local_day}\n\n"

    # Remove existing clockify block
    lines = content.splitlines()
    new_lines = []
    inside_block = False
    for line in lines:
        if line.startswith("> [!clockify]"):
            inside_block = True
            continue
        if inside_block and line.startswith("> "):
            continue
        inside_block = False
        new_lines.append(line)

    # Append updated block
    new_lines.append("")  # blank line
    new_lines.extend(block_lines)

    # Write back to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print(f"✅ Updated {filename}")
    print(f"🕒 {date_str} — total: {str(total_duration)}")