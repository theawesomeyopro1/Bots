import discord
import re
import asyncio
import random

TOKEN = "YOUR_BOT_TOKEN_HERE"
LOG_CHANNEL_ID = 123456789012345678  # Put your log channel ID here

INTENTS = discord.Intents.default()
INTENTS.messages = True
INTENTS.message_content = True
INTENTS.guilds = True
INTENTS.members = True
INTENTS.moderation = True
INTENTS.message_content = True
INTENTS.message_delete = True  # For on_message_delete event

client = discord.Client(intents=INTENTS)

# Cache to store recent messages (message ID: message)
message_cache = {}

@client.event
async def on_ready():
    print(f"Jarvis is online as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    # Cache the message for delete logging
    message_cache[message.id] = message
    # Optionally limit cache size:
    if len(message_cache) > 1000:
        message_cache.pop(next(iter(message_cache)))

    content = message.content.lower()

    if not content.startswith("hey jarvis"):
        return

    command = re.sub(r"^hey jarvis[,.]?", "", message.content, flags=re.I).strip()

    # --- 8ball game ---
    if "let's play 8ball" in command.lower():
        responses = [
            "It is certain.", "Without a doubt.", "You may rely on it.",
            "Yes – definitely.", "As I see it, yes.", "Most likely.",
            "Outlook good.", "Signs point to yes.", "Reply hazy, try again.",
            "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]
        chosen = random.choice(responses)
        await message.reply(f"As you wish, sir... My answer is: *{chosen}*")

    # --- Ping ---
    elif "ping" in command:
        latency = round(client.latency * 1000)
        await message.reply(f"Indeed sir, the latency is {latency} milliseconds.")

    # --- Balance (dummy) ---
    elif "balance" in command or "coins" in command:
        await message.reply("Your current balance stands at 300 credits, sir.")

    # --- Rock Paper Scissors ---
    elif "rock" in command or "paper" in command or "scissors" in command:
        user = None
        if "rock" in command: user = "rock"
        elif "paper" in command: user = "paper"
        elif "scissors" in command: user = "scissors"

        bot = random.choice(["rock", "paper", "scissors"])
        result = (
            "A tie, sir." if user == bot else
            "Victory is yours, sir." if (user, bot) in [("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")] else
            "Regrettably, you have lost this round, sir."
        )
        await message.reply(f"You chose {user}. I chose {bot}. {result}")

    # --- Mute ---
    elif "mute" in command:
        if not message.author.guild_permissions.manage_messages:
            await message.reply("You lack the necessary clearance to mute, sir.")
            return

        match = re.search(r"<@!?(\d+)>", message.content)
        duration_match = re.search(r"for (\d+) ?(seconds|minutes|hours)?", command)
        member = None
        if match:
            user_id = int(match.group(1))
            member = message.guild.get_member(user_id)

        duration_seconds = 60
        if duration_match:
            time = int(duration_match.group(1))
            unit = duration_match.group(2)
            if unit == "minutes":
                duration_seconds = time * 60
            elif unit == "hours":
                duration_seconds = time * 3600
            else:
                duration_seconds = time

        if member:
            try:
                await member.edit(timeout=discord.utils.utcnow() + discord.timedelta(seconds=duration_seconds))
                await message.reply(f"{member.display_name} has been muted for {duration_seconds} seconds, sir.")
            except Exception as e:
                await message.reply(f"Apologies, sir. I was unable to mute the user: {e}")
        else:
            await message.reply("I'm afraid I couldn't identify who to mute, sir.")

    # --- Unmute ---
    elif "unmute" in command:
        if not message.author.guild_permissions.manage_messages:
            await message.reply("You lack the clearance to unmute, sir.")
            return

        match = re.search(r"<@!?(\d+)>", message.content)
        if match:
            user_id = int(match.group(1))
            member = message.guild.get_member(user_id)
            if member:
                try:
                    await member.edit(timeout=None)
                    await message.reply(f"{member.display_name} has been unmuted, sir.")
                except Exception as e:
                    await message.reply(f"Regrettably, I could not unmute the user: {e}")
            else:
                await message.reply("I cannot locate that user, sir.")

    # --- Kick ---
    elif "kick" in command:
        if not message.author.guild_permissions.kick_members:
            await message.reply("That command is restricted, sir. You are not authorized to execute it.")
            return

        match = re.search(r"<@!?(\d+)>", message.content)
        reason = command.split("for")[-1].strip() if "for" in command else "No reason provided."
        if match:
            user_id = int(match.group(1))
            member = message.guild.get_member(user_id)
            if member:
                try:
                    await member.kick(reason=reason)
                    await message.reply(f"{member.display_name} has been kicked, sir. Reason: {reason}")
                except Exception as e:
                    await message.reply(f"Failed to kick. I encountered an error, sir: {e}")
            else:
                await message.reply("I cannot locate that user, sir.")

    # --- Ban ---
    elif "ban" in command:
        if not message.author.guild_permissions.ban_members:
            await message.reply("Regrettably, you do not possess ban privileges, sir.")
            return

        match = re.search(r"<@!?(\d+)>", message.content)
        reason = command.split("for")[-1].strip() if "for" in command else "No reason provided."
        if match:
            user_id = int(match.group(1))
            member = message.guild.get_member(user_id)
            if member:
                try:
                    await member.ban(reason=reason)
                    await message.reply(f"{member.display_name} has been banned, sir. Reason: {reason}")
                except Exception as e:
                    await message.reply(f"Failed to ban. I encountered an error, sir: {e}")
            else:
                await message.reply("I cannot locate that user, sir.")

    # --- Say ---
    elif command.startswith("say"):
        to_say = command[4:].strip()
        await message.channel.send(to_say)

    # --- Unknown ---
    else:
        await message.reply("I'm afraid I don't recognize that request, sir.")


@client.event
async def on_message_delete(message):
    if message.author.bot:
        return

    channel = client.get_channel(LOG_CHANNEL_ID)
    if channel is None:
        return  # No log channel set or invalid

    # Compose log message
    author = message.author
    content = message.content or "*No text content*"
    attachments = message.attachments

    embed = discord.Embed(title="🗑️ Message Deleted", color=0xff0000)
    embed.add_field(name="Author", value=f"{author} (ID: {author.id})", inline=False)
    embed.add_field(name="Channel", value=message.channel.mention, inline=False)
    embed.add_field(name="Content", value=content if len(content) < 1024 else content[:1020] + "...", inline=False)

    if attachments:
        attach_texts = []
        for a in attachments:
            attach_texts.append(f"[{a.filename}]({a.url})")
        embed.add_field(name=f"Attachments ({len(attachments)})", value="\n".join(attach_texts), inline=False)

    await channel.send(embed=embed)

client.run(TOKEN)
