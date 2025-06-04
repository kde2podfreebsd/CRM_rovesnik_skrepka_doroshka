const token = '6795573015:AAGKlQVzf2uKzUNDrbLhNOQ5w1g89WsAp58'

const TelegramBot = require('node-telegram-bot-api')

const bot = new TelegramBot(token, { polling: true })

bot.on('message', async (msg) => {
    if (msg.text === '/start') {
        const chatId = msg.chat.id
        await bot.sendMessage(chatId, `Рады вас видеть, ${msg.from.first_name}!`)
    } else {
        const chatId = msg.chat.id
        await bot.sendMessage(chatId, `Отсканируйте QR-код, ${msg.from.first_name}!`)
    }
})

