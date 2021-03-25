import logging
import os
import telegram as tl
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from script import config as keys
import re
from pymongo import MongoClient

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# config vars
PORT = keys.port
TOKEN = keys.telegram_key
MONGO = keys.mongodb_key
APP_NAME = 'https://compasschatbot.herokuapp.com/'

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

# setup bot
bot = Updater(TOKEN, use_context=True)

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
    try:
        temp_profile['_id'] = kwargs['id']
        temp_profile['first_name'] = kwargs['firstname']
        temp_profile['username'] = kwargs['username']
    except:
        print('Not in state to save ID')

    try:
        temp_profile['domisili'] = kwargs['dom']
    except:
        print('Not in state to save domisili')
    
    try:
        temp_profile['gender'] = kwargs['gen']
    except:
        print('Not in state to save gender')

    try:
        temp_profile['age'] = kwargs['age']
    except:
        print('Not in state to save age')

    if save == True:
        return db.insert_one(temp_profile), temp_profile
    else:
        return temp_profile

def update_dest(save=False, **kwargs):
    temp_dest['destination'] = kwargs['d']
    temp_dest['time'] = kwargs['t']
    return temp_dest

# /start
def start(update, context):
    """Send a message when the command /start is issued."""
    url = 'https://cdn1.vectorstock.com/i/thumb-large/47/45/cartoon-comical-character-bali-kids-vector-34684745.jpg'
    text1 = "Hai..!! <b>welcome to ChavellBot </b>\nPanggil saja kami <b><i>Chavel</i></b>, disini kami akan memandu anda untuk keliling Indonesia.\nUpss sabar, untuk dapat menggunakan fitur ini secara optimal, kami butuh data diri anda, bersediakan anda? (<b><i>yes/no</i></b>)"
    text2 = f"Hai {update.message.from_user['first_name']}! \nSudah tahu mau liburan kemana? Chavel punya rekomendasi nih special buat kamu."
    kboard = [
            [
                tl.InlineKeyboardButton('Bali', callback_data='BALI'),
                tl.InlineKeyboardButton('Danau Toba', callback_data='DNTOBA'),
                tl.InlineKeyboardButton('Yogyakarta', callback_data='YGY')
            ],
            [
                tl.InlineKeyboardButton('Labuan Bajo', callback_data='LABBJO'),
                tl.InlineKeyboardButton('Likupang', callback_data='LKP'),
                tl.InlineKeyboardButton('Mandalika', callback_data='MDL')
            ]
        ]
    context.bot.send_photo(chat_id=update.message.from_user['id'], photo=url)
    if update.message.from_user['first_name'] not in first_name:
        update.message.reply_text(text1, parse_mode=tl.ParseMode.HTML, reply_markup=tl.ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True))
        return WELCOME1
    else:
        reply_markup = tl.InlineKeyboardMarkup(kboard)
        update.message.reply_text('<b>Welcome back to ChavellBot</b>', parse_mode=tl.ParseMode.HTML)
        update.message.reply_text(text2, reply_markup = reply_markup)
        return WELCOME2

def welcome1(update, context):
    if update.message.text.lower() in ['yes', 'ya', 'y']:
        update_data(id=update.message.from_user['id'], firstname=update.message.from_user['first_name'], username=update.message.from_user['username'])
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
        bot.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN)
        bot.bot.set_webhook(APP_NAME + TOKEN)

    # bot.idle()

if __name__ == '__main__':
    main()