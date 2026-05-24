#!/usr/bin/env zsh

# -----------------------------------------------------------------------------------
# IWCTL INTERACTIVE WIFI FZF WIDGET SCRIPT
# With Active Connection Markers
# May 2026 v0.2.0
# -----------------------------------------------------------------------------------

if ! command -v iwctl &> /dev/null || ! command -v fzf &> /dev/null; then
    echo "Error: iwctl or fzf not found. Please install them to use this script."
    exit 1
fi

# Locate the active wireless device interface and strip hidden ANSI color codes
wifi_device=$(iwctl device list | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g" | grep 'station' | awk '{print $1}')

if [ -z "$wifi_device" ]; then
    echo "Error: No active wireless station device found via iwctl."
    exit 1
fi

echo "󰖩  Scanning for available wireless networks..."
iwctl station "$wifi_device" scan > /dev/null 2>&1
sleep 1.2

# Capture the raw stream, identify the highlighted network line, and inject a custom marker symbol
network_list=$(iwctl station "$wifi_device" get-networks | \
    awk '
    NR <= 4 { print; next }
    {
        # iwctl uses highlight tags to mark the connected network row in pipes
        if ($0 ~ /\x1B\[1m/ || $0 ~ />/) {
            gsub(/^[\t >*]+/, "");
            print "󰄬 " $0
        } else {
            print "  " $0
        }
    }')

# Interactive menu, passing the updated text stack straight through to fzf
selected_line=$(echo "$network_list" | \
    fzf --height 40% \
        --reverse \
        --ansi \
        --border rounded \
        --margin=1,2 \
        --header "Select WiFi Network (ESC to quit)" \
        --info inline \
        --header-lines=4 \
        --color="bg+:-1,bg:-1,hl:3,fg:7,header:3,info:4,pointer:3,marker:3,prompt:3")

[ -z "$selected_line" ] && exit

# Clean up ANSI sequences and markers completely for parameter parsing
clean_line=$(echo "$selected_line" | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g" | tr -d '*' | sed 's/^󰄬 //g' | awk '{$1=$1;print}')

# Parse fields out from the right side safely
security=$(echo "$clean_line" | awk '{print $(NF-1)}')
ssid=$(echo "$clean_line" | awk '{
    end = NF - 2;
    for(i=1; i<=end; i++) printf "%s%s", $i, (i==end?"":" ")
    print ""
}')

# Check if the network profile is recognised by the storage backend
if iwctl known-networks list | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[mGK]//g" | grep -F -q "$ssid"; then
    echo "Connecting to known network: $ssid..."
    iwctl station "$wifi_device" connect "$ssid"
else
    echo "New network detected: $ssid"
    if [[ "$security" =~ "open" ]]; then
        iwctl station "$wifi_device" connect "$ssid"
    else
        read -rs -p "Enter Password for $ssid: " password
        echo ""
        echo "$password" | iwctl station "$wifi_device" connect "$ssid"
    fi
fi
