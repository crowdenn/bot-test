import discord
import os
from discord.ext import tasks, commands
from flask import Flask
from threading import Thread

# --- 1. WEB SERVER (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Project is runnin and goin!"

def run():
    # Render uses the PORT env variable; we default to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. DISCORD BOT SETUP ---
intents = discord.Intents.default()
# You don't strictly need message_content just to SEND messages, 
# but it's good to have for future commands.
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# This is your "setInterval" equivalent in Python
@tasks.loop(minutes=10)
async def beep_loop():
    channel_id = 1364299553733345393  # Keep this as an integer, no quotes
    channel = bot.get_channel(channel_id)
    
    if channel:
        await channel.send("beep beep")
        print("Sent beep beep!")
    else:
        print("Channel not found! Make sure the ID is correct and the bot is in the server.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Start the loop when the bot is ready
    if not beep_loop.is_running():
        beep_loop.start()

# --- 3. START EVERYTHING ---
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))