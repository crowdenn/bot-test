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
    # Render uses the PORT env variable; we default to 8080
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
    
    # Randomly wait between 1 and 10 minutes (60 to 600 seconds)
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
    # Start the loop when the bot is ready
    if not beep_loop.is_running():
        beep_loop.start()

# --- 4. THE LIFESTEAL COMMAND ---
@bot.command(name="lifesteal")
async def lifesteal(ctx):
    # Bots cannot mute themselves or the server owner
    if ctx.author == bot.user:
        return

    try:
        # 1. Delete the "!lifesteal" message to keep the chat clean
        await ctx.message.delete()
        
        # 2. Correctly use datetime.timedelta for the 10-minute timeout
        duration = datetime.timedelta(minutes=10)
        await ctx.author.timeout(duration, reason="Used !lifesteal command")
        
        # 3. Inform the channel
        await ctx.send(f"🔇 {ctx.author.mention} has been muted for 10 minutes for saying the forbidden word.")
    
    except discord.Forbidden:
        # This usually means the bot's role is too low in the hierarchy
        await ctx.send(f"❌ **Permission Error:** I can't mute {ctx.author.mention}. Make sure my role is at the TOP of the role list!")
    
    except Exception as e:
        print(f"Command error: {e}")
        await ctx.send(f"⚠️ An error occurred: {e}")

# --- 5. START ---
if __name__ == "__main__":
    keep_alive()
    # Make sure DISCORD_TOKEN is set in your Render Environment Variables
    bot.run(os.getenv('DISCORD_TOKEN'))
