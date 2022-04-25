import logging
import os
from dbhelper import DBHelper

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
)


BOT_ENV = os.getenv('BOT_ENV')
TOKEN = os.getenv('TG_TOKEN')

if BOT_ENV == 'prod':
    APP_NAME = 'https://ge-random-coffee.herokuapp.com/'
    PORT = int(os.environ.get('PORT', '8443'))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

INTRO, BIO = range(2)


def start(update: Update, context: CallbackContext) -> int:
    keyboard = [[InlineKeyboardButton('Поехали!', callback_data='1')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Привет! 🙌 Я Random Coffee бот. \n\n'
        'Каждую неделю я буду знакомить тебя с новыми интересными людьми.'
        ' Встречи могут проходить в офлайне или онлайне, на твой выбор.\n\n'
        'Чтобы принять участие во встречах, тебе нужно ответить на несколько вопросов.'
    )
    update.message.reply_text('Ну что, погнали?', reply_markup=reply_markup)
    return INTRO

def intro(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    logger.info(f'Button push: {query.data}')

    query.answer()
    query.edit_message_text(
        '>> Поехали!'
    )
    query.message.reply_text('Расскажи в нескольких предложениях о себе')

    return BIO

def bio(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user.username
    answer = update.message.text
    logger.info(f'Bio of {user}: {update.message.text}')


    update.message.reply_text('Принял!')
    return ConversationHandler.END


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    user = query.from_user.username

    conn = DBHelper()

    if query.data == 'remove':
        conn.delete_user(user)
        answer_text = f'User {user} removed'
    elif query.data == 'signup':
        conn.add_user(user)
        answer_text = f'User {user} added'

    query.answer(answer_text)
    query.edit_message_text(answer_text)


def getusers(update: Update,context: CallbackContext) -> None:
    db = DBHelper()
    users = db.get_users()
    update.message.reply_text(users)

def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user.username
    logger.info(f'User {user} canceled the conversation')
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    conn = DBHelper()
    conn.setup()

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            INTRO: [CallbackQueryHandler(intro)],
            BIO: [
                MessageHandler(Filters.text & ~Filters.command, bio)
                ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]

    )

    dispatcher.add_handler(conv_handler)

    if BOT_ENV == 'prod':
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN,
                              webhook_url = APP_NAME + TOKEN)
    else:
        updater.start_polling(timeout=10)

    updater.idle()


if __name__ == '__main__':
    main()