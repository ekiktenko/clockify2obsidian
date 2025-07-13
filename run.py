from parse_funcs import parse_duration, get_utc_params_for_moscow_day

import requests
import json
from datetime import datetime, timedelta, timezone

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

API_KEY = config['api_key']
WORKSPACE_ID = config['workspace_id']
USER_ID = config['user_id']

OUTPUT_FILE = 'clockify_export.md'


headers = {"X-Api-Key": API_KEY}

# Getting project names
projects_url = f"https://api.clockify.me/api/v1/workspaces/{WORKSPACE_ID}/projects"
projects_resp = requests.get(projects_url, headers=headers)
project_names = {p["id"]: p["name"] for p in projects_resp.json()}


# Getting tasks for projects
task_names = {}

for project_id in project_names.keys():
    task_url = f"https://api.clockify.me/api/v1/workspaces/{WORKSPACE_ID}/projects/{project_id}/tasks"
    task_resp = requests.get(task_url, headers=headers)

    if task_resp.status_code == 200:
        for task in task_resp.json():
            task_names[task["id"]] = task["name"]

# Параметры периода
date_str = '2025-07-12'
params = get_utc_params_for_moscow_day(date_str)

# Загружаем time entries
time_url = f'https://api.clockify.me/api/v1/workspaces/{WORKSPACE_ID}/user/{USER_ID}/time-entries'
response = requests.get(time_url, headers=headers, params=params)
data = response.json()


# Формируем Markdown
lines = ["> [!clockify] Clockify time log"]

for entry in data[::-1]:
    description = entry.get("description", "Без описания")
    if description:
        description = "|" + description

    project_id = entry.get("projectId")
    project_name = project_names.get(project_id, "Без проекта")

    task_id = entry.get("taskId")
    task_name = task_names.get(task_id, "Без задачи")

    start = entry["timeInterval"]["start"]
    duration = entry["timeInterval"].get("duration", "")

    start_dt = datetime.fromisoformat(start[:-1]) + timedelta(hours=3)
    start_str = start_dt.strftime("%H:%M")

    lines.append(
        f"> {project_name} - {task_name}: {parse_duration(duration)} ({start_str}{description})"
    )

# Сохраняем
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"✅ Сохранено в {OUTPUT_FILE}")