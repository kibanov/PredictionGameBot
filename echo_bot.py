import telebot
import yaml
from telebot import types

import db_access

config = yaml.safe_load(open("conf.yml"))

bot = telebot.TeleBot(config["token"])

team1 = ''
team2 = ''

class Prediction:
    def __init__(self, uid):
        self.userid = uid
        self.matchid = None
        self.win = None
        self.goal = None
        self.total = None

pred = Prediction(1)


@bot.message_handler(commands=['start'])
def send_start(message):
    try:
        chat_id = message.chat.id
        bot.send_message(chat_id, "Welcome to Euro 2016 prediction contest! Type /help for help, /rules for rules or /predict to make your predictions")
        db_access.add_user(chat_id)
    except Exception as e:
        bot.reply_to(message, 'Something went wrong!')

@bot.message_handler(commands=['help'])
def send_help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, '/start View start message\n' +
        '/help View this message\n' +
        '/predict Make prediction\n' +
        '/setname Set your name\n' +
        '/setgroup Set your group\n' + 
        '/rules Show rules')

@bot.message_handler(commands=['rules'])
def send_rules(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "You need to answer three questions about each match:\n1. Who will win the game or will there be a draw?\n2. What will be the difference of team goals?\n3. Total of the match?\nYou get 3 points for each correct answer. If all 3 answers are correct, you get an additional point.")

@bot.message_handler(commands=['setname'])
def set_name(message):
    msg = bot.reply_to(message, "What is your name?")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    chat_id = message.chat.id
    name = message.text
    db_access.add_name(chat_id, name)
    bot.send_message(chat_id, "Nice to meet you, " + name + "!")

@bot.message_handler(commands=['setgroup'])
def set_group(message):
    msg = bot.reply_to(message, "Type the name of the group you want to be added to:")
    bot.register_next_step_handler(msg, process_group)

def process_group(message):
    chat_id = message.chat.id
    group_name = message.text
    db_access.add_group(chat_id, group_name)
    bot.send_message(chat_id, "You were added to the group " + group_name + "!")

@bot.message_handler(commands=['predict'])
def send_predict(message):
    chat_id = message.chat.id
    global team1
    global team2
    global pred
    pred = Prediction(chat_id)
    next_match = db_access.get_next_match(chat_id)
    pred.matchid = [c['match_no'] for c in next_match][0]
    team1 = [c['team_1'] for c in next_match][0]
    team2 = [c['team_2'] for c in next_match][0]
    stage = [c['type'] for c in next_match][0]
    if (stage == 'Group'):
        stage = stage + ' ' + [c['group'] for c in next_match][0]
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    # db_access.add_prediction(chat_id, 2, 3, 4, 2)
    team1button = types.KeyboardButton(team1)
    team2button = types.KeyboardButton(team2)
    drawbutton = types.KeyboardButton("Draw")
    markup.add(team1button, team2button, drawbutton)
    msg = bot.reply_to(message, stage + ': ' + team1 + ' vs. ' + team2 + '\n Who will win the game?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_win_step)
    # bot.send_message(chat_id, "Prediction added")

def process_win_step(message):
    chat_id = message.chat.id
    global pred
    print(team1)
    print(message.text)
    if (message.text == team1):
        pred.win = 1
    elif (message.text == team2):
        pred.win = 2
    elif (message.text == u'Draw'):
        pred.win = 0
    else:
        bot.send_message(chat_id, "Error!")
    print(pred.win)
    if (message.text == u'Draw'):
        msg = bot.reply_to(message, "How many goals will each team score?")
        bot.register_next_step_handler(msg, process_goal_step)
    else:
        msg = bot.reply_to(message, "What will be the goal difference?")
        bot.register_next_step_handler(msg, process_goal_step)

    # bot.register_next_step_handler(msg, process_goal_step)

def process_goal_step(message):
    chat_id = message.chat.id
    global pred
    pred.goal = int(message.text)
    underbutton = types.KeyboardButton('< 2.5')
    overbutton = types.KeyboardButton('> 2.5')
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(underbutton, overbutton)
    msg = bot.reply_to(message, 'How many goals will the teams score?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_total_step)

def process_total_step(message):
    chat_id = message.chat.id
    global pred
    if (message.text == '< 2.5'):
        pred.total = 0
    elif (message.text == '> 2.5'):
        pred.total = 1
    else:
        msg = bot.send_message(chat_id, "Error!")
    db_access.add_prediction(pred.userid, pred.matchid, pred.win, pred.goal, pred.total)
    bot.send_message(chat_id, "Your prediction for this game is saved!")

# @bot.message_handler(func=lambda message: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)

bot.polling()