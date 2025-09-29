# insta-osint
🔍 Advanced Instagram OSINT & Reconnaissance Tool — by **Néro**

`insta-osint` is a lightweight command-line tool for gathering **public information from Instagram profiles**.  
Useful for **cybersecurity analysts**, **penetration testers**, and **OSINT researchers**.

---

## ✨ Features
- Fetch full **public profile information**
- Download **HD profile picture**
- Extract **emails / hashtags / mentions** from bio
- Save output as **JSON** or **HTML report**
- Support for **single user** or **bulk mode** via .txt file

## ⚙️ Installation

### 🔹 Option 1 — Direct via `git clone`
```bash
git clone https://github.com/zazall/insta-recon-tool.git
cd insta-recon-tool
python in.py


usage: in.py [-h] [-u USERNAME] [-f FILE] [--no-html]

INSTA-RECON: An advanced OSINT tool for Instagram.

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        A single Instagram username to scan.
  -f FILE, --file FILE  Path to a file containing a list of usernames to scan (one per line).
  --no-html             Disable HTML report generation.
