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
# Track voice connection
current_voice_client = None

PROMO_MESSAGES = [
    "SUBCRIBE to support the stream and get access to awesome emotes!",
    "Did you know you can subscribe for FREE!? With Twitch Prime: <http://www.twitchprime.com/>",
    "Enter a message"
]

# Logic Settings
HYPE_THRESHOLD = 50     
PROMO_WINDOW = 1200      

# Tracking data
channel_hype = {cid: 0 for cid in PROMO_CHANNEL_IDS}
window_start_time = {cid: time.time() for cid in PROMO_CHANNEL_IDS}

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
        current_time = time.time()
        
        if current_time - window_start_time[cid] > PROMO_WINDOW:
            channel_hype[cid] = 0
            window_start_time[cid] = current_time
        
        channel_hype[cid] += 1
        
        if channel_hype[cid] >= HYPE_THRESHOLD:
            await message.channel.send(random.choice(PROMO_MESSAGES))
            channel_hype[cid] = 0 
            window_start_time[cid] = current_time

    await bot.process_commands(message)

# --- 5. THE RANDOM BEEP LOOP ---
@tasks.loop(seconds=1) 
async def beep_loop():
    # Wait between 10 to 45 minutes
    wait_time = random.randint(600, 2700) 
    await asyncio.sleep(wait_time)
    
    # 1. Text Beep
    channel = bot.get_channel(BEEP_CHANNEL_ID)
    if channel:
        try:
            await channel.send("beep beep")
        except Exception as e:
            print(f"Beep error: {e}")

    # 2. Voice Beep (Synced)
    if current_voice_client and current_voice_client.is_connected():
        try:
            # Ensure path to 'beep.mp3' is correct
            source = discord.FFmpegPCMAudio('beep.mp3')
            if not current_voice_client.is_playing():
                current_voice_client.play(source)
        except Exception as e:
            print(f"Voice playback error: {e}")

# --- 6. COMMANDS ---
@bot.command(name="join")
async def join(ctx):
    global current_voice_client
    
    # If bot is already in a voice channel, leave it
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        current_voice_client = None
        await ctx.send("Left voice channel.")
        return

    # Check if user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel for me to join!")
        return

    channel = ctx.author.voice.channel
    current_voice_client = await channel.connect()
    await ctx.send(f"Joined {channel.name}!")
    
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
