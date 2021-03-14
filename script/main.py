import constant as keys
import telegram as tl
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging
import re
import pandas as pd
from os import getcwd
from os.path import join, dirname

# references: https://www.thepythoncode.com/article/make-a-telegram-bot-in-python
# States, as integers
WELCOME1 = 0
WELCOME2 = 1
STARTAGAIN = 2
PROFILE_A = 3
PROFILE_B = 4
PROFILE_C = 5
SAVEDATA = 6
CANCEL = 100

user_profile = pd.read_csv(join('data', 'user_profile.csv'))
temp_profile = {
    'id': [],
    'first_name': [],
    'username': [],
    'domisili': [],
    'gender': [],
    'age': []
}

def start(update, context):

    update.message.reply_text('Haloo...')
    if update.message.from_user['first_name'] not in user_profile.values:
        update.message.reply_text('Selamat datang, untuk dapat menggunakan fitur ini secara optimal, kami butuh data diri anda, bersediakan anda?',
                                    reply_markup=tl.ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True))
        return WELCOME1
    else:
        update.message.reply_text('Kenalin nama aku Compass-Bot.')
        update.message.reply_text('Disini aku bakalan bantuin kalian nih untuk explore Indonesia.')
        update.message.reply_text('Kalian butuh info apa nih?',
                                    reply_markup=tl.ReplyKeyboardMarkup([['Mau tau tempat oke dong!', 'Bikinin itinerary bisa kali!']], one_time_keyboard=True))
        return WELCOME2

def update_data(kw, save=False, **kwargs):
    global user_profile, temp_profile
    if kw == 'id':
        temp_profile['id'] = [kwargs['id']]
        temp_profile['first_name'] = [kwargs['firstname']]
        temp_profile['username'] = [kwargs['username']]

    if kw == 'dom':
        temp_profile['domisili'] = [kwargs['dom']]
    
    if kw == 'gen':
        temp_profile['gender'] = [kwargs['gen']]

    if kw == 'age':
        temp_profile['age'] = [kwargs['age']]

    if save == True:
        df = pd.DataFrame.from_dict(temp_profile)
        user_profile = user_profile.append(df, ignore_index=True)
        return user_profile.to_csv(join('data', 'user_profile.csv'), index=False), temp_profile
    else:
        return temp_profile

def welcome1(update, context):
    if update.message.text.lower() in ['yes', 'ya', 'y']:
        update_data(kw='id', id=update.message.from_user['id'], firstname=update.message.from_user['first_name'], username=update.message.from_user['username'])
        update.message.reply_text('Dimanakah anda berdomisili saat ini?')
        return PROFILE_A
    else:
        return CANCEL

def profile_a(update, context):
    update_data(kw='dom', dom=update.message.text)
    update.message.reply_text('Gender anda?',
                                reply_markup=tl.ReplyKeyboardMarkup([['Pria', 'Wanita']], one_time_keyboard=True))
    return PROFILE_B

def profile_b(update, context):
    update_data(kw='gen', gen=update.message.text)
    update.message.reply_text('Berapakah umur anda saat ini?')
    return PROFILE_C

def profile_c(update, context):
    update_data(kw='age', save=True, age=update.message.text)
    update.message.reply_text('Terimakasih atas ketersediaan anda.')
    update.message.reply_text('Data akan kami simpan.')
    update.message.reply_text('Apakah anda ingin melanjutkan?',
                                reply_markup=tl.ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True))
    return STARTAGAIN

def startagain(update, context):
    update.message.reply_text('Kalian butuh info apa nih?',
                                reply_markup=tl.ReplyKeyboardMarkup([['Mau tau tempat oke dong!', 'Bikinin itinerary bisa kali!']], one_time_keyboard=True))
    return WELCOME2

def welcome2(update, context):
    if 'oke' in update.message.text:
        # update.message.reply_text('Ini nih tempat-tempat keren yang populer saat ini:')
        # update.message.reply_text('1. Danau Toba')
        # update.message.reply_text('2. Bali')
        # update.message.reply_text('3. Likupang')
        # update.message.reply_text('4. Jogjakarta')
        # update.message.reply_text('5. Mandalika')
        # update.message.reply_text('6. Labuan Bajo')
        # update.message.reply_text('Mau pilih yang mana nih?', reply_markup=tl.ReplyKeyboardMarkup([['Danau Toba', 'Bali', 'Likupang', 'Jogjakarta', 'Mandalika', 'Labuan Bajo']], one_time_keyboard=True))
        keyboard = [tl.InlineKeyboardButton('Danau Toba', callback_data='1'),
                    tl.InlineKeyboardButton('Bali', callback_data='2'),
                    tl.InlineKeyboardButton('Likupang', callback_data='3'),
                    tl.InlineKeyboardButton('Jogjakarta', callback_data='4'),
                    tl.InlineKeyboardButton('Mandalika', callback_data='5'),
                    tl.InlineKeyboardButton('Labuan Bajo', callback_data='6')]

        reply_markup = tl.InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Ini nih tempat-tempat keren dan populer yang bisa kalian pilih saat ini:', reply_markup = reply_markup)
        return CANCEL
    elif 'itinerary' in update.message.text:
        update.message.reply_text('Fitur itinerary sedang dalam tahap development', reply_markup=tl.ReplyKeyboardMarkup([['Ok']], one_time_keyboard=True))
        return CANCEL

def cancel(update, context):
    update.message.reply_text(f"Anda memilih {update.message.text}")
    return ConversationHandler.END

def main():
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher
    yes_no_regex = re.compile(r'^(yes|no|ya|y|n|tidak|tdk)$', re.IGNORECASE)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    handler = tl.ext.ConversationHandler(
                entry_points=[CommandHandler('start', start)],
                states={
                    WELCOME1: [MessageHandler(Filters.regex(yes_no_regex), welcome1)],
                    WELCOME2: [MessageHandler(Filters.regex(re.compile(r'\w+')), welcome2)],
                    PROFILE_A: [MessageHandler(Filters.regex(re.compile(r'\w+')), profile_a)],
                    PROFILE_B: [MessageHandler(Filters.regex(re.compile(r'^\w+$')), profile_b)],
                    PROFILE_C: [MessageHandler(Filters.regex(re.compile(r'\w+')), profile_c)],
                    STARTAGAIN: [MessageHandler(Filters.regex(yes_no_regex), startagain)],
                },
                fallbacks=[CommandHandler('cancel', cancel)]
            )
    dp.add_handler(handler)

    updater.start_polling()
    updater.idle()

main()