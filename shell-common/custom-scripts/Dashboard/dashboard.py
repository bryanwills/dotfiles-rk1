#!/usr/bin/env python3
import os
import json
import shutil
import subprocess
import sys
from datetime import datetime

# --- Configuration ---
VERSION = "1.8.0"
BACKUP_DIR = os.path.expanduser("~/dotfiles")
PROJECT_DIR = os.path.expanduser("~/arch-projects/arch-update-check")
TASKS_JSON = os.path.expanduser("~/.local/share/arch_task_manager/tasks.json")
SYNC_CACHE = os.path.expanduser("~/.cache/last_synced")

# Colors
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'

def get_updates():
    try:
        official = subprocess.check_output(["checkupdates"], stderr=subprocess.DEVNULL).decode().count('\n')
    except:
        official = 0

    try:
        aur = subprocess.check_output(["yay", "-Qua"], stderr=subprocess.DEVNULL).decode().count('\n')
    except:
        aur = 0

    total = official + aur

    if total == 0:
        return f"{GREEN}Up-to-date{RESET}"
    else:
        color = YELLOW if total < 15 else RED
        # Change the string here to be more descriptive and avoid double-counting
        if aur > 0:
            return f"{color}{total} Total ({aur} AUR){RESET}"
        else:
            return f"{color}{total} Pending{RESET}"
                    
def get_cache_size():
    cache_path = "/var/cache/pacman/pkg/"
    if not os.path.exists(cache_path): return "N/A"
    try:
        total = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(cache_path) for f in fs)
        gb = total / (1024**3)
        color = RED if gb > 10 else (YELLOW if gb > 5 else GREEN)
        return f"{color}{gb:.1f} GB{RESET}"
    except: return "Error"

def get_pending_tasks():
    if not os.path.exists(TASKS_JSON): return f"{YELLOW}No Data{RESET}"
    try:
        with open(TASKS_JSON, 'r') as f:
            tasks = json.load(f)
            pending = sum(1 for t in tasks if not (t.get('completed') or t.get('status') == 'done'))
            return f"{YELLOW}{pending} Pending{RESET}"
    except: return f"{RED}Error{RESET}"

def get_git_status():
    def check_repo(path):
        if not os.path.exists(path):
            return f"{RED}Missing{RESET}"
        
        try:
            is_dirty = subprocess.check_output(["git", "-C", path, "status", "--porcelain"], stderr=subprocess.DEVNULL).decode().strip()
            ahead = subprocess.check_output(["git", "-C", path, "rev-list", "@{u}..HEAD"], stderr=subprocess.DEVNULL).decode().count('\n')
        except:
            return f"{RED}Error{RESET}"
            
        status = f"{RED}Dirty{RESET}" if is_dirty else f"{GREEN}Clean{RESET}"
        if ahead > 0:
            status += f" {YELLOW}↑ {ahead}{RESET}"
        return status

    # Get the human-readable sync date
    try:
        with open(SYNC_CACHE, 'r') as f:
            sync_date = f.read().strip()
    except:
        sync_date = "Never"

    return {
        "dots": check_repo(BACKUP_DIR),
        "proj": check_repo(PROJECT_DIR),
        "date": sync_date
    }
        
def get_budget_status():
    """Fetches a summary string from the Budget Buddy script."""
    try:
        # Path to your budget script
        path = os.path.expanduser("~/custom-scripts/Budget-Buddy/budget-buddy.py")
        # Runs the script with the --stats flag and captures the text output
        result = subprocess.check_output(
            ["python", path, "--stats"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return result
    except Exception:
        return f"{RED}Budget Data Unavailable{RESET}"
        
def main():
    git_data = get_git_status()
    
    print(f"\n{BOLD}{CYAN}󰣇 SYSTEM REPORT{RESET} | {datetime.now().strftime('%H:%M:%S')}")
    print(f"{CYAN}......................................................{RESET}")
    
    # Define a helper to handle the padding correctly
    def align(label, value, width=15):
        # Subtracting 2 to account for the icon and space
        return f"{BOLD}{label}{RESET}".ljust(width + 8) + f" {value}"

    # Row 1
    s_text = f" 💾 {BOLD}Storage:{RESET}  {shutil.disk_usage(os.path.expanduser('~')).free // (2**30)} GB Free"
    t_text = f" 📝 {BOLD}Tasks:{RESET}    {get_pending_tasks()}"
    
    # Row 2
    u_text = f" 📦 {BOLD}Updates:{RESET}  {get_updates()}"
    d_text = f" 󱓞  {BOLD}Dots:{RESET}     {git_data['dots']} ({git_data['date']})"
    
    # Row 3
    c_text = f" 󰒋  {BOLD}Cache:{RESET}    {get_cache_size()}"
    p_text = f" 󱚝  {BOLD}Proj:{RESET}     {git_data['proj']}"

    # Print with manual spacing for total control
    # Adjust the number 35 to move the right column left or right
    print(f"{s_text:<40} {t_text}")
    print(f"{u_text:<49} {d_text}")
    print(f"{c_text:<50} {p_text}")
    print(f" 󱚝  {BOLD}Budget:{RESET}   {get_budget_status()}")
    
    print(f"{CYAN}......................................................{RESET}\n")
        
if __name__ == "__main__":
    main()
