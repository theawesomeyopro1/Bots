import os
import re
import random
import discord
import asyncio
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()
TOKEN = os.getenv("FRIDAY_TOKEN")

app = Flask(__name__)

@app.route('/')
def home():
    return "Friday is alive and ready, sir."

def run():
    app.run(host='0.0.0.0', port=8081)

def keep_alive():
    Thread(target=run).start()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)

# To track ongoing games by user id
active_games = {}

class RPSView(discord.ui.View):
    def __init__(self, user, channel, total_rounds):
        super().__init__(timeout=None)
        self.user = user
        self.channel = channel
        self.total_rounds = total_rounds
        self.rounds_played = 0
        self.user_score = 0
        self.bot_score = 0

    async def play_round(self, interaction, user_choice):
        bot_choice = random.choice(["rock", "paper", "scissors"])
        result = (
            "A tie, sir." if user_choice == bot_choice else
            "Victory is yours, sir." if (user_choice, bot_choice) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")] else
            "Regrettably, you have lost this round, sir."
        )
        if "Victory is yours" in result:
            self.user_score += 1
        elif "Regrettably" in result:
            self.bot_score += 1

        self.rounds_played += 1
        await interaction.response.send_message(
            f"Round {self.rounds_played}/{self.total_rounds}:\nYou chose **{user_choice}**.\nI chose **{bot_choice}**.\n{result}",
            ephemeral=True
        )

        if self.rounds_played >= self.total_rounds:
            # Disable all buttons
            for item in self.children:
                item.disabled = True
            # Send final embed with Play Again / End buttons
            embed = discord.Embed(
                title="🎮 Rock Paper Scissors - Game Over",
                description=(
                    f"You won **{self.user_score}** rounds.\n"
                    f"I won **{self.bot_score}** rounds.\n\n"
                    "Would you like to play again, sir?"
                ),
                color=0x3498db
            )
            await self.channel.send(embed=embed, view=PlayAgainView(self.user, self.channel, self.total_rounds))
            active_games.pop(self.user.id, None)
            self.stop()

class PlayAgainView(discord.ui.View):
    def __init__(self, user, channel, total_rounds):
        super().__init__(timeout=60)  # times out after 60 seconds
        self.user = user
        self.channel = channel
        self.total_rounds = total_rounds

    @discord.ui.button(label="Play Again", style=discord.ButtonStyle.success)
    async def play_again(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This is not your game, sir.", ephemeral=True)
        await interaction.response.send_message("Starting a new game, sir!", ephemeral=True)

        # Start new game (recreate RPSView and send new buttons)
        view = RPSView(self.user, self.channel, self.total_rounds)
        await self.channel.send(f"Let's play Rock Paper Scissors for {self.total_rounds} rounds, sir. Make your choice:", view=view)
        self.stop()

    @discord.ui.button(label="End Game", style=discord.ButtonStyle.danger)
    async def end_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This is not your game, sir.", ephemeral=True)
        await interaction.response.send_message("Goodbye, sir. I will now delete this channel.", ephemeral=True)
        await asyncio.sleep(3)
        try:
            await self.channel.delete()
        except:
            pass
        self.stop()

class ChoiceButton(discord.ui.Button):
    def __init__(self, label, view):
        super().__init__(label=label.capitalize(), style=discord.ButtonStyle.primary)
        self.choice = label
        self.view = view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.user:
            return await interaction.response.send_message("This is not your game, sir.", ephemeral=True)
        await self.view.play_round(interaction, self.choice)

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

    # Parse rounds from command
    rounds_match = re.search(r"for (\d+) rounds?", command)
    total_rounds = int(rounds_match.group(1)) if rounds_match else 1

    if "rock paper scissors" in command or any(x in command for x in ["rock", "paper", "scissors"]):
        # Check if user already has an active game
        if message.author.id in active_games:
            await message.reply("You already have an active game, sir! Please finish it before starting a new one.")
            return

        # Create new channel named "rps-with-<user>"
        guild = message.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            message.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        channel_name = f"rps-with-{message.author.display_name}".lower().replace(" ", "-")
        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

        await message.reply(f"Created a private channel {channel.mention} for Rock Paper Scissors, sir!")

        # Prepare and send buttons
        view = RPSView(message.author, channel, total_rounds)
        for choice in ["rock", "paper", "scissors"]:
            view.add_item(ChoiceButton(choice, view))

        await channel.send(f"Let's play Rock Paper Scissors for **{total_rounds}** rounds, sir! Please make your choice:", view=view)

        active_games[message.author.id] = view
        return

    # Other commands here (8ball, coin flip etc) ...
    # Example 8ball:
    if "8ball" in command:
        responses = [
            "It is certain.", "Without a doubt.", "Yes, definitely.",
            "Ask again later.", "Cannot predict now.",
            "Don't count on it.", "My reply is no.", "Outlook not so good."
        ]
        await message.reply(f"As you wish, sir... My answer is: *{random.choice(responses)}*")
        return

    # Default fallback
    await message.reply("I'm afraid I don't recognize that request, sir.")

keep_alive()
client.run(TOKEN)
