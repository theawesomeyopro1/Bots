const balances = require('./balance').balances || {};
const cooldowns = {};
const cd = require('../../config.json').dailyCooldown;

module.exports = {
  name: 'daily',
  description: 'Get daily coins',
  execute(message) {
    const id = message.author.id;
    const now = Date.now();
    if (cooldowns[id] && now - cooldowns[id] < cd) {
      return message.reply('You already claimed today.');
    }
    balances[id] = (balances[id] || 0) + 100;
    cooldowns[id] = now;
    message.reply('You got your daily 100 coins!');
  },
};
