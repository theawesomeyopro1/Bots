# Jarvis info.

This is a full-featured Discord bot written in Node.js using `discord.js`, inspired from the marvel movies.

## Features

✅ Minigames (Rock-Paper-Scissors, Number Guessing)  
✅ Economy System (Balance, Daily Rewards)  
✅ Utility Commands (Ping, Help)  

## Setup

1. Install dependencies:
```bash
npm install discord.js dotenv
```

2. Create a bot token from the [Discord Developer Portal](https://discord.com/developers/applications)

3. Fill in the `.env` file:
  ```env
TOKEN=YOUR_BOT_TOKEN
PREFIX=!
  ```

4. Run the bot:
   ```bash
node index.js
    ```

## Folder Structure

- \`commands/\`: All commands (fun, economy, util)
- \`events/\`: Bot event handlers
- \`index.js\`: Bot entry point
- \`.env\`, \`config.json\`: Config files

## Add More Features

You can expand this bot with moderation, music, logging, XP, and more!

---
Made with ❤️
