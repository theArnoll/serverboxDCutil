# ServerBox Discord Utility Bot

## Table of Contents

- [ServerBox Discord Utility Bot](#serverbox-discord-utility-bot)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
    - [Active Features](#active-features)
    - [Passive Features](#passive-features)
      - [Taiwanese extreme heat forecast in 24 hours](#taiwanese-extreme-heat-forecast-in-24-hours)
      - [Cryptocurrency price alert](#cryptocurrency-price-alert)
  - [Installation](#installation)
  - [Bot Setup Instruction](#bot-setup-instruction)
  - [Confirm if the bot is running](#confirm-if-the-bot-is-running)

## Features

### Active Features

This is the main function of this bot

```
calc <expression>  - Calculate the expression
should             - Basically a dice
server <function>  - Server related functions:
    status              - Show server status
    ip                  - Show server local IP address
    cockpit             - Show Cockpit link
    restart bot / rebot - Restart the bot process
    reboot              - Reboot the server (Requires confirmation)
    shutdown            - Shutdown the server (Requires confirmation)
    aliases: svr, srv, sv, s
hotspot <function> - Toggle Wi-Fi hotspot
    on                  - Turn on Wi-Fi hotspot and turn off Bluetooth
    off                 - Turn off Wi-Fi hotspot and turn on Bluetooth
    [no parameter]      - Toggle between on and off by record
    aliases: wifi
ping               - Pong ♪ (Confirming if the server connected to the internet and able to response)
help               - Show built-in help message
commands           - Show this command list
                     aliases: hepp, cmds, cmd
statusRainbow      - Show every color ">server status" will send
author             - Show bot author information
wake               - Remote booting PC
testNotif          - Test notification system
```

### Passive Features

#### Taiwanese extreme heat forecast in 24 hours

> **`!` Requires Traditional Chinese input on server side.**  
> &emsp;Recommends to type Chinese in cockpit terminal.

You can enable the extreme heat forcast tool by setting up the CWA API key and filling the location you want to track in `.env`.

Setup guide:

1. Login or sign up an account on [中央氣象署氣象資料開放平臺(CWA OPEN WEATHER DATA)](https://opendata.cwa.gov.tw/userLogin)
   If you need to sign up, make sure after signd up, go back to the link above and **log in on THAT webpage**, not the page you'll eventually be direct to after you go through the sign up step.  
   **Chinese ability or translator is required during sign up**
2. Click "取得授權碼" or "Get Authorization Key" button.
3. There will be a line of red text append on the side of the button that should start with "CWA-". That's your API key. Copy it.
4. Open `.env` and fill in the API key you just copied into `CWA_API_KEY=`
5. Fill in your location name in the format of [City/county name]-[District name] **in Chinese** into `LOCATION_NAME=`, e.g. `台北市-中正區`, `高雄市-苓雅區`.  
   You can also fill multiple locations at the same time. Just separate them with a comma, e.g. `台北市-中正區,臺中市-中區,高雄市-苓雅區`.  
   *Note that you should NOT put any other characters including space in the location name*.

After the setup, the bot will send you a message <!-- like below --> when any of your tracked location are expected to have extreme heat in 24 hours at roughly 7:00 ~ 7:10 AM.

The definition of extreme heat here is 35°C.  
&emsp;Since it's an open source script, you can `Ctrl + F` find "35.0" and replace it to your desired temperature in `main.py`.

#### Cryptocurrency price alert

When the price of your tracked cryptocurrency reaches the threshold price you set, the bot will send you a message. <!-- like below. -->

The default cryptocurrency and threshold is BTC (`bitcoin`), USD (`usd`), $36000.00 (`36000.00`), which means when BTC hits 36000 USD, send the message.

You can change the cryptocurrency, currency, and threshold in `.env` file. For example, you want the bot to send a message when DOGE hits 3 TWD, you can edit `monitoringCrypto`, `cryptoToCurrency` and `cryptoToCurrencyAlertThreshold` in `.env` file to:

```
monitoringCrypto=dogecoin
cryptoToCurrency=twd
cryptoToCurrencyAlertThreshold=3.00
```

This function is going to check the price of cryptocurrency each hour from 10 AM to 9 PM.

## Installation

``` bash
sudo apt install -y python3 python-is-python3 
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

## Confirm if the bot is running

Run

``` sh
systemctl status discord-bot.service 
```

The output should be something like

```
● discord-bot.service - Discord util
     Loaded: loaded (/etc/systemd/system/discord-bot.service; enabled; preset: enabled)
     Active: active (running) since Sun 2026-01-25 19:29:33 UTC; 17s ago
   Main PID: 2271 (python)
      Tasks: 3 (limit: 9165)
     Memory: 31.8M (peak: 32.1M)
        CPU: 543ms
     CGroup: /system.slice/discord-bot.service
             └─2271 /home/user/serverboxDCutil/venv/bin/python /home/user/serverboxDCutil/main.py
```

The "light bulb" (Big dot) before "discord-bot.service" should be green, and there shouldn't be any error message such as `(code=exited, status=1/FAILURE)` in the end of `Process:` line (or maybe there should be a line start with `Process:`) or `Main PID:` line.

---

Used Gemini for rapid prototyping; logic and system integration verified by human.

**Tested** in:

- VMWare Ubuntu Server 24.04 LTS environment.
- Intel N100 mini PC **`Currently running`**  
  Spec:
  - Intel N100
  - 8GB DDR5
  - 120GB 2.5" SSD (connected via USB)
  - Ubuntu Server 24.04 LTS
