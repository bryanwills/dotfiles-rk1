#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  update-dunst-colors.sh — Sync dunst colors with pywal
#  Safe ini-aware rewrite using Python
# ─────────────────────────────────────────────────────────────────────────────

DUNSTRC="$HOME/.config/dunst/dunstrc"
COLORS="$HOME/.cache/wal/colors"

if [[ ! -f "$COLORS" ]]; then
    echo "No pywal colors found at $COLORS"
    exit 1
fi

python3 - "$DUNSTRC" "$COLORS" << 'PYEOF'
import sys, os

dunstrc_path = sys.argv[1]
colors_path  = sys.argv[2]

# Read pywal colors
with open(colors_path) as f:
    C = [l.strip() for l in f if l.strip()]

BG   = C[0]
BG2  = C[1]
ACC  = C[2]
FG   = C[7]
FG2  = C[15] if len(C) > 15 else "#ffffff"
HIGH = C[4]
BG_T = BG + "b3"

# Color map per section
section_colors = {
    "global": {
        "frame_color":     ACC,
        "separator_color": ACC,
        "background":      BG_T,
        "foreground":      FG2,
    },
    "urgency_low": {
        "background":  BG_T,
        "foreground":  FG,
        "frame_color": BG2,
    },
    "urgency_normal": {
        "background":  BG_T,
        "foreground":  FG2,
        "frame_color": ACC,
    },
    "urgency_critical": {
        "background":  BG_T,
        "foreground":  FG2,
        "frame_color": HIGH,
    },
}

with open(dunstrc_path) as f:
    lines = f.readlines()

current_section = None
out = []

for line in lines:
    stripped = line.strip()

    # Detect section header e.g. [global]
    if stripped.startswith('[') and stripped.endswith(']'):
        current_section = stripped[1:-1]
        out.append(line)
        continue

    # Check if this line is a key we want to replace
    if current_section and '=' in stripped and not stripped.startswith('#'):
        key = stripped.split('=', 1)[0].strip()
        colors = section_colors.get(current_section, {})
        if key in colors:
            # Preserve original indentation
            indent = len(line) - len(line.lstrip())
            out.append(' ' * indent + f'{key} = "{colors[key]}"\n')
            continue

    out.append(line)

with open(dunstrc_path, 'w') as f:
    f.writelines(out)

print(f"Dunst colors updated -> BG:{BG_T} ACC:{ACC} FG:{FG2} HIGH:{HIGH}")
PYEOF
