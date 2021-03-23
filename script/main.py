import config as keys
import telegram as tl
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import logging
import re
from pymongo import MongoClient
# from flask import Flask, request
import threading

# setup bot
bot = Updater(keys.telegram_key, use_context=True)

# setup flask
# app = Flask(__name__)

# setup db
cluster = MongoClient(keys.mongodb_key)
db = cluster['compass_chatbot']['user_profile']

# setup data
global temp_profile
temp_profile = {}
global temp_dest
temp_dest = {}

first_name = []
for i in db.find({}):
    first_name.append(i['first_name'])

def update_data(save=False, **kwargs):
    temp_profile['_id'] = kwargs['id']
    temp_profile['first_name'] = kwargs['firstname']
    temp_profile['username'] = kwargs['username']
    temp_profile['domisili'] = kwargs['dom']
    temp_profile['gender'] = kwargs['gen']
    temp_profile['age'] = kwargs['age']
    if save == True:
        return db.insert_one(temp_profile), temp_profile
    else:
        return temp_profile

def update_dest(save=False, **kwargs):
    temp_dest['destination'] = kwargs['d']
    temp_dest['time'] = kwargs['t']
    return temp_dest

# States, as integers
WELCOME1 = 0
WELCOME2 = 1
STARTAGAIN = 2
PROFILE_A = 3
PROFILE_B = 4
PROFILE_C = 5
SAVEDATA = 6
DESTIN = 7
TIME = 8
TRAVELPLAN = 9
CANCEL = 100

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# /start
def start(update, context):
    update.message.reply_text('Haloo...')
    if update.message.from_user['first_name'] not in first_name:
        update.message.reply_text('Selamat datang, untuk dapat menggunakan fitur ini secara optimal, kami butuh data diri anda, bersediakan anda?',
                                    reply_markup=tl.ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True))
        return WELCOME1
    else:
        update.message.reply_text('Kenalin nama aku Compass-Bot.')
        update.message.reply_text('Disini aku bakalan bantuin kalian nih untuk explore Indonesia.')
        update.message.reply_text('Kalian butuh info apa nih?',
                                    reply_markup=tl.ReplyKeyboardMarkup([['Mau tau tempat oke dong!', 'Bikinin itinerary bisa kali!']], one_time_keyboard=True))
        return WELCOME2

def welcome1(update, context):
    if update.message.text.lower() in ['yes', 'ya', 'y']:
        update_data(kw='id', id=update.message.from_user['id'], firstname=update.message.from_user['first_name'], username=update.message.from_user['username'])
        update.message.reply_text('Dimanakah anda berdomisili saat ini?')
        return PROFILE_A
    else:
        return CANCEL

def profile_a(update, context):
    update_data(dom=update.message.text)
    update.message.reply_text('Gender anda?',
                                reply_markup=tl.ReplyKeyboardMarkup([['Pria', 'Wanita']], one_time_keyboard=True))
    return PROFILE_B

def profile_b(update, context):
    update_data(gen=update.message.text)
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
        keyboard = [[tl.InlineKeyboardButton('Danau Toba', url='https://travelspromo.com/htm-wisata/danau-toba-sumatera-utara/', callback_data=1)],
                    [tl.InlineKeyboardButton('Bali', url='https://travelspromo.com/?s=bali', callback_data=2)],
                    [tl.InlineKeyboardButton('Likupang', url='https://www.idntimes.com/travel/destination/prila-arofani/tempat-wisata-di-likupang-destinasi-super-prioritas/1', callback_data=3)],
                    [tl.InlineKeyboardButton('Jogjakarta', url='https://travelspromo.com/?s=jogja', callback_data=4)],
                    [tl.InlineKeyboardButton('Mandalika', url='https://travelspromo.com/?s=mandalika', callback_data=5)],
                    [tl.InlineKeyboardButton('Labuan Bajo', url='https://travelspromo.com/?s=labuan+bajo', callback_data=6)]]
        reply_markup = tl.InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Ini nih tempat-tempat keren dan populer yang bisa kalian pilih saat ini:', reply_markup = reply_markup)
        return CANCEL
    elif 'itinerary' in update.message.text or ('travel' in update.message.text and 'plan' in update.message.text):
        update.message.reply_text('Cerita mau kemana kamu?')
        return DESTIN

def destination(update, context):
    destinasi = update.message.text
    update_dest(kw='d', d=destinasi)
    update.message.reply_text(f"{destinasi} emang destinasi keren sih, kapan kesana?")
    return TIME

def definetime(update, context):
    waktu = update.message.text
    update_dest(kw='t', t=waktu)
    update.message.reply_text(f"{waktu} waktu yang tepat sih.")
    return TRAVELPLAN

def cancel(update, context):
    update.message.reply_text(f"Anda memilih {update.message.text}")
    return ConversationHandler.END

# @app.route('/{}'.format(keys.telegram_key), methods=['POST'])
def main():
    dp = bot.dispatcher
    yes_no_regex = re.compile(r'^(yes|no|ya|y|n|tidak|tdk)$', re.IGNORECASE)

    handler = ConversationHandler(
                entry_points=[CommandHandler('start', start)],
                states={
                    WELCOME1: [MessageHandler(Filters.regex(yes_no_regex), welcome1)],
                    WELCOME2: [MessageHandler(Filters.regex(re.compile(r'\w+')), welcome2)],
                    PROFILE_A: [MessageHandler(Filters.regex(re.compile(r'\w+')), profile_a)],
                    PROFILE_B: [MessageHandler(Filters.regex(re.compile(r'^\w+$')), profile_b)],
                    PROFILE_C: [MessageHandler(Filters.regex(re.compile(r'\w+')), profile_c)],
                    STARTAGAIN: [MessageHandler(Filters.regex(yes_no_regex), startagain)],
                    DESTIN: [MessageHandler(Filters.regex(re.compile(r'\w+')), destination)],
                    TIME: [MessageHandler(Filters.regex(re.compile(r'\w+')), definetime)]
                },
                fallbacks=[CommandHandler('cancel', cancel)]
            )
    dp.add_handler(handler)
    if keys.ENV == 'DEV':
        bot.start_polling()
    elif keys.ENV == 'PROD':
        bot.start_webhook(listen='0.0.0.0', port=keys.port, url_path=keys.telegram_key)
        bot.bot.set_webhook('https://compasschatbot.herokuapp.com/' + keys.telegram_key)

    # if keys.ENV == 'DEV':
    #     updater.start_polling()
    #     # updater.idle()
    # elif keys.ENV == 'PROD':
    #     updater.start_webhook(listen=keys.host, port=keys.port, url_path=keys.telegram_key, webhook_url='https://compasschatbot.herokuapp.com/' + keys.telegram_key)
    #     updater.idle()

# main()

# run
if __name__ == '__main__':
    main()