import os
import sys
import re
import hashlib
from pathlib import Path
from datetime import datetime


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

SUSPICIOUS_EXTENSIONS = {
    ".dll", ".exe", ".bat", ".vbs", ".ps1",
    ".py",  ".lua", ".asi", ".jar",
    ".so",  ".dylib",
}

KNOWN_BAD_HASHES = {}

MAX_HASH_FILE_SIZE = 50 * 1024 * 1024
HASH_CHUNK_SIZE    = 65_536

BAR = "=" * 44


def get_default_scan_paths():
    home = Path.home()

    if sys.platform.startswith("win"):
        candidates = [
            home / "Desktop",
            home / "Downloads",
            home / "Documents",
            home / "AppData" / "Roaming",
            home / "AppData" / "Local",
            Path("C:/Games"),
            Path("C:/Program Files/Steam"),
            Path("C:/Program Files (x86)/Steam"),
            Path("D:/Games"),
            Path("D:/SteamLibrary"),
            Path("E:/Games"),
            Path("E:/SteamLibrary"),
        ]
    elif sys.platform.startswith("darwin"):
        candidates = [
            home / "Desktop",
            home / "Downloads",
            home / "Documents",
            home / "Library" / "Application Support",
            Path("/Applications"),
        ]
    else:
        candidates = [
            home / "Desktop",
            home / "Downloads",
            home / "Documents",
            home / ".local" / "share",
            home / ".steam",
            home / ".config",
            Path("/opt"),
            Path("/usr/local/games"),
        ]

    seen, valid = set(), []
    for p in candidates:
        try:
            resolved = p.resolve()
        except OSError:
            continue
        if resolved not in seen and p.exists() and p.is_dir():
            seen.add(resolved)
            valid.append(p)
    return valid


def _clear_line():
    print(f"\r{' ' * 60}\r", end="", flush=True)


def _fmt_elapsed(td):
    total = int(td.total_seconds())
    h, rem = divmod(total, 3600)
    m, s   = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def print_banner():
    print()
    print(BAR)
    print("       GAMEGUARD ANTI-CHEAT SCANNER")
    print(BAR)
    print()


def print_finding(filepath, reason):
    _clear_line()
    print("  [!] Potentially Suspicious File Found")
    print()
    print(f"      Name     : {filepath.name}")
    print(f"      Location : {filepath}")
    print(f"      Reason   : {reason}")
    print()


def print_access_denied(path):
    _clear_line()
    print(f"  [!] Access denied  : {path}")


def print_summary(total, findings, elapsed):
    print()
    print(BAR)
    print("               SCAN COMPLETE")
    print(BAR)
    print()
    print(f"  Files Scanned            : {total:,}")
    print(f"  Potentially Suspicious   : {len(findings)}")
    print(f"  Scan Duration            : {_fmt_elapsed(elapsed)}")

    if findings:
        print()
        print("  Potentially Suspicious Files:")
        print()
        for i, (fp, reason) in enumerate(findings, 1):
            print(f"  {i}. {fp.name}")
            print(f"     {fp}")
            print(f"     Reason : {reason}")
            print()
    else:
        print()
        print("  No potentially suspicious files detected.")
        print()

    print(BAR)
    print()
    print("  NOTE: These results are informational only.")
    print("  A keyword match does NOT confirm a file is malicious.")
    print("  Review each flagged file manually before taking action.")
    print()


def _extract_tokens(text):
    t1 = set(re.findall(r'[a-z]+', text.lower()))
    t2 = set(re.findall(r'[a-z]+', re.sub(r'([a-z])([A-Z])', r'\1 \2', text).lower()))
    return t1 | t2


def _keyword_in(keyword, tokens):
    if keyword in tokens:
        return True
    klen = len(keyword)
    if klen >= 4:
        for token in tokens:
            if token.startswith(keyword):
                return True
    if klen >= 8:
        for token in tokens:
            if keyword in token:
                return True
    return False


def sha256_hash(filepath):
    try:
        size = filepath.stat().st_size
    except OSError:
        return None

    if size > MAX_HASH_FILE_SIZE:
        return None

    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as fh:
            for chunk in iter(lambda: fh.read(HASH_CHUNK_SIZE), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, PermissionError):
        return None


def check_file(filepath):
    if KNOWN_BAD_HASHES:
        digest = sha256_hash(filepath)
        if digest and digest in KNOWN_BAD_HASHES:
            label = KNOWN_BAD_HASHES[digest]
            return True, f"known bad hash — {label}"

    ext     = filepath.suffix.lower()
    ext_ctx = (f"; risky extension '{ext}'"
               if ext in SUSPICIOUS_EXTENSIONS else "")

    stem_tokens = _extract_tokens(filepath.stem)
    for kw in SUSPICIOUS_KEYWORDS:
        if _keyword_in(kw, stem_tokens):
            return True, f"keyword '{kw}' in file name{ext_ctx}"

    for part in filepath.parts[:-1]:
        part_tokens = _extract_tokens(part)
        for kw in SUSPICIOUS_KEYWORDS:
            if _keyword_in(kw, part_tokens):
                return True, (f"keyword '{kw}' in "
                              f"parent folder '{part}'{ext_ctx}")

    return False, ""


def run_scan(roots):
    findings      = []
    total_scanned = 0
    scan_start    = datetime.now()

    print("  Starting system scan...")
    print()
    for root in roots:
        print(f"  →  {root}")
    print()
    print("  Scanning...  (press Ctrl+C to stop early)")
    print()

    def _on_dir_error(err):
        _clear_line()
        print(f"  [!] Access denied  : {getattr(err, 'filename', str(err))}")

    for root in roots:
        for dirpath, dirnames, filenames in os.walk(
            root, followlinks=False, onerror=_on_dir_error
        ):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]

            for filename in filenames:
                filepath = Path(dirpath) / filename
                total_scanned += 1

                if total_scanned % 250 == 0:
                    print(
                        f"\r  Files checked: {total_scanned:,}   ",
                        end="", flush=True,
                    )

                try:
                    suspicious, reason = check_file(filepath)
                    if suspicious:
                        findings.append((filepath, reason))
                        print_finding(filepath, reason)

                except PermissionError:
                    print_access_denied(filepath)

                except OSError:
                    pass

    _clear_line()
    elapsed = datetime.now() - scan_start
    print_summary(total_scanned, findings, elapsed)


def choose_scan_target():
    print("  Scan Options:")
    print()
    print("  [1] Scan common user folders")
    print("      Desktop, Downloads, Documents, AppData, Steam libraries …")
    print()
    print("  [2] Scan a specific folder")
    print()

    while True:
        choice = input("  Enter choice (1 or 2): ").strip()
        if choice in ("1", "2"):
            break
        print("  Invalid choice. Please enter 1 or 2.")

    print()

    if choice == "1":
        roots = get_default_scan_paths()
        if not roots:
            print("  [!] No default scan directories found on this system.")
            print("      Please use option 2 to enter a path manually.")
            sys.exit(1)
        return roots

    raw = input("  Enter folder path: ").strip().strip('"').strip("'")

    if not raw:
        print("\n  [!] No path entered. Exiting.")
        sys.exit(1)

    target = Path(raw)

    if not target.exists():
        print(f"\n  [!] Path not found: {raw}")
        sys.exit(1)

    if not target.is_dir():
        print(f"\n  [!] That path is a file, not a folder: {raw}")
        sys.exit(1)

    return [target]


def main():
    print_banner()
    roots = choose_scan_target()
    print()
    run_scan(roots)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("  [!] Scan interrupted by user (Ctrl+C).")
        print()
        sys.exit(0)
