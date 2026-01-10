import discord
import os
import random
import asyncio
import datetime
from discord.ext import tasks, commands
from flask import Flask
from threading import Thread

# --- 1. WEB SERVER (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Project is runnin and goin!"

def run():
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
    
    # Wait for a random time between 10 and 60 minutes (600 to 3600 seconds)
    wait_time = random.randint(600, 3600) 
    await asyncio.sleep(wait_time)
    
    if channel:
        try:
            # Beeps will now stay in the chat permanently
            await channel.send("beep beep")
            print(f"Sent beep beep. Next one in {wait_time}s")
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
    if ctx.author == bot.user:
        return

    try:
        # Delete the user's message immediately
        await ctx.message.delete()
        
        # Apply a 10-minute timeout
        duration = datetime.timedelta(minutes=10)
        await ctx.author.timeout(duration, reason="void.")
        
        # Bot's confirmation deletes itself after 5 seconds to keep chat clean
        await ctx.send(f"{ctx.author.mention} went to the void. (Message auto-cleaned)", delete_after=5)
    
    except discord.Forbidden:
        # Error if bot is lower than the user in role hierarchy
        await ctx.send("no perms?", delete_after=10)
    
    except Exception as e:
        print(f"Command error: {e}")
        # Fixed the syntax error here
        await ctx.send(f"error: {e}", delete_after=5)

# --- 5. START ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('DISCORD_TOKEN'))
