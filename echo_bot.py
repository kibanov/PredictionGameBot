import telebot
import yaml
import sys
from telebot import types

import db_access

config = yaml.safe_load(open("conf.yml"))

bot = telebot.TeleBot(config["token"])

match_dict = {}
pred_dict = {}

class Prediction:
    def __init__(self, uid):
        self.userid = uid
        self.matchid = None
        self.win = None
        self.goal = None
        self.total = None

class Match:
    def __init__(self, teamname1, teamname2):
        self.team1 = teamname1
        self.team2 = teamname2


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
            '/rules Show rules\n' +
            '/today See what happens today')
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

@bot.message_handler(commands=['rules'])
def send_rules(message):
    try:
        chat_id = message.chat.id
        bot.send_message(chat_id, "You need to answer three questions about each match:\n1. Who will win the game or will there be a draw?\n2. What will be the difference of team goals?\n3. Total of the match?\nYou get 3 points for each correct answer. If all 3 answers are correct, you get an additional point.")
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

@bot.message_handler(commands=['today'])
def send_today_info(message):
    try:
        chat_id = message.chat.id
        today_matches = db_access.today_matches()
        if (len(today_matches) == 0):
            bot.send_message(chat_id, 'No matches today!')
        today_matches_ids = [c['match_no'] for c in today_matches]
        user_profile = db_access.get_user(chat_id)
        info_text = 'Matches and your predictions for today:\n'
        if (user_profile == 0):
            return (0)
        else:
            user_predictions = user_profile['predictions']
            today_user_prediction_ids = [c['match_no'] for c in user_predictions if c['match_no'] in today_matches_ids]
            for match in today_matches:
                info_text = info_text + match['team_1'] + " vs. " + match['team_2'] + ': '
                if match['match_no'] in today_user_prediction_ids:
                    prediction = [c for c in user_predictions if c['match_no'] == match['match_no']][0]
                    if (prediction['winner'] == 0):
                        info_text = info_text + 'Draw '
                        info_text = info_text + str(prediction['goals']) + ':' + str(prediction['goals']) + ', ' 
                    else:
                        if (prediction['winner'] == 1):
                            info_text = info_text + match['team_1']
                        elif (prediction['winner'] == 2):
                            info_text = info_text + match['team_2']
                        info_text = info_text + ' by ' + str(prediction['goals']) + ' goals, '
                    if (prediction['total'] == 0):
                        info_text = info_text + '<2.5'
                    elif (prediction['total'] == 1):
                        info_text = info_text + '>2.5'
                else:
                    info_text = info_text + 'No prediction (yet)'
                info_text = info_text + '\n'
            info_text = info_text + 'Click /predict to make Predictions!'
            bot.send_message(chat_id, info_text)
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
        pred = Prediction(chat_id)
        pred_dict[chat_id] = pred
        next_match = db_access.get_next_match(chat_id)
        if(next_match == 0):
            bot.send_message(chat_id, "Sorry! There are no matches in our database you can currently predict!")
        else:
            pred.matchid = [c['match_no'] for c in next_match][0]
            team1 = [c['team_1'] for c in next_match][0]
            team2 = [c['team_2'] for c in next_match][0]
            match = Match(team1, team2)
            match_dict[chat_id] = match
            stage = [c['type'] for c in next_match][0]
            quote = [c['quote'] for c in next_match][0]
            if (stage == 'Group'):
                stage = stage + ' ' + [c['group'] for c in next_match][0]
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            team1button = types.KeyboardButton(match.team1)
            team2button = types.KeyboardButton(match.team2)
            drawbutton = types.KeyboardButton("Draw")
            markup.add(team1button, team2button, drawbutton)
            msg = bot.reply_to(message, stage + ': ' + match.team1 + ' vs. ' + match.team2 + '(Quote: ' + str(quote) + ')\n Who will win the game?', reply_markup=markup)
            bot.register_next_step_handler(msg, process_win_step)
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')
        print("Unexpected error:", sys.exc_info()[0])

def process_win_step(message):
    try:
        chat_id = message.chat.id
        match = match_dict[chat_id]
        print("Prediction started for the match: " + match.team1 + " vs. " + match.team2)
        pred = pred_dict[chat_id]
        if (message.text == match.team1):
            pred.win = 1
        elif (message.text == match.team2):
            pred.win = 2
        elif (message.text == u'Draw'):
            pred.win = 0
        else:
            bot.send_message(chat_id, "Error!")
        print("Chat id: " + str(chat_id) + "; Prediction: " + message.text + ' (' + str(pred.win) + ')')
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
        pred = pred_dict[chat_id]
        print("Chat id: " + str(chat_id) + "; Prediction: " + message.text)
        pred.goal = int(message.text)
        underbutton = types.KeyboardButton('< 2.5')
        overbutton = types.KeyboardButton('> 2.5')
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(underbutton, overbutton)
        msg = bot.reply_to(message, 'How many goals will the teams score?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_total_step)
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')
        print("Unexpected error:", sys.exc_info()[0])

def process_total_step(message):
    try:
        chat_id = message.chat.id
        pred = pred_dict[chat_id]
        print("Chat id: " + str(chat_id) + "; Prediction: " + message.text)
        if (message.text == '< 2.5'):
            pred.total = 0
        elif (message.text == '> 2.5'):
            pred.total = 1
        else:
            msg = bot.send_message(chat_id, "Error!")
        db_access.add_prediction(pred.userid, pred.matchid, pred.win, pred.goal, pred.total)
        bot.send_message(chat_id, "Your prediction for this game is saved! Click /predict to make the next prediction! Click /today to see today's matches and your predictions!")
    except Exception as e:
        bot.reply_to(message, 'Something went wrong! Please, contact the provider of this bot!')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    return (0)
    # bot.reply_to(message, "Unfortunately we do not support free text. If you see this message, something went wrong (or you just typed some text the bot can not understand).")

bot.polling()