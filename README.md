# ⏱ Clockify → Obsidian

A Python script to sync time tracking entries from [Clockify](https://clockify.me/) into your daily [Obsidian](https://obsidian.md/) Markdown daily notes.

---

## 📌 What it does

- Fetches time entries from Clockify for the last N days
- Formats them into a collapsible Obsidian callout block:
  ```
  > [!clockify] Clockify time log
  > Project - Task: 01:15:33 (14:22|Optional comment)
  ```
- Inserts or updates the block inside daily `.md` notes
- Converts UTC to your specified time zone (e.g. `Europe/Moscow`)

---

## 🚀 Setup

1. Make sure you have Python 3.9+ installed.
2. Clone this repository:
   ```bash
   git clone https://github.com/ekiktenko/clockify2obsidian.git
   cd clockify2obsidian
   ```
3. Install dependencies:
   ```bash
   pip install requests
   ```

---

## ⚙️ Configuration

1. Copy the example config:
   ```bash
   cp clockify_config.example.json clockify_config.json
   ```
2. Edit `clockify_config.json`:
   ```json
   {
     "api_key": "YOUR_CLOCKIFY_API_KEY",
     "vault_path": "Obsidian/daily_notes",
     "days_back": 3,
     "time_zone": "Europe/Moscow"
   }
   ```

To get your Clockify API key:  
[https://app.clockify.me/user/settings](https://app.clockify.me/user/settings)

---

## 🛠 Usage

```bash
python run_clockify_sync.py
```

---

## ✅ Output example

```markdown
# 2025-07-12

> [!clockify] Clockify time log
> Life - Cleaning: 01:16:10 (16:22)
> Work - Automation: 01:31:07 (18:04|Building automation)
```

---

## ⚠️ Notes

- This script fetches only your own entries from Clockify
- Existing `[!clockify]` blocks will be replaced
- All logic is local and simple — modify freely

---

## ⚖️ License

MIT. Use at your own risk. No guarantees, no support, but contributions welcome.
