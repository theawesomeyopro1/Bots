import os
import re
import random
import discord
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("FRIDAY_TOKEN")

# Flask keep-alive server
app = Flask(__name__)

@app.route('/')
def home():
    return "Friday is alive and ready, sir."

def run():
    app.run(host='0.0.0.0', port=8081)

def keep_alive():
    Thread(target=run).start()

# Discord client setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Friday is online as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()
    if not content.startswith("hey friday"):
        return

    command = re.sub(r"^hey friday[,.]?", "", message.content, flags=re.I).strip()

    # Help menu embed
    if "help" in command or "commands" in command:
        embed = discord.Embed(
            title="🤖 Friday's Fun Commands",
            description="Here's what I can do, sir:",
            color=0x3498db
        )
        embed.add_field(name="Play 8ball", value="`hey friday, let's play 8ball`", inline=False)
        embed.add_field(name="Rock Paper Scissors", value="`hey friday, rock` or `paper` or `scissors`", inline=False)
        embed.add_field(name="Coin Flip", value="`hey friday, flip a coin`", inline=False)
        embed.set_footer(text="More fun commands coming soon!")
        await message.reply(embed=embed)
        return

    # 8ball
    if "let's play 8ball" in command:
        responses = [
            "It is certain.", "Without a doubt.", "Yes, definitely.",
            "Ask again later.", "Cannot predict now.",
            "Don't count on it.", "My reply is no.", "Outlook not so good."
        ]
        await message.reply(f"As you wish, sir... My answer is: *{random.choice(responses)}*")
        return

    # Rock Paper Scissors
    if any(x in command for x in ["rock", "paper", "scissors"]):
        user_choice = next((x for x in ["rock", "paper", "scissors"] if x in command), None)
        bot_choice = random.choice(["rock", "paper", "scissors"])
        result = (
            "A tie, sir." if user_choice == bot_choice else
            "Victory is yours, sir." if (user_choice, bot_choice) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")] else
            "Regrettably, you have lost this round, sir."
        )
        await message.reply(f"You chose {user_choice}. I chose {bot_choice}. {result}")
        return

    # Coin Flip
    if "flip a coin" in command:
        flip = random.choice(["Heads", "Tails"])
        await message.reply(f"The coin landed on: {flip}, sir.")
        return

    # Unknown command fallback
    await message.reply("I'm afraid I don't recognize that request, sir.")

# Run keep-alive server and bot
keep_alive()
client.run(TOKEN)
