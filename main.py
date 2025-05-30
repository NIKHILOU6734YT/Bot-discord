import os
import discord
from discord.ext import commands, tasks
import requests
from flask import Flask
from threading import Thread

# Intents configurés
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Initialisation du bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Récupération des variables d'environnement
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
SERVER_ID = int(os.getenv("SERVER_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Tâche qui vérifie les abonnés toutes les 5 minutes
last_subscriber_count = None

@tasks.loop(minutes=5)
async def update_subscriber_count():
    global last_subscriber_count

    try:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"
        response = requests.get(url)
        data = response.json()

        subs = int(data["items"][0]["statistics"]["subscriberCount"])

        if subs != last_subscriber_count:
            last_subscriber_count = subs
            guild = bot.get_guild(SERVER_ID)
            channel = guild.get_channel(CHANNEL_ID)
            await channel.edit(name=f"📊 {subs} abonnés")
            print(f"✅ Salon mis à jour : {subs} abonnés")

    except Exception as e:
        print(f"❌ Erreur update_channel_name : {e}")

# Commande simple pour tester le bot
@bot.command()
async def ping(ctx):
    await ctx.send("Pong !")

# Quand le bot est prêt
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    update_subscriber_count.start()

# Flask pour maintenir Railway actif
app = Flask("")

@app.route("/")
def home():
    return "Bot actif !"

def run():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run).start()

# Lancement du bot
bot.run(DISCORD_TOKEN)

