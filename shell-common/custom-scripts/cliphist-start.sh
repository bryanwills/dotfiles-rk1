#!/usr/bin/env bash
# Wipe cliphist but restore pinned entries first

PINS="$HOME/.cache/clipbox-pins.json"

# Wipe existing history
cliphist wipe

# Re-seed pinned entries back in
if [[ -f "$PINS" ]]; then
    python3 -c "
import json
with open('$PINS') as f:
    pins = json.load(f)
for p in reversed(pins):
    print(p)
" | while IFS= read -r line; do
        echo "$line" | cliphist store
    done
fi
