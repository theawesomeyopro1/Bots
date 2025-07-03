module.exports = {
  name: 'help',
  description: 'List commands',
  execute(message) {
    const cmds = message.client.commands.map(c => `**${c.name}**: ${c.description}`).join('\n');
    message.reply(`Here are my commands:\n${cmds}`);
  },
};
