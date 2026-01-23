# ServerBox Discord Utility Bot

## Functions
```
calc <expression>  - Calculate the expression
should             - Basically a dice
server <function>  - Server related functions:
    status       - Show server status
    ip           - Show server local IP address
    cockpit      - Show Cockpit link
    restart bot  - Restart the bot process
    reboot       - Reboot the server
    shutdown     - Shutdown the server
hotspot            - Turn on Wi-Fi hotspot
ping               - Pong ♪
help               - Show this help message
```

## Installation

``` bash
git clone https://github.com/theArnoll/serverboxDCutil.git
cd serverboxDCutil
chmod +x setup.sh
chmod +x main.py
```

## Bot Setup Instruction

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click `New Application`, give it a name, and create it.
3. Click `Bot` at the left sidebar
4. Find `Presence Intent`, `Server Members Intent` and `Message Content Intent` and enable it.
5. Click `Reset Token` and copy the token to [.env file](./.env).
6. Invite the bot to your server:
   1. Click `OAuth2` at the left sidebar → `OAuth2 URL Generator`.
   2. Have `bot` checkbox checked.
   3. Check `Send Messages` and `Read Message History` in the `Bot Permissions` field below.
   4. Copy the generated URL, paste it to your browser, and invite the bot to your private server.
7.  Open your Discord app, go to Settings → Advanced, and enable Developer Mode.
8.  Go to your private Discord server, right click on your profile picture, and click `Copy User ID`. Paste it to the `ALLOWED_USER_ID` field in the [.env file](./.env).
9. Run `setup.sh` to install dependencies and set up the systemd service.

---

Used Gemini for rapid prototyping; logic and system integration verified by human.  
**Tested** in VMWare Ubuntu Server 24.04 LTS environment.