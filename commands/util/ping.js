module.exports = {
  name: 'ping',
  description: 'Check latency',
  execute(message) {
    message.reply(`Pong! 🏓 ${Date.now() - message.createdTimestamp}ms`);
  },
};
