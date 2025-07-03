module.exports = {
  name: 'guess',
  description: 'Guess a number 1-10',
  async execute(message) {
    const num = Math.floor(Math.random() * 10) + 1;
    message.reply('Guess a number between 1 and 10:');
    const filter = m => m.author.id === message.author.id;
    const c = message.channel.createMessageCollector({ filter, time: 10000, max: 1 });
    c.on('collect', m => m.reply(parseInt(m.content) === num ? '🎉 Correct!' : `❌ Nope, it was ${num}`));
    c.on('end', coll => { if (coll.size === 0) message.reply('⏳ Time up!'); });
  },
};
