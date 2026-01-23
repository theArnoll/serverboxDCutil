repoDict=$(pwd)
sudo apt install -y python3-pip python3-venv python3-full
python3 -m venv venv
source venv/bin/activate
pip install discord.py python-dotenv psutil simpleeval
echo Have you done editing .env? If not, Ctrl+C and edit it now. If yes, press Enter to continue.
read
read -p "Please enter the name (SSID) of your hotspot: " WIFI_SSID
read -s -p "Please enter your Wi-Fi Password (Password hidden): " WIFI_PASS

sudo bash -c "cat <<EOF > /etc/systemd/system/discord-bot.service
[Unit]
Description=Discord util
After=network.target

[Service]
User=root

WorkingDirectory=$repoDict

ExecStart=$repoDict/venv/bin/python $repoDict/main.py

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"
sudo systemctl daemon-reload
sudo systemctl enable discord-bot.service
sudo systemctl start discord-bot.service
sudo systemctl status discord-bot

WIFI_IFACE=$(ip a | grep -oP 'wlan[0-9]+' | head -1)
cat <<EOF > hotspot.sh
#!/bin/bash
WIFI_IFACE="$WIFI_IFACE"
SSID="$WIFI_SSID"
PASSWORD="$WIFI_PASS"
if ! sudo nmcli device wifi hotspot ifname "\$WIFI_IFACE" con-name "blackbox-Hotspot" ssid "\$SSID" password "\$PASSWORD"; then
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
EOF
chmod +x hotspot.sh