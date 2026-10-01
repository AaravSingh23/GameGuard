# 🛡️ GameGuard – Console Anti-Cheat File Scanner

A lightweight, single-file Python tool that scans your computer for
potentially suspicious gaming cheat and hack-related files.
No GUI. No internet connection. No files deleted. Completely transparent.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Scan Options](#scan-options)
- [Sample Output](#sample-output)
- [Configuration](#configuration)
- [How Detection Works](#how-detection-works)
- [Building a Windows .exe](#building-a-windows-exe)
- [Project Structure](#project-structure)
- [Disclaimer](#disclaimer)

---

## Overview

GameGuard is a beginner-friendly Python console program whose only job is:

```
SCAN → DETECT POTENTIALLY SUSPICIOUS FILES → SHOW NAME + LOCATION
```

It walks your directories recursively, checks every file name and parent
folder name against a configurable keyword list, and reports anything
that looks suspicious — in real time, as it scans.

---

## Features

| Feature | Detail |
|---|---|
| ✅ Real-time alerts | Suspicious files are printed immediately as found |
| ✅ Smart token matching | `model.py` is NOT flagged for keyword `mod` |
| ✅ CamelCase support | `CheatEngine.exe`, `WallESP.dll`, `ModMenu.dll` all detected |
| ✅ Folder-name detection | Files inside a `hacktools/` folder are flagged |
| ✅ SHA-256 hash blocklist | Optional — catches renamed copies of known-bad files |
| ✅ No false crashes | Access-denied files and directories are reported and skipped |
| ✅ Clean elapsed time | Shows `2m 7s`, not `0:02:07.419283` |
| ✅ Two scan modes | Common user folders OR a custom path you choose |
| ✅ Zero dependencies | Only Python standard library — nothing to pip install |
| ✅ Cross-platform | Works on Windows, macOS, and Linux |

---

## Requirements

- **Python 3.7 or newer**
- No third-party packages — uses only the Python standard library

To check your Python version:

```bash
python --version
# or
python3 --version
```

---

## Installation

No installation required. Download the single file and run it.

**Step 1 — Download or clone**

```bash
# Option A: clone the repo
git clone https://github.com/yourname/gameguard.git
cd gameguard

# Option B: just download gameguard.py directly
```

**Step 2 — Run**

```bash
python gameguard.py
# or on Linux/macOS
python3 gameguard.py
```

That is all. No `pip install`, no virtual environment, no setup.

---

## Usage

```bash
python gameguard.py
```

You will be shown two options:

```
  Scan Options:

  [1] Scan common user folders
      Desktop, Downloads, Documents, AppData, Steam libraries …

  [2] Scan a specific folder

  Enter choice (1 or 2):
```

**Option 1** scans the folders most likely to contain cheat files
(see [Scan Options](#scan-options) below for the full list).

**Option 2** lets you type any folder path:

```
  Enter folder path: C:\Games\MyGame
```

Drag-and-dropping a folder onto the terminal window also works —
surrounding quotes are stripped automatically.

To stop a scan early, press **Ctrl+C**. The program exits cleanly.

---

## Scan Options

### Option 1 — Common user folders

| Platform | Folders scanned |
|---|---|
| **Windows** | Desktop, Downloads, Documents, AppData\Roaming, AppData\Local, C:\Games, C:\Program Files\Steam, C:\Program Files (x86)\Steam, D:\Games, D:\SteamLibrary, E:\Games, E:\SteamLibrary |
| **macOS** | Desktop, Downloads, Documents, ~/Library/Application Support, /Applications |
| **Linux** | Desktop, Downloads, Documents, ~/.local/share, ~/.steam, ~/.config, /opt, /usr/local/games |

Only folders that actually exist on your machine are scanned.
Protected system directories (e.g. `C:\Windows`) are intentionally excluded.

### Option 2 — Specific folder

Type any path you want to scan recursively:

```
Windows:  C:\Games\MyGame
Linux:    /home/user/games
macOS:    /Users/user/Library/Application Support/Steam
```

---

## Sample Output

**While scanning:**

```
============================================
       GAMEGUARD ANTI-CHEAT SCANNER
============================================

  Scan Options:

  [1] Scan common user folders
  [2] Scan a specific folder

  Enter choice (1 or 2): 2
  Enter folder path: C:\Games\TestGame

  Starting system scan...

  →  C:\Games\TestGame

  Scanning...  (press Ctrl+C to stop early)

  Files checked: 500

  [!] Potentially Suspicious File Found

      Name     : aimbot.exe
      Location : C:\Games\TestGame\Downloads\aimbot.exe
      Reason   : keyword 'aimbot' in file name; risky extension '.exe'

  [!] Potentially Suspicious File Found

      Name     : injector.dll
      Location : C:\Games\TestGame\injector.dll
      Reason   : keyword 'injector' in file name; risky extension '.dll'
```

**At the end:**

```
============================================
               SCAN COMPLETE
============================================

  Files Scanned            : 1,247
  Potentially Suspicious   : 3
  Scan Duration            : 4s

  Potentially Suspicious Files:

  1. aimbot.exe
     C:\Games\TestGame\Downloads\aimbot.exe
     Reason : keyword 'aimbot' in file name; risky extension '.exe'

  2. injector.dll
     C:\Games\TestGame\injector.dll
     Reason : keyword 'injector' in file name; risky extension '.dll'

  3. config.ini
     C:\Games\hacktools\config.ini
     Reason : keyword 'hack' in parent folder 'hacktools'

============================================

  NOTE: These results are informational only.
  A keyword match does NOT confirm a file is malicious.
  Review each flagged file manually before taking action.
```

---

## Configuration

All configuration is at the top of `gameguard.py`. No separate config file needed.

### Changing the keyword list

Open `gameguard.py` and find `SUSPICIOUS_KEYWORDS`:

```python
SUSPICIOUS_KEYWORDS = [
    "cheat",
    "hack",
    "hacker",
    "aimbot",
    "wallhack",
    "esp",
    "triggerbot",
    "injector",
    "trainer",
    "loader",
    "bypass",
    "modmenu",
    "mod",
    "script",
    "exploit",
]
```

- **Add a keyword** → add a new lowercase string to the list
- **Remove a keyword** → delete or comment-out that line

All entries must be lowercase. The scanner handles uppercase and mixed-case
filenames automatically.

### Adding a SHA-256 hash blocklist

If you know the exact SHA-256 hash of a cheat file, add it to `KNOWN_BAD_HASHES`.
The file will be flagged even if it has been renamed:

```python
KNOWN_BAD_HASHES = {
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855":
        "ExampleCheatTool v2.1",
}
```

To find a file's SHA-256 hash:

```bash
# Windows (PowerShell)
Get-FileHash "C:\path\to\file.exe" -Algorithm SHA256

# Linux / macOS
sha256sum /path/to/file.exe
```

### Adjusting the file-size limit for hashing

Very large files are skipped during hash checking to keep scanning fast.
The default limit is 50 MB. Change it here:

```python
MAX_HASH_FILE_SIZE = 50 * 1024 * 1024   # 50 MB
```

---

## How Detection Works

Detection runs in three layers for every file:

### Layer 1 — SHA-256 hash blocklist
The file's hash is computed and checked against `KNOWN_BAD_HASHES`.
This catches files that have been renamed to hide their identity.
Only active when you populate `KNOWN_BAD_HASHES`.

### Layer 2 — File name matching
The file name (without extension) is broken into word tokens and checked
against `SUSPICIOUS_KEYWORDS` using three strategies:

| Strategy | Keyword min length | What it catches |
|---|---|---|
| **Exact token** | any | `aimbot.exe` via keyword `aimbot` |
| **Token starts-with** | ≥ 4 chars | `hacktools.exe` via keyword `hack` |
| **Keyword inside token** | ≥ 8 chars | `dllinjector.exe` via keyword `injector` |

The minimum-length guards prevent short keywords from matching inside
unrelated words. For example:

- `mod` (3 chars) → **only exact match** → `model.py` is **not** flagged ✓
- `script` (6 chars) → prefix match → `description.txt` is **not** flagged
  because `description` does not start with `script` ✓
- `trainer` (7 chars) → prefix only, no substring → `container.cfg` is
  **not** flagged because `container` does not start with `trainer` ✓

### Layer 3 — Parent folder name matching
Every directory in the file's path is checked individually using the same
three-strategy algorithm. This means a file sitting inside a folder named
`hacktools` or `cheat_mods` will be flagged even if the file itself has
an innocent name.

> **Why individually and not the whole path as one string?**
> Concatenating the path would cause false positives — for example,
> if your username or a folder like `ModernGameSuite` happened to contain
> a keyword substring like `mod`.

---

## Building a Windows .exe

You can package GameGuard into a standalone Windows executable that runs
without Python installed.

**Step 1 — Install PyInstaller**

```bash
pip install pyinstaller
```

**Step 2 — Build**

```bash
pyinstaller --onefile gameguard.py
```

**Step 3 — Find your .exe**

```
dist/
└── gameguard.exe    ← your standalone executable
```

**Step 4 — Run it**

Double-click `gameguard.exe`, or run it from a terminal:

```
gameguard.exe
```

> On Windows you may need to right-click → **Run as administrator** if you
> want to scan folders that require elevated access.
> The scanner will otherwise skip those folders and report them as
> access-denied without crashing.

---

## Project Structure

```
gameguard/
├── gameguard.py       ← the entire program (single file)
├── requirements.txt   ← no dependencies; documents standard-library use
└── README.md          ← this file
```

---

## Disclaimer

- GameGuard is a **passive scanner** only. It reads files and reports names
  and paths. It does not delete, modify, upload, or execute anything.
- A keyword or hash match does **not** confirm that a file is a cheat tool
  or malicious software. Many legitimate programs ship DLL files, loader
  utilities, or scripts. Always review flagged files manually.
- The tool does not replace a full antivirus or a dedicated anti-cheat
  system. It is intended as a simple, transparent, educational first pass.
- GameGuard does not access the internet, does not send telemetry, and
  does not require any permissions beyond reading the directories you
  point it at.

---

*Built with Python standard library only — no external packages required.*
