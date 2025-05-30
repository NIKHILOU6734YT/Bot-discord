import os
import discord
from discord.ext import commands, tasks
from flask import Flask
from threading import Thread
import requests

# === Intents ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# === Bot setup ===
bot = commands.Bot(command_prefix="!", intents=intents)

# === Variables d'environnement ===
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
SERVER_ID = int(os.getenv("SERVER_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# === Flask keep-alive ===
app = Flask('')

@app.route('/')
def home():
    return "Bot Discord actif !"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run)
    thread.start()

# === Commande !subs ===
@bot.command()
async def subs(ctx):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    response = requests.get(url).json()
    
    try:
        subs = response["items"][0]["statistics"]["subscriberCount"]
        await ctx.send(f"📊 Le nombre d'abonnés est : {subs}")
    except Exception as e:
        await ctx.send("Erreur lors de la récupération des abonnés.")
        print("Erreur !", e)

# === Tâche de mise à jour automatique ===
@tasks.loop(minutes=10)
async def update_channel_name():
    try:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"
        response = requests.get(url).json()
        subs = response["items"][0]["statistics"]["subscriberCount"]
        guild = bot.get_guild(SERVER_ID)
        channel = guild.get_channel(CHANNEL_ID)
        await channel.edit(name=f"{subs} abonnés")
        print(f"✅ Salon mis à jour : {subs} abonnés")
    except Exception as e:
        print("Erreur lors de la mise à jour du salon :", e)

# === Lancement du bot ===
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    update_channel_name.start()

keep_alive()
bot.run(DISCORD_TOKEN)
