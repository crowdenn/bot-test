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
intents.message_content = True 
intents.members = True          

bot = commands.Bot(command_prefix="!", intents=intents)
CHANNEL_ID = 1364219102662754405 # Defined here for easy access

# --- 3. RANDOM BEEP LOOP ---
@tasks.loop(seconds=1) 
async def beep_loop():
    # Wait for a random time between 10 and 20 minutes (600 to 1200 seconds)
    wait_time = random.randint(600, 1200) 
    await asyncio.sleep(wait_time)
    
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            await channel.send("beep beep")
            print(f"Sent loop beep. Next one in {wait_time}s")
        except Exception as e:
            print(f"Loop error: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # --- IMMEDIATE BEEP ON STARTUP ---
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("beep beep")
        print("Initial startup beep sent!")

    if not beep_loop.is_running():
        beep_loop.start()

# --- 4. THE LIFESTEAL COMMAND ---
@bot.command(name="lifesteal")
async def lifesteal(ctx):
    if ctx.author == bot.user:
        return

    try:
        await ctx.message.delete()
        duration = datetime.timedelta(minutes=10)
        await ctx.author.timeout(duration, reason="void.")
        await ctx.send(f"{ctx.author.mention} has been muted. (Message auto-cleaned)", delete_after=5)
    
    except discord.Forbidden:
        await ctx.send("no perms?", delete_after=10)
    
    except Exception as e:
        print(f"Command error: {e}")
        await ctx.send(f"error: {e}", delete_after=5)

# --- 5. START ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('DISCORD_TOKEN'))
