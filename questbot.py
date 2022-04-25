from email import message
import logging
import os
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Updater,
    Filters,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
)
from telegram.chataction import ChatAction
from time import sleep


BOT_ENV = os.getenv('BOT_ENV')
TOKEN = os.getenv('TG_TOKEN')

if BOT_ENV == 'prod':
    APP_NAME = 'https://ge-random-coffee.herokuapp.com/'
    PORT = int(os.environ.get('PORT', '8443'))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

INTRO, QUESTION_01, QUESTION_02 = range(3)



def start(update: Update, context: CallbackContext) -> int:
    keyboard = [[
        InlineKeyboardButton('Погнали!', callback_data='1'), 
        InlineKeyboardButton('Я передумал', callback_data='2') ]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        'Привет! 🙌 Я квест-бот.'
    )
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    sleep(0.5)
    update.message.reply_text('Готов разгадать пару головоломок?', reply_markup=reply_markup)
    return INTRO

def intro(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data == '1':
        query.edit_message_text('>> Погнали!')
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        sleep(0.5)
        # Question 1
        query.message.reply_text('Сколько будет 2+2?')
        return QUESTION_01
    else:
        query.delete_message()
        query.message.reply_text('Пока!')
        return ConversationHandler.END

def answer_right(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Красава!')
    
    keyboard = [['Следующий', 'Заканчиваем']]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    update.message.reply_text('Давай следующий вопрос?', reply_markup = reply_markup)
    return QUESTION_02

def question_02(update: Update, context: CallbackContext):
    ans = update.message.text
    if ans == 'Следующий':
        reply_markup = ReplyKeyboardRemove()
        update.message.reply_text('Удаляю клаву', reply_markup= reply_markup)
    elif ans == 'Заканчиваем':
        update.message.reply_text('Не удаляю клаву')
    return ConversationHandler.END

def answer_wrong(update, context) -> int:
    update.message.reply_text('Подумай еще')
    return QUESTION_01


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user.username
    logger.info(f'User {user} canceled the conversation')
    update.message.reply_text('Пока 🖖')
    return ConversationHandler.END


def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            INTRO: [CallbackQueryHandler(intro)],

            QUESTION_01: [
                MessageHandler(Filters.regex('^4$') & ~Filters.command, answer_right),
                MessageHandler(Filters.text & ~Filters.command, answer_wrong)
                ],
            QUESTION_02: [
                MessageHandler(Filters.regex('(Следующий|Заканчиваем)'), question_02)
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