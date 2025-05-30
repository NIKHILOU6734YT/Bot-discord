import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
SERVER_ID = int(os.getenv("SERVER_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))


# === Setup Flask pour Railway/Uptime ===
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot actif !"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# === Intents et initialisation du bot ===
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === Fonction pour obtenir les abonnés YouTube ===
def get_subscriber_count():
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    try:
        return int(data["items"][0]["statistics"]["subscriberCount"])
    except Exception as e:
        print("❌ Erreur get_subscriber_count :", e)
        return 0

# === Mise à jour automatique du nom du salon ===
@tasks.loop(minutes=5)
async def update_channel_name():
    try:
        sub_count = get_subscriber_count()
        guild = bot.get_guild(SERVER_ID)
        if guild:
            channel = guild.get_channel(CHANNEL_ID)
            if channel:
                await channel.edit(name=f"📊• {sub_count} abonnés")
                print(f"✅ Salon mis à jour : {sub_count} abonnés")
            else:
                print("❌ Salon non trouvé")
        else:
            print("❌ Serveur non trouvé")
    except Exception as e:
        print("❌ Erreur update_channel_name :", e)

# === Commande !subs pour afficher les abonnés ===
@bot.command()
async def subs(ctx):
    count = get_subscriber_count()
    await ctx.send(f"📈 La chaîne compte **{count} abonnés**.")

# === Quand le bot est prêt ===
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    update_channel_name.start()

# === Démarrer ===
keep_alive()
bot.run(DISCORD_TOKEN)
