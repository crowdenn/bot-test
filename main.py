import discord
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Render provides the PORT variable; we use 8080 as a backup
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content == '!ping':
            await message.channel.send('pong!')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)

keep_alive()
client.run(os.getenv('DISCORD_TOKEN'))
