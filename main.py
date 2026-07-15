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
BEEP_CHANNEL_ID = 1500916551031980052
PROMO_CHANNEL_IDS = [1500852876245729390, 1500912425900179598]
TARGET_USER_ID = 666000585266561034

current_voice_client = None
PROMO_MESSAGES = [
    "SUBCRIBE to support the stream and get access to awesome emotes!",
    "Did you know you can subscribe for FREE!? With Twitch Prime: <http://www.twitchprime.com/>",
    "Enter a message"
]

HYPE_THRESHOLD = 50     
PROMO_WINDOW = 1200       
channel_hype = {cid: 0 for cid in PROMO_CHANNEL_IDS}
window_start_time = {cid: time.time() for cid in PROMO_CHANNEL_IDS}

# --- 2. WEB SERVER ---
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
intents.voice_states = True 
intents.members = True # Required to fetch member timeout status
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 4. SILENT UNTIMEOUT LOGIC ---
async def clear_my_timeout():
    for guild in bot.guilds:
        try:
            member = await guild.fetch_member(TARGET_USER_ID)
            if member and member.is_timed_out():
                await member.edit(timed_out_until=None, reason="Startup silent cleanup.")
        except:
            continue

# --- 5. ACTIVITY & PROMO LOGIC ---
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

# --- 6. BEEP LOOP ---
@tasks.loop(seconds=1) 
async def beep_loop():
    wait_time = random.randint(600, 2700) 
    await asyncio.sleep(wait_time)
    channel = bot.get_channel(BEEP_CHANNEL_ID)
    if channel:
        try: await channel.send("beep beep")
        except: pass
    global current_voice_client
    if current_voice_client and current_voice_client.is_connected():
        if not current_voice_client.is_playing():
            source = discord.FFmpegPCMAudio('beep.mp3', options="-loglevel panic", before_options="-reconnect 1")
            current_voice_client.play(source)

# --- 7. COMMANDS ---
@bot.command(name="beep")
async def manual_beep(ctx):
    if ctx.author.id != TARGET_USER_ID: return
    channel = bot.get_channel(BEEP_CHANNEL_ID)
    if channel: await channel.send("beep beep (manual)")
    v_client = current_voice_client or ctx.voice_client
    if v_client and v_client.is_connected() and not v_client.is_playing():
        v_client.play(discord.FFmpegPCMAudio('beep.mp3', options="-loglevel panic"))

@bot.command(name="join")
async def join(ctx):
    global current_voice_client
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        current_voice_client = None
        return
    if ctx.author.voice:
        current_voice_client = await ctx.author.voice.channel.connect()

@bot.command(name="lifesteal")
async def lifesteal(ctx):
    try:
        await ctx.message.delete()
        await ctx.author.timeout(datetime.timedelta(minutes=10), reason="void.")
    except: pass

# --- 8. STARTUP ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Run the silent untimeout
    await clear_my_timeout()
    if not beep_loop.is_running():
        beep_loop.start()

if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
