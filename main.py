import os
import discord
from discord.ext import commands
import requests
from flask import Flask
from threading import Thread

# === Configuration des intents ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# === Création du bot ===
bot = commands.Bot(command_prefix="!", intents=intents)

# === Variables d'environnement ===
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
SERVER_ID = int(os.getenv("SERVER_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# === Commande pour afficher les abonnés ===
@bot.command(name="subs")
async def subs(ctx):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        subs = data["items"][0]["statistics"]["subscriberCount"]
        await ctx.send(f"📊 Le nombre d'abonnés est : **{subs}**")
    else:
        await ctx.send("❌ Impossible de récupérer les abonnés.")

# === Tâche au démarrage ===
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")

    # Récupérer le nombre d'abonnés et mettre à jour le nom du salon
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        subs = data["items"][0]["statistics"]["subscriberCount"]

        guild = bot.get_guild(SERVER_ID)
        if guild:
            channel = guild.get_channel(CHANNEL_ID)
            if channel:
                await channel.edit(name=f"{subs} abonnés")
                print(f"✅ Salon mis à jour : {subs} abonnés")
            else:
                print("❌ Canal introuvable")
        else:
            print("❌ Serveur introuvable")
    else:
        print("❌ Erreur lors de la récupération des stats")

# === Keep alive avec Flask (pour Railway) ===
app = Flask('')

@app.route('/')
def home():
    return "Bot Discord actif !"

def run():

