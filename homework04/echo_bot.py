import telebot


access_token = '1027789245:AAEoOP6EmxbaCQHvtAQ4IAPZzmBCeqKVau4'
telebot.apihelper.proxy = {'https': 'https://141.125.82.106:80'}

# Создание бота с указанным токеном доступа
bot = telebot.TeleBot(access_token)


# Бот будет отвечать только на текстовые сообщения
@bot.message_handler(content_types=['text'])
def echo(message: str) -> None:
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.polling()
