import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BOT_ENV = 'prod'

if BOT_ENV == 'prod':
    TOKEN = '5151383399:AAHijezjPaSYIa-U1mBKvkJNuLBohCLEVzk'
    APP_NAME = 'https://ge-random-coffee.herokuapp.com/'
    PORT = int(os.environ.get('PORT', '8443'))
else:
    TOKEN = '5192806492:AAEpnMrgpsg7UCALqyHMKZ8NVSqIXufb-qA'


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    """Send a message when the command /start is issued."""
    username = update.message.chat.username
    update.message.reply_text(f'Hey {username}!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    # update.message.reply_text(update.message.text)
    update.message.reply_text(update.message.chat.username)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
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