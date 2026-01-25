#!/bin/bash
WIFI_IFACE=""
SSID="blackbox"
PASSWORD="arnold10054"
if ! sudo nmcli device wifi hotspot ifname "$WIFI_IFACE" con-name "blackbox-Hotspot" ssid "$SSID" password "$PASSWORD"; then
    echo "┌───┬───────┬─────────────────────────────────────────────────────────────┬───┬───┬───┐"
    echo "│ ! │ Error │ Setup failed.                                               │ _ │ O │ X │"
    echo "├───┴───────┴─────────────────────────────────────────────────────────────┴───┴───┴───┤"
    echo "│ below this box is the internet interfaces detected on your system:                  │"
    echo "│ Find the name of Wi-Fi card and edit this script (hotspot.sh)                       │"
    echo "├─────────────────────────────────────────────────────────────────────────────────────┤"
    echo "│ Available interfaces:                                                               │"
    echo "│ ─────────────────────────────────────────────────────────────────────────────────── │"
    ip -brief link | grep -v "lo" | sed 's/^/│ /'
    echo "└─────────────────────────────────────────────────────────────────────────────────────┘"
    exit 1
fi
echo "-> Hotspot created successfully!"
