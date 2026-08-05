import discord
import os
import random
import asyncio
import logging
from discord.ext import commands
from flask import Flask
from threading import Thread

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 1. CONFIGURATION ---
BEEP_CHANNEL_ID = 1500916551031980052
PROMO_CHANNEL_IDS = [1500852876245729390, 1500912425900179598]
ADMIN_USER_ID = 666000585266561034

PROMO_MESSAGES = [
    "SUBSCRIBE to support the stream and get access to awesome emotes!",
    "Did you know you can subscribe for FREE!? With Twitch Prime: <http://www.twitchprime.com/>",
    "Enter a message"
]

HYPE_THRESHOLD = 50
PROMO_WINDOW = 1200

# --- 2. STATE MANAGEMENT ---
channel_hype = {cid: 0 for cid in PROMO_CHANNEL_IDS}
window_start_time = {cid: time.time() for cid in PROMO_CHANNEL_IDS}
current_voice_client = None

# --- 3. WEBSERVER (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running."

def run_webserver():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

def keep_alive():
    Thread(target=run_webserver, daemon=True).start()
    logger.info("Webserver started on background thread")

# --- 4. BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- 5. PROMO & MESSAGE HANDLING ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    cid = message.channel.id
    
    if cid in PROMO_CHANNEL_IDS:
        current_time = time.time()
        
        # Reset window if expired
        if current_time - window_start_time[cid] > PROMO_WINDOW:
            channel_hype[cid] = 0
            window_start_time[cid] = current_time
        
        channel_hype[cid] += 1
        
        if channel_hype[cid] >= HYPE_THRESHOLD:
            try:
                await message.channel.send(random.choice(PROMO_MESSAGES))
                channel_hype[cid] = 0
                window_start_time[cid] = current_time
            except Exception as e:
                logger.error(f"Promo message failed: {e}")

    await bot.process_commands(message)

# --- 6. BEEP LOOP (ASYNC TASK) ---
async def beep_scheduler():
    """Runs beep loop outside of tasks framework to avoid overhead."""
    while True:
        wait_time = random.randint(600, 2700)
        logger.debug(f"Next beep in {wait_time}s ({wait_time/60:.1f} min)")
        await asyncio.sleep(wait_time)
        
        # Text beep
        try:
            channel = bot.get_channel(BEEP_CHANNEL_ID)
            if channel:
                await channel.send("beep beep")
                logger.info("Text beep sent")
        except Exception as e:
            logger.error(f"Text beep error: {e}")

        # Voice beep
        global current_voice_client
        if current_voice_client and current_voice_client.is_connected():
            try:
                if not current_voice_client.is_playing():
                    source = discord.FFmpegPCMAudio(
                        'beep.mp3',
                        options="-loglevel panic",
                        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
                    )
                    current_voice_client.play(source)
                    logger.info("Voice beep played")
            except Exception as e:
                logger.error(f"Voice beep error: {e}")

# --- 7. COMMANDS ---
@bot.command(name="beep")
async def manual_beep(ctx):
    if ctx.author.id != ADMIN_USER_ID:
        logger.debug(f"Unauthorized beep attempt by {ctx.author.id}")
        return

    logger.info(f"Manual beep triggered by {ctx.author}")
    
    # Text beep
    try:
        channel = bot.get_channel(BEEP_CHANNEL_ID)
        if channel:
            await channel.send("beep beep (manual)")
    except Exception as e:
        logger.error(f"Manual text beep error: {e}")

    # Voice beep
    v_client = current_voice_client or ctx.voice_client
    if v_client and v_client.is_connected():
        try:
            if not v_client.is_playing():
                source = discord.FFmpegPCMAudio('beep.mp3', options="-loglevel panic")
                v_client.play(source)
                logger.info("Manual voice beep played")
        except Exception as e:
            logger.error(f"Manual voice beep error: {e}")

@bot.command(name="join")
async def join_command(ctx):
    global current_voice_client
    
    # Disconnect if already joined
    if ctx.voice_client:
        try:
            await ctx.voice_client.disconnect()
            current_voice_client = None
            await ctx.send("Left voice channel.")
            logger.info("Bot disconnected from voice channel")
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
        return

    # Check if user is in voice channel
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel for me to join!")
        return

    channel = ctx.author.voice.channel
    try:
        current_voice_client = await channel.connect()
        await ctx.send(f"Joined {channel.name}!")
        logger.info(f"Bot joined voice channel: {channel.name}")
    except Exception as e:
        await ctx.send(f"Failed to join: {e}")
        logger.error(f"Join error: {e}")

@bot.command(name="lifesteal")
async def lifesteal_command(ctx):
    try:
        await ctx.message.delete()
        duration = datetime.timedelta(minutes=10)
        await ctx.author.timeout(duration, reason="void.")
        logger.info(f"User {ctx.author} timed out for 10 minutes")
    except Exception as e:
        logger.error(f"Timeout failed: {e}")

# --- 8. STARTUP ---
@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    asyncio.create_task(beep_scheduler())

if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        logger.error("No DISCORD_TOKEN found in environment variables.")
