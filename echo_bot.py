import telebot
import yaml

config = yaml.safe_load(open("conf.yml"))

bot = telebot.TeleBot(config["token"])

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        chat_id = message.chat.id
        bot.send_message(chat_id, "Welcome to Euro 2016 prediction contest! Type /help for help, /rules for rules or /predict to make your predictions")
    except Exception as e:
        bot.reply_to(message, 'oooops')

@bot.message_handler(commands=['help'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "/start View start message\n/help View this message\n/predict Make prediction")

@bot.message_handler(commands=['rules'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "You need to answer general questions (Who will win the tournament? Who will score the most goals?) And three questions about each match:\n1. Who will win the game or will there be a draw?\n2. What will be ")

@bot.message_handler(commands=['predict'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "We are currently working on this feature!")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.polling()