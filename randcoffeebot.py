import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from dbhelper import DBHelper

BOT_ENV = os.getenv('BOT_ENV')
TOKEN = os.getenv('TG_TOKEN')

if BOT_ENV == 'prod':
    APP_NAME = 'https://ge-random-coffee.herokuapp.com/'
    PORT = int(os.environ.get('PORT', '8443'))

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
    conn = DBHelper()
    users = conn.get_users()
    user = update.effective_user.username

    if user in users:
        keyboard = [[InlineKeyboardButton('Remove', callback_data='remove')]]
    else:
        keyboard = [[InlineKeyboardButton('Signup', callback_data='signup')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Choose', reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
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


def help_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    """Run the bot."""
    # Setup database
    conn = DBHelper()
    conn.setup()

    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('getusers', getusers))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    # Start the Bot
    if BOT_ENV == 'prod':
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN,
                              webhook_url = APP_NAME + TOKEN)
    else:
        updater.start_polling(timeout=10)

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()