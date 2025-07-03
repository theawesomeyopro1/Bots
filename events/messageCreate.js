module.exports = {
  name: 'messageCreate',
  execute(client, message) {
    if (message.author.bot || !message.content.startsWith(client.config.prefix)) return;
    const [cmd, ...args] = message.content.slice(client.config.prefix.length).split(/\s+/);
    const command = client.commands.get(cmd.toLowerCase());
    if (command) command.execute(message, args);
  },
};
