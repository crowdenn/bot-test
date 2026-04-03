import discord
import os
import random
import asyncio
import datetime
import time
from discord.ext import tasks, commands
from flask import Flask
from threading import Thread

# --- 1. CONFIGURATION ---
BEEP_CHANNEL_ID = 1364219102662754405
PROMO_CHANNEL_IDS = [1395842773562822696, 1363954478847627375]

PROMO_MESSAGES = [
    "SUBCRIBE to support the stream and get access to awesome emotes!",
    "Did you know you can subscribe for FREE!? With Twitch Prime: <http://www.twitchprime.com/>",
    "Enter a message"
]

# Logic Settings
HYPE_THRESHOLD = 15      # Messages required
PROMO_COOLDOWN = 1200    # Seconds (20 minutes)

# Tracking data
channel_hype = {cid: 0 for cid in PROMO_CHANNEL_IDS}
last_promo_time = {cid: 0 for cid in PROMO_CHANNEL_IDS}

# --- 2. WEB SERVER (KEEP ALIVE) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running."

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- 3. BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 4. ACTIVITY & PROMO LOGIC ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    cid = message.channel.id
    if cid in PROMO_CHANNEL_IDS:
        channel_hype[cid] += 1
        
        current_time = time.time()
        time_diff = current_time - last_promo_time.get(cid, 0)

        # Trigger check: Both requirements must be met
        if channel_hype[cid] >= HYPE_THRESHOLD and time_diff >= PROMO_COOLDOWN:
            await message.channel.send(random.choice(PROMO_MESSAGES))
            channel_hype[cid] = 0 
            last_promo_time[cid] = current_time

    await bot.process_commands(message)

# --- 5. THE RANDOM BEEP LOOP ---
@tasks.loop(seconds=1) 
async def beep_loop():
    wait_time = random.randint(600, 2700) 
    await asyncio.sleep(wait_time)
    
    channel = bot.get_channel(BEEP_CHANNEL_ID)
    if channel:
        try:
            await channel.send("beep beep")
        except Exception as e:
            print(f"Beep error: {e}")

# --- 6. COMMANDS ---
@bot.command(name="lifesteal")
async def lifesteal(ctx):
    try:
        await ctx.message.delete()
        duration = datetime.timedelta(minutes=10)
        await ctx.author.timeout(duration, reason="void.")
    except Exception:
        pass 

# --- 7. STARTUP ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    if not beep_loop.is_running():
        beep_loop.start()

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('DISCORD_TOKEN'))
