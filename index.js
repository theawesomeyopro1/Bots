const fs = require('fs');
const { Client, Collection, GatewayIntentBits } = require('discord.js');
require('dotenv').config();

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] });

client.config = require('./config.json');
client.commands = new Collection();

// Load commands
fs.readdirSync('./commands').forEach(cat => {
  fs.readdirSync(`./commands/${cat}`).forEach(file => {
    const cmd = require(`./commands/${cat}/${file}`);
    client.commands.set(cmd.name, cmd);
  });
});

// Load events
fs.readdirSync('./events').forEach(file => {
  const event = require(`./events/${file}`);
  client[event.name] = event.execute.bind(null, client);
  client.on(event.name.toLowerCase(), client[event.name]);
});

client.login(process.env.TOKEN);
