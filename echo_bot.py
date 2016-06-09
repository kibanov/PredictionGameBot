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
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

@bot.message_handler(commands=['help'])
def send_help(message):
    try:
        chat_id = message.chat.id
        bot.send_message(chat_id, '/start View start message\n' +
            '/help View this message\n' +
            '/predict Make prediction\n' +
            '/setname Set your name\n' +
            '/setgroup Set your group\n' + 
            '/rules Show rules')
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

@bot.message_handler(commands=['rules'])
def send_rules(message):
    try:
        chat_id = message.chat.id
        bot.send_message(chat_id, "You need to answer three questions about each match:\n1. Who will win the game or will there be a draw?\n2. What will be the difference of team goals?\n3. Total of the match?\nYou get 3 points for each correct answer. If all 3 answers are correct, you get an additional point.")
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

@bot.message_handler(commands=['setname'])
def set_name(message):
    try:
        msg = bot.reply_to(message, "What is your name?")
        bot.register_next_step_handler(msg, process_name)
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

def process_name(message):
    try:
        chat_id = message.chat.id
        name = message.text
        db_access.add_name(chat_id, name)
        bot.send_message(chat_id, "Nice to meet you, " + name + "!")
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

@bot.message_handler(commands=['setgroup'])
def set_group(message):
    try:
        msg = bot.reply_to(message, "Type the name of the group you want to be added to:")
        bot.register_next_step_handler(msg, process_group)
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

def process_group(message):
    try:
        chat_id = message.chat.id
        group_name = message.text
        db_access.add_group(chat_id, group_name)
        bot.send_message(chat_id, "You were added to the group " + group_name + "!")
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

@bot.message_handler(commands=['predict'])
def send_predict(message):
    try:
        chat_id = message.chat.id
        global team1
        global team2
        global pred
        pred = Prediction(chat_id)
        next_match = db_access.get_next_match(chat_id)
        if(next_match == 0):
            bot.send_message(chat_id, "Sorry! There are no matches in our database you can currently predict!")
        else:
            pred.matchid = [c['match_no'] for c in next_match][0]
            team1 = [c['team_1'] for c in next_match][0]
            team2 = [c['team_2'] for c in next_match][0]
            stage = [c['type'] for c in next_match][0]
            quote = [c['quote'] for c in next_match][0]
            if (stage == 'Group'):
                stage = stage + ' ' + [c['group'] for c in next_match][0]
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            team1button = types.KeyboardButton(team1)
            team2button = types.KeyboardButton(team2)
            drawbutton = types.KeyboardButton("Draw")
            markup.add(team1button, team2button, drawbutton)
            msg = bot.reply_to(message, stage + ': ' + team1 + ' vs. ' + team2 + '(Quote: ' + str(quote) + ')\n Who will win the game?', reply_markup=markup)
            bot.register_next_step_handler(msg, process_win_step)
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

def process_win_step(message):
    try:
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
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

def process_goal_step(message):
    try:
        chat_id = message.chat.id
        global pred
        pred.goal = int(message.text)
        underbutton = types.KeyboardButton('< 2.5')
        overbutton = types.KeyboardButton('> 2.5')
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(underbutton, overbutton)
        msg = bot.reply_to(message, 'How many goals will the teams score?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_total_step)
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

def process_total_step(message):
    try:
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
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    return (0)
    # bot.reply_to(message, "Unfortunately we do not support free text. If you see this message, something went wrong (or you just typed some text the bot can not understand).")

bot.polling()