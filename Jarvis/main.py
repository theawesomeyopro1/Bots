import os
import re
import discord
import asyncio
from datetime import datetime, timedelta, timezone
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# ===== Load environment variables =====
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # from .env
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))

# ===== Flask keep-alive server =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Jarvis is alive, sir."

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# ===== Discord Client Setup =====
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)
message_cache = {}

@client.event
async def on_ready():
    print(f"Jarvis is online as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    message_cache[message.id] = message
    if len(message_cache) > 1000:
        message_cache.pop(next(iter(message_cache)))

    content = message.content.lower()
    if not content.startswith("hey jarvis"):
        return

    command = re.sub(r"^hey jarvis[,.]?", "", message.content, flags=re.I).strip()

    # === Help Embed ===
    if any(phrase in command for phrase in [
        "help", 
        "i need help using you", 
        "how do i use you", 
        "what can you do", 
        "commands", 
        "assist me"
    ]):
        embed = discord.Embed(
            title="🛡️ Jarvis Moderation Commands",
            description="Here’s what I can do for you, sir:",
            color=0x7289DA
        )
        embed.add_field(name="Mute", value="`hey jarvis, mute @user for 10 minutes`", inline=False)
        embed.add_field(name="Unmute", value="`hey jarvis, unmute @user`", inline=False)
        embed.add_field(name="Kick", value="`hey jarvis, kick @user for spamming`", inline=False)
        embed.add_field(name="Ban", value="`hey jarvis, ban @user for violating rules`", inline=False)
        embed.add_field(name="Purge", value="`hey jarvis, purge 25` — Deletes the last 25 messages", inline=False)
        embed.set_footer(text="Permissions required: Manage Messages, Kick, or Ban Members")
        return await message.reply(embed=embed)

    elif "mute" in command:
        if not message.author.guild_permissions.manage_messages:
            return await message.reply("You lack the necessary clearance to mute, sir.")

        match = re.search(r"<@!?(\d+)>", message.content)
        duration_match = re.search(r"for (\d+) ?(seconds|minutes|hours)?", command)
        member = message.guild.get_member(int(match.group(1))) if match else None

        duration_seconds = 60
        if duration_match:
            num = int(duration_match.group(1))
            unit = duration_match.group(2)
            if unit == "minutes": duration_seconds = num * 60
            elif unit == "hours": duration_seconds = num * 3600
            else: duration_seconds = num

        if member:
            try:
                until = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)
                await member.edit(timed_out_until=until)
                await message.reply(f"{member.display_name} has been muted for {duration_seconds} seconds, sir.")
            except Exception as e:
                await message.reply(f"Apologies, sir. I was unable to mute the user: {e}")
        else:
            await message.reply("I'm afraid I couldn't identify who to mute, sir.")

    elif "unmute" in command:
        if not message.author.guild_permissions.manage_messages:
            return await message.reply("You lack the clearance to unmute, sir.")

        match = re.search(r"<@!?(\d+)>", message.content)
        member = message.guild.get_member(int(match.group(1))) if match else None

        if member:
            try:
                await member.edit(timed_out_until=None)
                await message.reply(f"{member.display_name} has been unmuted, sir.")
            except Exception as e:
                await message.reply(f"Regrettably, I could not unmute the user: {e}")
        else:
            await message.reply("I cannot locate that user, sir.")

    elif "kick" in command:
        if not message.author.guild_permissions.kick_members:
            return await message.reply("That command is restricted, sir.")

        match = re.search(r"<@!?(\d+)>", message.content)
        reason = command.split("for")[-1].strip() if "for" in command else "No reason provided."
        member = message.guild.get_member(int(match.group(1))) if match else None

        if member:
            try:
                await member.kick(reason=reason)
                await message.reply(f"{member.display_name} has been kicked, sir. Reason: {reason}")
            except Exception as e:
                await message.reply(f"Failed to kick. I encountered an error, sir: {e}")
        else:
            await message.reply("I cannot locate that user, sir.")

    elif "ban" in command:
        if not message.author.guild_permissions.ban_members:
            return await message.reply("Regrettably, you do not possess ban privileges, sir.")

        match = re.search(r"<@!?(\d+)>", message.content)
        reason = command.split("for")[-1].strip() if "for" in command else "No reason provided."
        member = message.guild.get_member(int(match.group(1))) if match else None

        if member:
            try:
                await member.ban(reason=reason)
                await message.reply(f"{member.display_name} has been banned, sir. Reason: {reason}")
            except Exception as e:
                await message.reply(f"Failed to ban. I encountered an error, sir: {e}")
        else:
            await message.reply("I cannot locate that user, sir.")

    elif "purge" in command:
        if not message.author.guild_permissions.manage_messages:
            return await message.reply("You lack the authorization to purge messages, sir.")

        match = re.search(r"purge (\d+)", command)
        if match:
            amount = int(match.group(1))
            amount = max(1, min(100, amount))  # Clamp between 1 and 100

            try:
                deleted = await message.channel.purge(limit=amount + 1)  # +1 to include the command itself
                confirmation = await message.channel.send(f"🧹 Successfully purged {len(deleted) - 1} messages, sir.")
                await asyncio.sleep(3)
                await confirmation.delete()
            except Exception as e:
                await message.reply(f"Regrettably, I couldn't complete the purge, sir: {e}")
        else:
            await message.reply("Please specify how many messages you'd like me to purge, sir. Example: `hey jarvis, purge 10`")

    else:
        await message.reply("I'm afraid I don't recognize that request, sir.")

@client.event
async def on_message_delete(message):
    if message.author.bot or LOG_CHANNEL_ID == 0:
        return

    channel = client.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(title="🗑️ Message Deleted", color=0xff0000, timestamp=datetime.utcnow())
    embed.add_field(name="Author", value=f"{message.author} (ID: {message.author.id})", inline=False)
    embed.add_field(name="Channel", value=message.channel.mention, inline=False)
    embed.add_field(name="Content", value=message.content or "*No text content*", inline=False)

    if message.attachments:
        image_attachments = [a for a in message.attachments if a.content_type and a.content_type.startswith("image/")]
        if image_attachments:
            embed.set_image(url=image_attachments[0].url)

            if len(image_attachments) > 1:
                other_images = image_attachments[1:]
                embed.add_field(
                    name=f"Other Images ({len(other_images)})",
                    value="\n".join(f"[{a.filename}]({a.url})" for a in other_images),
                    inline=False,
                )

            non_image_attachments = [a for a in message.attachments if a not in image_attachments]
            if non_image_attachments:
                embed.add_field(
                    name=f"Other Attachments ({len(non_image_attachments)})",
                    value="\n".join(f"[{a.filename}]({a.url})" for a in non_image_attachments),
                    inline=False,
                )
        else:
            embed.add_field(
                name=f"Attachments ({len(message.attachments)})",
                value="\n".join(f"[{a.filename}]({a.url})" for a in message.attachments),
                inline=False,
            )

    await channel.send(embed=embed)

# ===== Launch Bot =====
keep_alive()
client.run(TOKEN)
