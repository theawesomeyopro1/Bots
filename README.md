# Jarvis - Your All-in-One Discord Assistant 🤖

A single-file, Python-based Discord bot inspired by Marvel’s Jarvis.  
Commands are triggered by starting messages with **"hey Jarvis,"** or **"hey Jarvis."**

---

## Features

- 🎲 Play Rock-Paper-Scissors  
- 🎱 Magic 8-Ball game (`hey Jarvis. let's play 8ball, <question>`)  
- 🛡️ Moderation commands: mute, unmute, kick, ban (permission-restricted)  
- 💬 Utility commands: ping, balance (dummy), say  
- 🗑️ Logs deleted messages (text + attachments) in a configurable channel with neat embeds  
- 📝 Permissions checks with Jarvis-style polite responses  

---

## Setup & Run

1. Install dependencies:

        pip install -U discord.py

2. Create a Discord bot via the [Discord Developer Portal](https://discord.com/developers/applications) and get its token.

3. Update the bot code:
   - Replace `YOUR_BOT_TOKEN_HERE` with your bot token
   - Replace `LOG_CHANNEL_ID` with your log channel ID for deleted message logs

4. Run the bot:

        python jarvis_bot.py

---

## Usage Examples

    hey Jarvis, ping  
    hey Jarvis, mute @user for 5 minutes  
    hey Jarvis, kick @user for spamming  
    hey Jarvis, ban @user for being rude  
    hey Jarvis, unmute @user  
    hey Jarvis, say Hello, world!  
    hey Jarvis. let's play 8ball, will I ace my exams?  
    hey Jarvis, rock

---

## Notes

- Moderation commands require appropriate Discord permissions.  
- Bot responds only when commands start with `"hey Jarvis,"` or `"hey Jarvis."`.  
- Deleted messages get logged with attachments to the configured channel.

---

Made with ❤️ by you, inspired by Jarvis from Marvel.  
Enjoy commanding your own AI assistant on Discord!
