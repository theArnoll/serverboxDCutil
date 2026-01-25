import discord
from discord.ext import commands
import random
import psutil  # sysinfo
import os
from dotenv import load_dotenv
from simpleeval import simple_eval
import asyncio
import sys

load_dotenv()

# Configurations
TOKEN = os.getenv('DC_TOKEN')
ALLOWED_USER_ID = int(os.getenv('ALLOWED_USER_ID'))
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

# Check if the user is allowed
@bot.check
async def globally_block_strangers(ctx):
    return ctx.author.id == ALLOWED_USER_ID

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
        ip_address = os.popen("hostname -I | awk '{print $1}'").read().strip()
        tailscale = os.popen("tailscale ip -4").read().strip()
        await ctx.send(f"Server local IP Address: `{ip_address}`.\n[Cockpit](https://{ip_address}:9090)\nFor remote access, check Tailscace yourself or click:")
        await ctx.send(f"[Tailscale Cockpit](https://{tailscale}:9090)")
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
reboot       - Reboot the server (Requires confirmation)
               alias: reb
shutdown     - Shutdown the server (Requires confirmation)
               alias: sht
```""")

# Wi-Fi Hotspot activation
@bot.command(aliases=["wifi"])
async def hotspot(ctx):
    await ctx.send("Turning hotspot on...")
    Location = os.getenv('REPO_PATH')
    os.system(f"sudo bash {Location}/hotspot.sh")
    await ctx.send(f"Command sent.\nIf Wi-Fi isn't available, please check the server by cockpit and try manually run `{Location}/hotspot.sh.`")

# No comment needed
@bot.command()
async def ping(ctx):
    await ctx.send("Pong ♪")

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
hotspot            - Turn on Wi-Fi hotspot
                     aliases: wifi
ping               - Pong ♪
help               - Show built-in help message
commands           - Show this command list
                     aliases: hepp, cmds, cmd
author             - Show bot author information"""
    await ctx.send(f"## Available commands:\n```{help_text}```")

# Author
@bot.command()
async def author(ctx):
    await ctx.send("## Discord Bot by [theArnoll](https://github.com/theArnoll)\nBot repo is located at [here](https://github.com/theArnoll/serverboxDCutil)")


bot.run(TOKEN)
