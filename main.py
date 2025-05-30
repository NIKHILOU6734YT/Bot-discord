import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import requests
import asyncio

# Variables d'environnement
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
SERVER_ID = int(os.getenv("SERVER_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Flask pour UptimeRobot
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot actif !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Bot Discord
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Récupère le nombre d'abonnés YouTube
def get_subscriber_count():
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    try:
        return int(data["items"][0]["statistics"]["subscriberCount"])
    except Exception as e:
        print("❌ Erreur get_subscriber_count :", e)
        return 0

# Commande !subs
@bot.command()
async def subs(ctx):
    count = get_subscriber_count()
    await ctx.send(f"La chaîne a {count} abonnés 📊")

# Mise à jour automatique du nom du salon
async def update_channel_name():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            count = get_subscriber_count()
            guild = bot.get_guild(SERVER_ID)
            channel = guild.get_channel(CHANNEL_ID)
            if channel:
                await channel.edit(name=f"📊• {count} abonnés")
                print(f"✅ Salon mis à jour : {count} abonnés")
            else:
                print("❌ Channel non trouvé")
        except Exception as e:
            print(f"❌ Erreur update_channel_name : {e}")
        await asyncio.sleep(300)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    bot.loop.create_task(update_channel_name())

# Lancer
keep_alive()
bot.run(DISCORD_TOKEN)

