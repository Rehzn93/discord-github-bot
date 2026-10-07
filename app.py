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






@app.route("/github", methods=["POST"])
def github_webhook():
    data = request.json

    print("📦 Webhook GitHub reçu !")

    # Informations du dépôt
    repository = data["repository"]["full_name"]

    # Informations sur le commit
    commits = data.get("commits", [])

    # Branche
    branch = data["ref"].split("/")[-1]

    # Envoyer les commits sur Discord
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

        asyncio.run_coroutine_threadsafe(
            send_discord_message(discord_message),
            client.loop
        )

    return "OK", 200


async def send_discord_message(message):
    channel = client.get_channel(CHANNEL_ID)

    if channel:
        await channel.send(message)


def run_flask():
    app.run(host="0.0.0.0", port=5001)


async def main():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    await client.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())