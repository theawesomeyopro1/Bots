import os
import re
import random
import discord
import asyncio
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from datetime import datetime, timedelta

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

# Game storage
rps_games = {}

class RPSGame:
    def __init__(self, player, channel, total_rounds):
        self.player = player
        self.channel = channel
        self.total_rounds = total_rounds
        self.current_round = 1
        self.player_score = 0
        self.bot_score = 0
        self.choices = ["rock", "paper", "scissors"]

    async def play_round(self, message):
        user_input = message.content.strip().lower()
        if user_input not in self.choices:
            return  # Invalid input; ignore

        bot_choice = random.choice(self.choices)
        result_text = f"**Round {self.current_round}**\nYou chose **{user_input}**, I chose **{bot_choice}**.\n"

        if user_input == bot_choice:
            result_text += "It's a tie! 🤝"
        elif (user_input, bot_choice) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")]:
            self.player_score += 1
            result_text += "You win this round! 🎉"
        else:
            self.bot_score += 1
            result_text += "I win this round! 😈"

        await self.channel.send(result_text)
        self.current_round += 1

        if self.current_round > self.total_rounds:
            await self.end_game()

    async def end_game(self):
        embed = discord.Embed(
            title="🎮 Game Over!",
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="Final Score",
            value=(
                f"{self.player.mention}: {self.player_score}\n"
                f"Friday: {self.bot_score}"
            ),
            inline=False
        )

        if self.player_score > self.bot_score:
            embed.add_field(name="Result", value="🎉 You win overall! Congratulations!", inline=False)
        elif self.player_score < self.bot_score:
            embed.add_field(name="Result", value="😈 I win overall! Better luck next time!", inline=False)
        else:
            embed.add_field(name="Result", value="🤝 It's an overall tie!", inline=False)

        await self.channel.send(embed=embed)

        # Countdown before deletion
        for i in range(10, 0, -1):
            await self.channel.send(f"Deleting this channel in {i} seconds...", delete_after=1)
            await asyncio.sleep(1)

        await self.channel.delete()
        rps_games.pop(self.channel.id, None)

@client.event
async def on_ready():
    print(f"Friday is online as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    # Handle game input if channel is in active games
    if message.channel.id in rps_games:
        game = rps_games[message.channel.id]
        if message.author.id == game.player.id:
            await game.play_round(message)
        return

    if not content.startswith("hey friday"):
        return

    command = re.sub(r"^hey friday[,.]?", "", message.content, flags=re.I).strip()

    if "let's play rock paper scissors" in command:
        match = re.search(r"for (\d+)", command)
        rounds = int(match.group(1)) if match else 3

        # Create a game channel
        guild = message.guild
        channel_name = f"rps-with-{message.author.name}".lower().replace(" ", "-")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            message.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        game_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

        await message.channel.send(
            f"{message.author.mention}, your Rock Paper Scissors game channel has been created: {game_channel.mention}\n"
            f"Head over there and type your choice to begin!"
        )

        await game_channel.send(
            f"{message.author.mention} Welcome to **Rock Paper Scissors**!\n"
            f"Type your choice for round 1: **rock**, **paper**, or **scissors**."
        )

        rps_games[game_channel.id] = RPSGame(message.author, game_channel, rounds)
        return

    if "let's play 8ball" in command:
        responses = [
            "It is certain.", "Without a doubt.", "Yes, definitely.",
            "Ask again later.", "Cannot predict now.",
            "Don't count on it.", "My reply is no.", "Outlook not so good."
        ]
        await message.reply(f"As you wish, sir... My answer is: *{random.choice(responses)}*")
        return

    if "flip a coin" in command:
        await message.reply(f"The coin landed on: **{random.choice(['Heads', 'Tails'])}**, sir.")
        return

    if "help" in command or "commands" in command:
        embed = discord.Embed(
            title="Friday Help Menu",
            description="Here are the available commands you can use with Friday:",
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="🎮 Rock Paper Scissors",
            value="`hey friday, let's play rock paper scissors for [rounds]`\nPlay an RPS game. Default rounds: 3.",
            inline=False
        )
        embed.add_field(
            name="🎱 Magic 8-Ball",
            value="`hey friday, let's play 8ball`\nAsk a yes/no question and get a mysterious response.",
            inline=False
        )
        embed.add_field(
            name="🪙 Coin Flip",
            value="`hey friday, flip a coin`\nFlip a virtual coin.",
            inline=False
        )
        embed.set_footer(text="Friday Bot • Your loyal assistant")
        await message.channel.send(embed=embed)
        return

    await message.reply("I'm afraid I don't recognize that request, sir.")

# Start server and bot
keep_alive()
client.run(TOKEN)
