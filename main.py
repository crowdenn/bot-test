import discord
import os
import random
import asyncio
from discord.ext import tasks, commands
from flask import Flask
from threading import Thread

# --- 1. WEB SERVER (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Project is runnin and goin!"

def run():
    # Use the port Render provides or default to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True  # Required to read commands
intents.members = True          # Required for timeouts/muting

bot = commands.Bot(command_prefix="!", intents=intents)

# --- 3. RANDOM BEEP LOOP ---
@tasks.loop(seconds=1) 
async def beep_loop():
    channel_id = 1364299553733345393
    channel = bot.get_channel(channel_id)
    
    # Wait for a random time between 1 and 10 minutes
    wait_time = random.randint(60, 600)
    await asyncio.sleep(wait_time)
    
    if channel:
        try:
            await channel.send("beep beep")
            print(f"Sent beep beep after waiting {wait_time}s")
        except Exception as e:
            print(f"Loop error: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    if not beep_loop.is_running():
        beep_loop.start()

# --- 4. THE LIFESTEAL COMMAND ---
@bot.command(name="lifesteal")
async def lifesteal(ctx):
    # The bot cannot mute the Server Owner or itself
    if ctx.author == bot.user:
        return

    try:
        # Timeout for 10 minutes
        duration = asyncio.timedelta(minutes=10)
        await ctx.author.timeout(duration, reason="Used !lifesteal command")
        await ctx.send(f"🔇 {ctx.author.mention} has been muted for 10 minutes.")
    
    except discord.Forbidden:
        # This triggers if the bot's role is too low
        await ctx.send("❌ **Permission Error:** My role must be ABOVE yours in the server settings to mute you!")
    
    except Exception as e:
        await ctx.send(f"⚠️ Could not mute: {e}")

# --- 5. START ---
if __name__ == "__main__":
    keep_alive()
    # Ensure your Secret/Environment Variable in Render is named DISCORD_TOKEN
    bot.run(os.getenv('DISCORD_TOKEN'))
