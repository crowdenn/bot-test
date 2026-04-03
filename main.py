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

# Your specific promo messages
PROMO_MESSAGES = [
    "SUBCRIBE to support the stream and get access to awesome emotes!",
    "Did you know you can subscribe for FREE!? With Twitch Prime: <http://www.twitchprime.com/>",
    "Enter a message"
]

# Logic Settings
HYPE_THRESHOLD = 15      # Messages required before a promo
PROMO_COOLDOWN = 1200    # Seconds to wait (20 minutes) between promos

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

    # Check if message is in one of the promo target channels
    if message.channel.id in PROMO_CHANNEL_IDS:
        cid = message.channel.id
        channel_hype[cid] += 1
        
        current_time = time.time()
        time_diff = current_time - last_promo_time.get(cid, 0)

        # TRIGGER CHECK: Both message count AND time must be met
        if channel_hype[cid] >= HYPE_THRESHOLD and time_diff >= PROMO_COOLDOWN:
            await message.channel.send(random.choice(PROMO_MESSAGES))
            # Reset trackers
            channel_hype[cid] = 0 
            last_promo_time[cid] = current_time

    await bot.process_commands(message)

# --- 5. THE RANDOM BEEP LOOP ---
@tasks.loop(seconds=1) 
async def beep_loop():
    # Wait between 10 and 45 minutes
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
        # Silently delete the user's message
        await ctx.message.delete()
        
        # Apply 10 minute timeout
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
    bot.run(os.getenv('DISCORD_TOKEN'))    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- 3. BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 4. UPDATED ACTIVITY & PROMO LOGIC ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if message is in one of the promo target channels
    if message.channel.id in PROMO_CHANNEL_IDS:
        cid = message.channel.id
        channel_hype[cid] += 1
        
        current_time = time.time()
        time_diff = current_time - last_promo_time.get(cid, 0)

        # Trigger only if BOTH the message count AND the time cooldown are met
        if channel_hype[cid] >= HYPE_THRESHOLD and time_diff >= PROMO_COOLDOWN:
            await message.channel.send(random.choice(PROMO_MESSAGES))
            # Reset both trackers
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
        # Delete the command message
        await ctx.message.delete()
        
        # Timeout the user for 10 minutes
        duration = datetime.timedelta(minutes=10)
        await ctx.author.timeout(duration, reason="void.")
        
        # No confirmation message is sent (Silent Mode)
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
    bot.run(os.getenv('DISCORD_TOKEN'))def keep_alive():
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

    # Check if message is in one of the promo target channels
    if message.channel.id in PROMO_CHANNEL_IDS:
        cid = message.channel.id
        channel_hype[cid] += 1
        
        # If enough people have talked, roll for a promo
        if channel_hype[cid] >= HYPE_THRESHOLD:
            channel_hype[cid] = 0 # Reset counter
            if random.random() < PROMO_CHANCE:
                await message.channel.send(random.choice(PROMO_MESSAGES))

    await bot.process_commands(message)

# --- 5. THE RANDOM BEEP LOOP ---
@tasks.loop(seconds=1) 
async def beep_loop():
    # Wait between 10 and 45 minutes (600 to 2700 seconds)
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
        # Delete the user's command message
        await ctx.message.delete()
        
        # Timeout the user for 10 minutes
        duration = datetime.timedelta(minutes=10)
        await ctx.author.timeout(duration, reason="void.")
        
        # Confirmation message removed for a "silent" effect
    except Exception:
        # Fails silently if bot lacks 'Manage Messages' or 'Moderate Members' permissions
        pass 

# --- 7. STARTUP ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    if not beep_loop.is_running():
        beep_loop.start()

if __name__ == "__main__":
    keep_alive()
    # Ensure DISCORD_TOKEN is set in your environment variables/Secrets
    bot.run(os.getenv('DISCORD_TOKEN'))
