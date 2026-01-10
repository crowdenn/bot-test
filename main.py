import discord
import os
import random
import asyncio
from discord.ext import tasks, commands
from flask import Flask
from threading import Thread

# --- 1. WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Project is runnin and goin!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True # Needed to mute/manage members

bot = commands.Bot(command_prefix="!", intents=intents)

# --- 3. RANDOM BEEP LOOP ---
@tasks.loop(seconds=1) # We run it frequently but use logic to decide when to beep
async def beep_loop():
    channel_id = 1364299553733345393
    channel = bot.get_channel(channel_id)
    
    # Wait for a random time between 1 and 10 minutes (60 to 600 seconds)
    wait_time = random.randint(60, 600)
    await asyncio.sleep(wait_time)
    
    if channel:
        await channel.send("beep beep")
        print(f"Sent beep beep after waiting {wait_time}s")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    if not beep_loop.is_running():
        beep_loop.start()

# --- 4. THE LIFESTEAL MUTE LOGIC ---
@bot.event
async def on_message(message):
    # Don't let the bot mute itself
    if message.author == bot.user:
        return

    # Check for !lifesteal (case insensitive)
    if "!lifesteal" in message.content.lower():
        try:
            # This "mutes" them by removing their ability to send messages in the server
            # Note: The bot needs 'Manage Roles' or 'Moderate Members' permission!
            await message.author.timeout(discord.utils.utcnow() + asyncio.timedelta(minutes=10), reason="Said !lifesteal")
            await message.channel.send(f"{message.author.mention} test")
        except Exception as e:
            await message.channel.send("I tried to mute them, but I don't have enough permissions!")
            print(f"Error: {e}")

    # This line ensures other commands (like !ping) still work
    await bot.process_commands(message)

# --- START ---
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
