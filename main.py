import discord
from discord.ext import commands, tasks
import random
import psutil  # sysinfo
import os
from dotenv import load_dotenv
from simpleeval import simple_eval
import asyncio
import sys
import shutil
import aiohttp  # Replace requests with async aiohttp
import datetime

from wakeonlan import send_magic_packet

last_weather_date = None  # Record if weather has been checked today

load_dotenv()

hotspot_tog = False

# Configurations
TOKEN = os.getenv('DC_TOKEN')
MAC = os.getenv('MAC')
ALLOWED_USER_ID = int(os.getenv('ALLOWED_USER_ID'))
CWA_API_KEY = os.getenv('CWA_API_KEY')
TARGET_CITY = os.getenv('TARGET_CITY')
cryptoToMonitor = os.getenv('monitoringCrypto')
cryptoToCurrency = os.getenv('cryptoToCurrency')
alertThreshold = float(os.getenv('cryptoToCurrencyAlertThreshold'))

bot = commands.Bot(
    command_prefix='>',
    intents=discord.Intents.all(),
    case_insensitive=True
)
# '>' is the command prefix

@bot.event
async def on_ready():
    print(f'DC tool is now online: {bot.user}')
    # Bot status (ex. Playing N100 Server)
    # await bot.change_presence(activity=discord.Game(name="N100 Server"))
    
    # Start background monitoring schedule
    if not autoMonitor.is_running():
        autoMonitor.start()

# Check if the user is allowed
@bot.check
async def globally_block_strangers(ctx):
    return ctx.author.id == ALLOWED_USER_ID

async def get_cmd_output(cmd):
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    return stdout.decode().strip()

async def fetch_temperatures(thresholdTemp):
    if not CWA_API_KEY: return []
    COUNTY_MAP = {
        "宜蘭縣": "F-D0047-001", "桃園市": "F-D0047-005", "新竹縣": "F-D0047-009",
        "苗栗縣": "F-D0047-013", "彰化縣": "F-D0047-017", "南投縣": "F-D0047-021",
        "雲林縣": "F-D0047-025", "嘉義縣": "F-D0047-029", "屏東縣": "F-D0047-033",
        "臺東縣": "F-D0047-037", "花蓮縣": "F-D0047-041", "澎湖縣": "F-D0047-045",
        "基隆市": "F-D0047-049", "新竹市": "F-D0047-053", "嘉義市": "F-D0047-057",
        "臺北市": "F-D0047-061", "高雄市": "F-D0047-065", "新北市": "F-D0047-069",
        "臺中市": "F-D0047-073", "臺南市": "F-D0047-077", "連江縣": "F-D0047-081",
        "金門縣": "F-D0047-085"
    }
    alerts = []
    target_regions_str = os.getenv('TARGET_LOCATION', '')
    if not target_regions_str: return alerts
    try:
        async with aiohttp.ClientSession() as session:
            for region in target_regions_str.split(','):
                region = region.strip()
                if '-' not in region: continue
                
                county, town = region.split('-', 1)
                county = county.replace("台", "臺") # Auto-correct variant Chinese characters
                
                dataset_id = COUNTY_MAP.get(county)
                if not dataset_id: continue
                
                url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{dataset_id}"
                
                params = {
                    "Authorization": CWA_API_KEY,
                    "LocationName": town,
                    "ElementName": "溫度"
                }
                
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        print(f"! Request failed for {county}-{town}, status code: {response.status}")
                        continue
                        
                    data = await response.json()
                    
                    locations_data = data.get("records", {}).get("Locations", [])
                    if not locations_data: continue
                        
                    county_data = locations_data[0]
                    location_list = county_data.get("Location", [])
                    
                    if not location_list:
                        print(f"! CWA could not find data for {town}.")
                        continue
                        
                    town_data = location_list[0]
                    highest_temp = 0.0
                    
                    for el in town_data.get("WeatherElement", []):
                        if el.get("ElementName") == "溫度":
                            # Township forecast provides data every 3 hours; scan the first 8 blocks (next 24 hours)
                            for time_block in el.get("Time", [])[:8]:
                                try:
                                    val = float(time_block["ElementValue"][0]["Temperature"])
                                    if val > highest_temp:
                                        highest_temp = val
                                except (IndexError, ValueError, KeyError, TypeError):
                                    continue
                            break
                            
                    print(f"> Found temperature for {county} {town}: {highest_temp if highest_temp > 0 else 'None'}")
                    
                    if highest_temp >= thresholdTemp:
                        alerts.append((county, town, highest_temp))
    except Exception as e:
        print(f"X CWA API request exception error: {e}")

    return alerts

async def fetch_crypto_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": cryptoToMonitor, "vs_currencies": cryptoToCurrency}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data[cryptoToMonitor][cryptoToCurrency])
    except Exception as e:
        print(f"Crypto API request error: {e}")
    return None

lastCryptoPrice = 0.0
sameCryptoPrice = 0

@tasks.loop(minutes=10.0)  # Check every 10 minutes to improve time accuracy
async def autoMonitor(test: bool = False):
    global last_weather_date, lastCryptoPrice, sameCryptoPrice
    try:
        now = datetime.datetime.now()
        currentHour = now.hour
        currentMinute = now.minute
        currentDate = now.date()
        threshTemp = 35.0
        threshPrice = alertThreshold

        if test:
            currentHour = 7
            currentMinute = 0
            currentDate = datetime.date(2026, 1, 23)
            threshTemp = -100.0
            threshPrice = 0.0
        user = bot.get_user(ALLOWED_USER_ID) or await bot.fetch_user(ALLOWED_USER_ID)

        # Weather alert | 7 AM
        if currentHour == 7 and (last_weather_date != currentDate or test):
            temp_alerts = await fetch_temperatures(threshTemp)
            if temp_alerts:
                alert_msgs = []
                for county, town, temp in temp_alerts:
                    alert_msgs.append(f"• **{county}{town}**: `{temp}°C`")
                msg = "⚠️ **High Temperature Alert**: The following areas are forecasted to reach or exceed the maximum temperature threshold today!\n" + "\n".join(alert_msgs)
                await user.send(msg)
            # Only update the anti-spam flag in production
            if not test:
                last_weather_date = currentDate
        
        if test:
            currentHour = 12  # 符合 10 <= hour <= 21
            currentMinute = 5 # 符合 minute < 10

        # Crypto tracking | 10 AM to 9 PM (10 to 21)
        if 10 <= currentHour <= 21 and (currentMinute < 10 or test):
            cryptoPrice = await fetch_crypto_price()
            if cryptoPrice and cryptoPrice >= threshPrice:
                price_changed = (lastCryptoPrice != cryptoPrice)
                
                if price_changed or test: # Allow test mode to pass through
                    msgToSend = f"🚀 **{cryptoToMonitor.capitalize()} Price Alert**: The price has changed, reaching `{cryptoPrice} {cryptoToCurrency.upper()}`!"
                    if lastCryptoPrice != 0.0:
                        diff = cryptoPrice - lastCryptoPrice
                        msgToSend += f"\nPrice difference: `{diff:.2f} {cryptoToCurrency.upper()}`"
                    await user.send(msgToSend)
                    if not test:
                        lastCryptoPrice = cryptoPrice
                        sameCryptoPrice = 0
                elif sameCryptoPrice >= 3:
                    msgToSend = f"📊 **{cryptoToMonitor.capitalize()} Stability Report**: Price is holding steady at `{cryptoPrice} {cryptoToCurrency.upper()}` for 3 hours. System is running normally."
                    await user.send(msgToSend)
                    if not test:
                        sameCryptoPrice = 0
                else:
                    if not test:
                        sameCryptoPrice += 1

    except Exception as e:
        print(f"Background monitoring task error: {e}")

@autoMonitor.before_loop
async def before_autoMonitor():
    # Ensure the Bot is fully ready before starting the loop
    await bot.wait_until_ready()

# calculator
@bot.command(aliases=["calculate"])
async def calc(ctx, *, expression):
    try:
        result = simple_eval(expression)
        await ctx.send(f"Calculation Result: `{result}`")
    except Exception as e:
        await ctx.send("No result, please check your expression.")

# Should I ... ?
@bot.command(name="should", aliases=["decide", "if", "hmm", "dice"])
async def decide(ctx):
    responses = [
        "1 / Yes",
        "2 / Yes",
        "3 / Yes",
        "4 / No",
        "5 / No",
        "6 / No"
    ]
    answer = random.choice(responses)
    await ctx.send(f"Probably **{answer}**")

# server functions
@bot.command(aliases=["svr", "srv", "sv", "s"])
async def server(ctx, *, function):
    if function == "status" or function == "sta":
        cpu_usage = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        ram_usage = mem.percent
        ram_total = round(mem.total / (1024**3), 1) # GB
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        temp_msg = "N/A"
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                current_temp = temps['coretemp'][0].current
                temp_msg = f"{current_temp}°C"
        except:
            pass
        if (cpu_usage > 95): # color palette: https://flatuicolors.com/palette/defo
            clr = 0x8e44ad # puρπle
        elif (cpu_usage > 85) or (ram_usage > 85):
            clr = 0xd35400 # orånʒ
        elif (cpu_usage > 50) or (ram_usage > 70):
            clr = 0xf1c40f # yeλλow
        elif (cpu_usage > 20) or (ram_usage > 40):
            clr = 0x00ff00 # miΔorι
        else:
            clr = 0x3498db # blau
        embed = discord.Embed(title="Server Status", color=clr)
        embed.add_field(name="CPU Load", value=f"`{cpu_usage}%`", inline=True)
        embed.add_field(name="CPU Temp", value=f"`{temp_msg}`", inline=True)
        embed.add_field(name="Memory", value=f"`{ram_usage}%` (of {ram_total}GB)", inline=True)
        embed.add_field(name="Disk Space", value=f"`{disk_usage}%` Used", inline=True)
        await ctx.send(embed=embed)
    elif function == "IP" or function == "ip":
        ip_address = await get_cmd_output("hostname -I | awk '{print $1}'")
        tailscale = await get_cmd_output("tailscale ip -4")
        ngrok_path = shutil.which("ngrok")
        ipMsg = f"Server local IP Address: `{ip_address}`.\n[Cockpit](https://{ip_address}:9090)"
        if(tailscale != ""):
            ipMsg += f"\nFor remote access, check Tailscace yourself or click: [Tailscale Cockpit](https://{tailscale}:9090)"
        if ngrok_path is not None:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:4040/api/tunnels", timeout=2) as response:
                        if response.status == 200:
                            data = await response.json()
                            ngrokURL = data['tunnels'][0]['public_url']
                            ipMsg += f"\n[ngrok URL]({ngrokURL})"
                        else:
                            ipMsg += "\nngrok is running but API is unreachable."
            except Exception:
                ipMsg += "\nngrok is currently offline."
            await ctx.send(ipMsg)
    elif function == "cockpit" or function == "Cockpit":
        ip_address = os.popen("hostname -I | awk '{print $1}'").read().strip()
        tailscale = os.popen("tailscale ip -4").read().strip()
        await ctx.send(f"[Here](https://{ip_address}:9090)\nFor remote access, use [Tailscale Cockpit](https://{tailscale}:9090)")
    elif function == "restart bot" or function == "rebot":
        await ctx.send("Restarting bot...")
        sys.exit(0)
    elif function == "reboot" or function == "reb":
        # Warning
        await ctx.send("⚠️ **Warning:** You are about to reboot the server.\nType `yes` within 15 seconds to confirm.")
        # Confirming "yes" is sending from the same user and channel
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'yes'
        try:
            # Wait for input
            await bot.wait_for('message', check=check, timeout=15.0)
            # if "yes"
            await ctx.send("Rebooting...")
            os.system("reboot")
        except asyncio.TimeoutError:
            # if timeout
            await ctx.send("Timeout. Reboot cancelled.")
    elif function == "shutdown" or function == "sht":
        # Warning
        await ctx.send("⚠️ **Warning:** You are about to **SHUTDOWN**, power off the server.\nYou will **not** able to do any remote control or monitoring, and this bot is likely be down.\nType `yes` within 15 seconds to confirm.")
        # Confirming "yes" is sending from the same user and channel
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'yes'
        try:
            # Wait for input
            await bot.wait_for('message', check=check, timeout=15.0)
            # if "yes"
            await ctx.send("Shutting down...")
            os.system("poweroff")
        except asyncio.TimeoutError:
            # if timeout
            await ctx.send("Timeout. Shutdown cancelled.")
    else:
        await ctx.send("""That's not a valid function. Available functions:\n```\n
status       - Show server status
               alias: sta
ip           - Show server local IP address
cockpit      - Show Cockpit link
restart bot  - Restart the bot process
               alias: rebot
reboot       - Reboot the server (Requires confirmation)
               alias: reb
shutdown     - Shutdown the server (Requires confirmation)
               alias: sht
```""")

# Wi-Fi Hotspot activation
@bot.command(aliases=["wifi"])
async def hotspot(ctx, *, function="tog"):
    global hotspot_tog
    Location = os.getenv('REPO_PATH')
    if(function == "on"):
        await ctx.send("Turning hotspot on...")
        os.system(f"sudo bash {Location}/hotspot.sh")
        await ctx.send(f"Command sent.\nIf Wi-Fi isn't available, please connect to server via cockpit and try running `{Location}/hotspot.sh` manually.")
        hotspot_tog = True
    elif(function == "off"):
        await ctx.send("Turning hotspot off...")
        os.system(f"sudo bash {Location}/hotspot_off.sh")
        await ctx.send(f"Command sent.\nIf Wi-Fi is still available, please connect to server via cockpit and try running `{Location}/hotspot_off.sh` manually.")
        hotspot_tog = False
    else:
        response = "Togging hotspot. Current state in record: "
        if(hotspot_tog):
            await ctx.send(response + "`on`.\nTurning off...")
            os.system(f"sudo bash {Location}/hotspot_off.sh")
            await ctx.send(f"Command sent and record updated.\nIf Wi-Fi is still available, please connect to server via cockpit and try running `{Location}/hotspot_off.sh` manually.")
            hotspot_tog = False
        else:
            await ctx.send(response + "`off`.\nTurning on...")
            os.system(f"sudo bash {Location}/hotspot.sh")
            await ctx.send(f"Command sent and record updated.\nIf Wi-Fi isn't available, please connect to server via cockpit and try running `{Location}/hotspot.sh` manually.")
            hotspot_tog = True

# No comment needed
@bot.command()
async def ping(ctx):
    await ctx.send("Pong ♪")

@bot.command()
async def statusRainbow(ctx):
    clr = [0x8e44ad, 0xd35400, 0xf1c40f, 0x00ff00, 0x3498db]
    txt = ["RA", "IN", "B", "O", "W"]
    for text, calr in zip(txt, clr):
        embed = discord.Embed(title=text, color=calr)
        await ctx.send(embed=embed)

@bot.command(aliases=["hepp", "cmds", "cmd"])
async def commands(ctx):
    help_text = """
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
statusRainbow      - Show every color \">server status\" will send
author             - Show bot author information
wake               - Remote booting PC
testNotif          - Test notification system"""
    await ctx.send(f"## Available commands:\n```{help_text}```")

# Author
@bot.command()
async def author(ctx):
    await ctx.send("## Discord Bot by [theArnoll](https://github.com/theArnoll)\nBot repo is located at [here](https://github.com/theArnoll/serverboxDCutil)")

@bot.command()
async def wake(ctx):
    send_magic_packet(MAC)
    await ctx.send(f"Remote booted PC.")

@bot.command()
async def testNotif(ctx):
    await ctx.send("Running full integration test for monitor system...")
    await autoMonitor.coro(True)

bot.run(TOKEN)