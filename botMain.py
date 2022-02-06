############################################
# Minecraft Server Management              #
# By BetaTester41                          #
# Modified on: 1/26/2022                   #
# DO NOT REMOVE THIS NOTICE OR THE CREDITS #
############################################

# Import things needed for this program
import discord
import socket
import os
from discord.ext import commands , tasks
from asyncio import sleep
from mcstatus import MinecraftBedrockServer
from os.path import exists
from datetime import datetime

# Initialize the bot and variables
bot = commands.Bot(command_prefix='.')
bot.mcServer = "geo.hivebedrock.network:19132"
bot.startCmd = "wakeonlan 8D:WHAT:EVER:YOUR:MAC:IS"
bot.footerTxt = "ServerStats • v0.41-beta • BetaTester41"
bot.authorPage = ""
token = ""

# Colors
bot.colorError = discord.Color.red()
bot.colorSuccess = discord.Color.green()
bot.colorWarning = discord.Color.yellow()
bot.colorInfo = discord.Color.blue()

# Make sure files are stored in the same folder as this script
if os.path.dirname(os.path.abspath(__file__)) != os.path.abspath(os.getcwd()):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create date file for the server
if not exists("date.txt"):
    with open("date.txt", "w") as f:
        f.write("")

# Make sure token works properly
if not exists("token.txt"):
    with open("token.txt", "w") as f:
        while True:
            token = input("Enter your bot token: ")
            if len(token) == 59:
                f.write(token)
                break
            else:
                print("Invalid token length. Please try again.")
else:
    with open("token.txt", "r") as f:
        token = f.read()
        if len(token) != 59:
            while True:
                token = input("Invalid token length. Please try again: ")
                if len(token) == 59:
                    with open("token.txt", "w") as f:
                        f.write(token)
                    break
                else:
                    print("Invalid token length. Please try again.")

# Dynamically make embeds to shorten code
def embedMaker(title, description, color, thumbnail = None):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_author(name="Server Operations", url=bot.authorPage, icon_url="https://yt3.ggpht.com/a/AGF-l7-C1i8-8VAu1IsFjqh5HxDHzu0MxaxTqobTOg")
    embed.set_footer(text=bot.footerTxt)
    if thumbnail != None:
        embed.set_thumbnail(url=thumbnail)
    return embed

# Chnage bot status every 1 minute
@tasks.loop(minutes=3)
async def status_update():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="the server's heartbeat."))
    await sleep(60)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the server for errors."))
    await sleep(60)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name="the new v0.41 update.", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"))

# Show message on bot login
@bot.event
async def on_ready():
    print(f"Bot started as {bot.user}")
    status_update.start()

# Sets up the .start command
@bot.command(alias=['start'])
async def start(ctx, override = None):
    if ctx.author == bot.user:
        await ctx.reply(embed=embedMaker("Error!", "A bot can't start the server", bot.colorError))
        return
    if not ctx.message.author.guild_permissions.administrator:
        if not ctx.channel.name.startswith(("bot","command","cmd")):
            await ctx.reply(embed=embedMaker("Error!", "Commands are not allowed in this channel! Please use #commands", bot.colorError))
            return
    if override == "override":
        os.system(bot.startCmd)
        return
    with open('date.txt', 'r') as f:
        date = f.read()
        if date == datetime.today().strftime('%Y%m%d'):
            await ctx.reply(embed=embedMaker("Error!", "The server is already running! If you believe this is a mistake, please contact the admin.", bot.colorError))
        else:
            os.system(bot.startCmd)
            await ctx.reply(embed=embedMaker("Running Command...", "The server is now starting... This may take a while (up to 5 mins)", bot.colorSuccess))
            with open('date.txt', 'w') as f:
                f.write(datetime.today().strftime('%Y%m%d'))

# Sets up the .check command
@bot.command(alias=['check'])
async def check(ctx):
    if ctx.author == bot.user:
        await ctx.reply(embed=embedMaker("Error!", "A bot can't start the server", bot.colorError))
        return
    if not ctx.message.author.guild_permissions.administrator:
        if not ctx.channel.name.startswith(("bot","command","cmd")):
            await ctx.reply(embed=embedMaker("Error!", "Commands are not allowed in this channel! Please use #commands", bot.colorError))
            return
    sentReply = await ctx.reply(embed=embedMaker("Checking...", "Checking the server's status...", bot.colorInfo, "https://cdn.discordapp.com/attachments/932037238525685781/933860786999267358/sunflower_front.png"))
    try:
        bedrock = MinecraftBedrockServer.lookup(bot.mcServer)
    except ValueError:
        await sentReply.edit(embed=embedMaker("Error!", "An error occurred while looking up the server.", bot.colorError, "https://cdn.discordapp.com/attachments/932037238525685781/933860786999267358/sunflower_front.png"))
        return
    try:
        status = bedrock.status()
    except socket.gaierror:
        await sentReply.edit(embed=embedMaker("Error!", "The hostname can't be resolved.", bot.colorError, "https://cdn.discordapp.com/attachments/932037238525685781/933860786999267358/sunflower_front.png"))
        return
    except TimeoutError:
        await sentReply.edit(embed=embedMaker("Error!", "The server is not responding.", bot.colorError, "https://cdn.discordapp.com/attachments/932037238525685781/933860786999267358/sunflower_front.png"))
        return
    except socket.error:
        await sentReply.edit(embed=embedMaker("Checkup Report", "The server seems to be off.", bot.colorError, "https://cdn.discordapp.com/attachments/932037238525685781/933860786999267358/sunflower_front.png"))
        return
    embed = discord.Embed(title="Checkup Report", description="Displaying information for: `" + bot.mcServer + "`" , color=bot.colorSuccess)
    embed.set_author(name="Server Operations", url=bot.authorPage, icon_url="https://yt3.ggpht.com/a/AGF-l7-C1i8-8VAu1IsFjqh5HxDHzu0MxaxTqobTOg")
    embed.set_footer(text=bot.footerTxt)
    embed.add_field(name="Latency", value=str("`" + str(round(status.latency, 2)) + "` ms."))
    embed.add_field(name="Software", value=str("The server is running\n \"" + str(status.version.brand) + "\", version \"" + str(status.version.version) + "\"."))
    embed.add_field(name="Player Count", value=str("`" + str(status.players_online) + "` / `" + str(status.players_max) + "`"))
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/932037238525685781/933860786999267358/sunflower_front.png")
    await sentReply.edit(embed=embed)

bot.run(token)
