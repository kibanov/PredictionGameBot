from datetime import datetime, timedelta
import telebot
import yaml

import db_access

config = yaml.safe_load(open("conf.yml"))

bot = telebot.TeleBot(config["token"])


def remind_user(user, matches):
    try:
        if ('predicted_matches' in user):
            predicted_matches = user['predicted_matches']
        else:
    	    predicted_matches = []
        matches_to_remind = [c for c in matches if c['match_no'] not in predicted_matches]
        no_of_matches_to_remind = len(matches_to_remind)
        if (no_of_matches_to_remind > 0):
            chat_id = user['user_id']
            if (no_of_matches_to_remind == 1):
                remind_text = 'Do not forget to make your predictions today! You have 1 more prediction to make today:\n'
            else:
                remind_text = 'Do not forget to make your predictions today! You have ' + str(no_of_matches_to_remind) + ' more predictions to make today:\n'
            for match in matches_to_remind:
                remind_text = remind_text + match['team_1'] + ' vs. ' + match['team_2'] + '\n'
            remind_text = remind_text + 'Type /predict to make predictions!'
            bot.send_message(chat_id, remind_text)
            print(str(datetime.now()) + ': the reminder was sent to ' + str(chat_id))
    except Exception as e:
        print('Exception thrown, the reason needs to be investigated! chat_id: ' + str(chat_id))

def remind():
    try:
        today_matches = db_access.today_matches()
        all_users = db_access.get_all_users()
        for user in all_users:
           remind_user(user, today_matches)
    except Exception as e:
        print('Exception thrown (the reason needs to be investigated!')

def main():
    remind()


if __name__ == '__main__':
    main()