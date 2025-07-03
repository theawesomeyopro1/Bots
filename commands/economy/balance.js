const balances = {};
module.exports = {
  name: 'balance',
  description: 'Check your coins',
  execute(message) {
    const bal = balances[message.author.id] || 0;
    message.reply(`You have ${bal} coins.`);
  },
};
