import discord
from discord.ext import commands
import random
import psutil  # 抓系統資訊的神器
import os
from dotenv import load_dotenv
from simpleeval import simple_eval
import asyncio
import sys

load_dotenv()

# Configurations
TOKEN = os.getenv('DC_TOKEN')
ALLOWED_USER_ID = int(os.getenv('ALLOWED_USER_ID'))
bot = commands.Bot(command_prefix='>', intents=discord.Intents.all())
# '>' is the command prefix

@bot.event
async def on_ready():
    print(f'DC tool is now online: {bot.user}')
    # Bot status (ex. Playing N100 Server)
    # await bot.change_presence(activity=discord.Game(name="N100 Server"))

# Check if the user is allowed
@bot.check
async def globally_block_strangers(ctx):
    return ctx.author.id == ALLOWED_USER_ID

# calculator
@bot.command()
async def calc(ctx, *, expression):
    try:
        result = simple_eval(expression)
        await ctx.send(f"Calculation Result: `{result}`")
    except Exception as e:
        await ctx.send("No result, please check your expression.")

# Should I ... ?
@bot.command(name="should")  # 指定指令名稱
async def decide(ctx, *, question):
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
@bot.command()
async def server(ctx, *, function):
    if function == "status":
        # 1. CPU Usage
        cpu_usage = psutil.cpu_percent(interval=1)
        # 2. RAM Usage
        mem = psutil.virtual_memory()
        ram_usage = mem.percent
        ram_total = round(mem.total / (1024**3), 1) # GB
        # 3. Disk Usage
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        # 4. Linux CPU temp
        temp_msg = "N/A"
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                current_temp = temps['coretemp'][0].current
                temp_msg = f"{current_temp}°C"
        except:
            pass
        # Making an embed message
        embed = discord.Embed(title="Server Status", color=0x00ff00)
        embed.add_field(name="CPU Load", value=f"`{cpu_usage}%`", inline=True)
        embed.add_field(name="CPU Temp", value=f"`{temp_msg}`", inline=True)
        embed.add_field(name="Memory", value=f"`{ram_usage}%` (of {ram_total}GB)", inline=False)
        embed.add_field(name="Disk Space", value=f"`{disk_usage}%` Used", inline=True)
        await ctx.send(embed=embed)
    elif function == "IP" or function == "ip":
        ip_address = os.popen("hostname -I | awk '{print $1}'").read().strip()
        tailscale = os.popen("tailscale ip -4").read().strip()
        await ctx.send(f"Server local IP Address: `{ip_address}`.\n[Cockpit](https://{ip_address}:9090)\nFor remote access, check Tailscace yourself and access by:")
        # await ctx.send(f"{tailscale}")
        # await ctx.send("↑ Long press to copy.")
        await ctx.send(f"[Tailscale Cockpit](https://{tailscale}:9090)")
    elif function == "cockpit" or function == "Cockpit":
        ip_address = os.popen("hostname -I | awk '{print $1}'").read().strip()
        await ctx.send(f"[Here](https://{ip_address}:9090)\nFor remote access, check Tailscace and access by:")
        await ctx.send("100.x.x.x:9090")
        await ctx.send("↑ Long press to copy.")
    elif function == "restart bot":
        await ctx.send("Restarting bot...")
        sys.exit(0)
    elif function == "reboot":
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
    elif function == "shutdown":
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

@bot.command()
async def Server(ctx, *, function):  #for if phone
    if function == "status":
        # 1. CPU Usage
        cpu_usage = psutil.cpu_percent(interval=1)
        # 2. RAM Usage
        mem = psutil.virtual_memory()
        ram_usage = mem.percent
        ram_total = round(mem.total / (1024**3), 1) # GB
        # 3. Disk Usage
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        # 4. Linux CPU temp
        temp_msg = "N/A"
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                current_temp = temps['coretemp'][0].current
                temp_msg = f"{current_temp}°C"
        except:
            pass
        # Making an embed message
        embed = discord.Embed(title="Server Status", color=0x00ff00)
        embed.add_field(name="CPU Load", value=f"`{cpu_usage}%`", inline=True)
        embed.add_field(name="CPU Temp", value=f"`{temp_msg}`", inline=True)
        embed.add_field(name="Memory", value=f"`{ram_usage}%` (of {ram_total}GB)", inline=False)
        embed.add_field(name="Disk Space", value=f"`{disk_usage}%` Used", inline=True)
        await ctx.send(embed=embed)
    elif function == "IP" or function == "ip":
        ip_address = os.popen("hostname -I | awk '{print $1}'").read().strip()
        await ctx.send(f"Server local IP Address: `{ip_address}`.\n[Cockpit](https://{ip_address}:9090)\nFor remote access, check Tailscace yourself and access by:")
        await ctx.send("100.x.x.x:9090")
        await ctx.send("↑ Long press to copy.")
    elif function == "cockpit" or function == "Cockpit":
        ip_address = os.popen("hostname -I | awk '{print $1}'").read().strip()
        await ctx.send(f"[Here](https://{ip_address}:9090)\nFor remote access, check Tailscace and access by:")
        await ctx.send("100.x.x.x:9090")
        await ctx.send("↑ Long press to copy.")
    elif function == "restart bot":
        await ctx.send("Restarting bot...")
        sys.exit(0)
    elif function == "reboot":
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
    elif function == "shutdown":
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

# Wi-Fi Hotspot activation
@bot.command()
async def hotspot(ctx):
    await ctx.send("Turning hotspot on...")
    Location = os.getenv('REPO_PATH')
    os.system(f"sudo bash {Location}/hotspot.sh")
    await ctx.send(f"Command sent.\nIf Wi-Fi isn't available, please check the server by cockpit and try manually run `{Location}/hotspot.sh.`")

# No comment needed
@bot.command()
async def ping(ctx):
    await ctx.send("Pong ♪")

@bot.command()
async def commands(ctx):
    help_text = """
calc <expression>  - Calculate the expression
should             - Basically a dice
server <function>  - Server related functions:
    status       - Show server status
    ip           - Show server local IP address
    cockpit      - Show Cockpit link
    restart bot  - Restart the bot process
    reboot       - Reboot the server (Requires confirmation)
    shutdown     - Shutdown the server (Requires confirmation)
hotspot            - Turn on Wi-Fi hotspot
ping               - Pong ♪
help               - Show built-in help message
commands           - Show this command list
author             - Show bot author information"""
    await ctx.send(f"## Available commands:\n```{help_text}```")

# Author
@bot.command()
async def author(ctx):
    await ctx.send("## Discord Bot by [theArnoll](https://github.com/theArnoll)\nBot repo is located at [here](https://github.com/theArnoll/serverboxDCutil)")


bot.run(TOKEN)
