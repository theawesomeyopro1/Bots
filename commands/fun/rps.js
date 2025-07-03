module.exports = {
  name: 'rps',
  description: 'Play rock-paper-scissors',
  execute(message, args) {
    const choices = ['rock', 'paper', 'scissors'];
    const user = args[0]?.toLowerCase();
    if (!choices.includes(user)) return message.reply('Use: !rps rock|paper|scissors');
    const bot = choices[Math.floor(Math.random() * 3)];
    const res = user === bot ? 'Tie!' :
                (user === 'rock' && bot === 'scissors') ||
                (user === 'paper' && bot === 'rock') ||
                (user === 'scissors' && bot === 'paper')
                  ? 'You win!' : 'You lose!';
    message.reply(`You: ${user}\nBot: ${bot}\n${res}`);
  },
};
