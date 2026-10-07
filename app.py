import os
import asyncio
import threading

import discord
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"✅ Connecté à Discord en tant que {client.user}")


async def send_discord_message(message):
    try:
        channel = client.get_channel(CHANNEL_ID)

        if channel is None:
            channel = await client.fetch_channel(CHANNEL_ID)

        await channel.send(message)
        print("✅ Message envoyé sur Discord")

    except Exception as e:
        print(f"❌ Erreur Discord : {e}")


@app.route("/github", methods=["POST"])
def github_webhook():
    data = request.json

    print("📦 Webhook GitHub reçu !")

    repository = data["repository"]["full_name"]
    commits = data.get("commits", [])
    branch = data["ref"].split("/")[-1]

    for commit in commits:
        author = commit["author"]["name"]
        message = commit["message"]
        url = commit["url"]

        discord_message = (
            f"🚀 **Nouveau commit sur `{repository}`**\n\n"
            f"👤 **Auteur :** {author}\n"
            f"🌿 **Branche :** `{branch}`\n"
            f"📝 **Message :** {message}\n"
            f"🔗 [Voir le commit]({url})"
        )

        # On envoie le message au bot via une file d'attente
        asyncio.run_coroutine_threadsafe(
            send_discord_message(message=discord_message),
            bot_loop
        )

    return "OK", 200


bot_loop = None


def start_bot():
    global bot_loop

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    bot_loop = loop

    loop.run_until_complete(client.start(TOKEN))


def run_flask():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))


if __name__ == "__main__":
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    run_flask()