#!/usr/bin/env python3
# File: ~/.config/hypr/scripts/hypr-minimize.py

import json
import subprocess
import sys


def run_dispatch(cmd: str):
    """Executes a hyprctl dispatch instruction using exact native Lua function calls."""
    subprocess.run(
        ["hyprctl", "dispatch", cmd],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def get_hypr_json(endpoint: str) -> list | dict:
    """Extracts JSON status configurations from active hyprctl sockets."""
    try:
        result = subprocess.run(
            ["hyprctl", "-j", endpoint], capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, ValueError):
        return {}


def toggle_minimize(action: str):
    active_window = get_hypr_json("activewindow")
    clients = get_hypr_json("clients")

    if not isinstance(clients, list):
        return

    minimized_addresses = [
        c["address"]
        for c in clients
        if c.get("workspace", {}).get("name") == "special:minimize"
    ]

    # Explicit minimize action
    if action == "minimize":
        if active_window and "address" in active_window:
            addr = active_window["address"]
            current_ws = active_window.get("workspace", {}).get("name", "")
            
            if addr not in minimized_addresses and current_ws != "special:minimize":
                run_dispatch('hl.dsp.workspace.toggle_special("minimize")')
                run_dispatch(f'hl.dsp.window.move{{ workspace = "special:minimize", window = "address:{addr}" }}')
                run_dispatch('hl.dsp.workspace.toggle_special("minimize")')

    # Explicit restore action (Can be spammed continuously to empty the stack)
    elif action == "restore":
        if minimized_addresses:
            last_addr = minimized_addresses[-1]
            
            run_dispatch('hl.dsp.workspace.toggle_special("minimize")')
            run_dispatch(f'hl.dsp.window.move{{ workspace = "+0", window = "address:{last_addr}" }}')
            
            active_workspace = get_hypr_json("activeworkspace")
            if isinstance(active_workspace, dict) and active_workspace.get("name") == "special:minimize":
                run_dispatch('hl.dsp.workspace.toggle_special("minimize")')


if __name__ == "__main__":
    # Default to minimize if no argument is passed, otherwise catch the flag
    target_action = sys.argv[1] if len(sys.argv) > 1 else "minimize"
    toggle_minimize(target_action)
