#!/usr/bin/env python3
import os
import json
import shutil
import subprocess
import sys
from datetime import datetime

# --- Configuration ---
VERSION = "1.8.0"
BACKUP_DIR = os.path.expanduser("~/backup-configs")
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
    BACKUP_DIR = os.path.expanduser("~/backup-configs")
    SYNC_CACHE = os.path.expanduser("~/.cache/last_synced")
    
    # Define the system-wide folders and files to monitor
    watched = [
        '~/.config/hypr', 
        '~/.config/waybar', 
        '~/.config/foot',
        '~/.config/kitty', 
        '~/custom-scripts',
        '~/.config/wal',
        '~/.config/rofi',
        '~/.config/fastfetch',
        '~/.config/nwg-look',
        '~/.config/mako', 
        '~/.zshrc',
        '~/.p10k.zsh',
        '~/Pictures/Wallpapers'
    ]
    
    dirty_items = []

    try:
        # 1. Get the last sync time from the file itself
        if not os.path.exists(SYNC_CACHE):
            return f"{RED}Never Synced{RESET}"
        
        # We use the modification time of the cache file as our reference
        last_sync_time = os.path.getmtime(SYNC_CACHE)
        
        # 2. Scan LIVE system folders for changes since last_sync_time
        for path in watched:
            full_path = os.path.expanduser(path)
            if not os.path.exists(full_path):
                continue
            
            if os.path.isfile(full_path):
                if os.path.getmtime(full_path) > last_sync_time:
                    dirty_items.append(os.path.basename(path))
            else:
                # Deep scan directories
                found_change = False
                for root, _, files in os.walk(full_path):
                    for f in files:
                        if os.path.getmtime(os.path.join(root, f)) > last_sync_time:
                            dirty_items.append(os.path.basename(path))
                            found_change = True
                            break
                    if found_change:
                        break

        # 3. Check Git status for unpushed commits
        ahead = 0
        try:
            ahead = subprocess.check_output(
                ["git", "-C", BACKUP_DIR, "rev-list", "@{u}..HEAD"], 
                stderr=subprocess.DEVNULL
            ).decode().count('\n')
        except:
            pass

        # 4. Read the text date from the cache for display
        with open(SYNC_CACHE, 'r') as f:
            sync_date = f.read().strip()

        # Formatting the output
        if dirty_items:
            # \033[1;31m is Bold Red. This overrides pywal's standard red.
            # We show the first dirty item to keep the line from getting too long.
            main_item = dirty_items[0].replace('.config/', '')
            status_text = f"\033[1;31mDirty\033[0m ({main_item})"
        else:
            status_text = f"{GREEN}Clean{RESET}"
        
        # 2. Sync Logic
        sync_color = YELLOW if ahead > 0 else GREEN
        sync_text = f"↑ {ahead} Unpushed" if ahead > 0 else "Synced"
        
        return f"{status_text} | {sync_color}{sync_text}{RESET} ({sync_date})"

    except Exception as e:
        return f"{RED}Backup Error{RESET}"

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
    # Final aligned layout
    print(f"\n{BOLD}{CYAN}󰣇 SYSTEM REPORT{RESET} | {datetime.now().strftime('%H:%M:%S')}")
    print(f"{CYAN}......................................................{RESET}")
    
    col1_w = 38 # Adjusted for your terminal padding
    
    s_text = f" 💾 {BOLD}Storage:{RESET}  {shutil.disk_usage(os.path.expanduser('~')).free // (2**30)} GB Free"
    u_text = f" 📦 {BOLD}Updates:{RESET}  {get_updates()}"
    c_text = f" 󰒋  {BOLD}Cache:{RESET}    {get_cache_size()}"
    
    t_text = f" 📝 {BOLD}Tasks:{RESET}   {get_pending_tasks()}"
    b_text = f" 🔄 {BOLD}Backup:{RESET}  {get_git_status()}"

    budget_text = get_budget_status()
    
    # Define the widths for both columns
    col1_w = 40  
    col2_w = 48
    # Print each row with explicit padding for both sides
    print(f"{s_text:<{col1_w}} {t_text}")
    print(f"{u_text:49} {b_text}")
    print(f"{c_text:<{col1_w}}")
    print(f" 󱚝  {BOLD}Budget:{RESET}  {budget_text}")
    
    print(f"{CYAN}......................................................{RESET}\n")

if __name__ == "__main__":
    main()
