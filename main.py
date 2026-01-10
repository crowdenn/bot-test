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
    # Render uses the PORT env variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True  # Required to read the !lifesteal command
intents.members = True          # Required for timeouts/muting

bot = commands.Bot(command_prefix="!", intents=intents)

# --- 3. RANDOM BEEP LOOP ---
@tasks.loop(seconds=1) 
async def beep_loop():
    # Replace with your actual Channel ID
    channel_id = 1364299553733345393
    channel = bot.get_channel(channel_id)
    
    # Wait for a random time between 1 and 10 minutes (60 to 600 seconds)
    wait_time = random.randint(60, 600)
    await asyncio.sleep(wait_time)
    
    if channel:
        try:
            # The beep also deletes itself after 30 seconds to stay clean
            await channel.send("beep beep", delete_after=30)
            print(f"Sent beep beep after waiting {wait_time}s")
        except Exception as e:
            print(f"Loop error: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Start the loop when the bot is ready
    if not beep_loop.is_running():
        beep_loop.start()

# --- 4. THE LIFESTEAL COMMAND (WITH AUTO-CLEANUP) ---
@bot.command(name="lifesteal")
async def lifesteal(ctx):
    # Prevent the bot from muting itself or the Server Owner
    if ctx.author == bot.user:
        return

    try:
        # 1. Delete the user's "!lifesteal" message immediately
        await ctx.message.delete()
        
        # 2. Apply a 10-minute timeout using datetime.timedelta
        duration = datetime.timedelta(minutes=10)
        await ctx.author.timeout(duration, reason="void.")
        
        # 3. Send a confirmation message that deletes ITSELF after 5 seconds
        await ctx.send(f" {ctx.author.mention} has been muted. (Message auto-cleaned)", delete_after=5)
    
    except discord.Forbidden:
        # Happens if bot role is too low or target is Server Owner
        await ctx.send(f"no perms?", delete_after=10)
    
    except Exception as e:
        print(f"Command error: {e}")
        await ctx.send(f error: {e}", delete_after=5)

# --- 5. START ---
if __name__ == "__main__":
    keep_alive()
    # Ensure DISCORD_TOKEN is set in Render Environment Variables
    bot.run(os.getenv('DISCORD_TOKEN'))
