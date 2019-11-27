import logging
import telegram
from telegram.ext import Updater, CommandHandler
import os
import time
import json
import requests
import datetime as dt

BOT_TOKEN = 'your_telegram_bot_token_here'
BASE_PATH = 'your_api_base_path_here'
ON = "on"
OFF = "off"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text('Welcome ! you can \'turn_on\' and \'turn_off\' the Grotta alarm')

def help(update, context):
    update.message.reply_text('You can type \'turn_on\' and \'turn_off\' in order to handle the alarm at Grotta home!')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def turn_on(update, context):
    requests.get(BASE_PATH, params={'status': ON, 'delay': 5})
    context.bot.send_message(chat_id=update.message.chat_id, text="*** Turning on the alarm in 5 minutes ***", parse_mode=telegram.ParseMode.MARKDOWN)

def turn_off(update, context):
    requests.get(BASE_PATH, params={'status': OFF, 'delay': 0})
    context.bot.send_message(chat_id=update.message.chat_id, text="*** Alarm is OFF. You are ready to go! ***", parse_mode=telegram.ParseMode.MARKDOWN)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("turn_on", turn_on))
    dp.add_handler(CommandHandler("turn_off", turn_off))
    
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
