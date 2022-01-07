from telegram.ext import ConversationHandler
from telegram import ParseMode
import os
import time
import json
import base64
from tabscanner_functions import callProcess, callResult
from helper_functions import format_line_items

TABSCANNER_TOKEN = os.environ['TABSCANNER_TOKEN']
WEBAPP_LINK = 'http://google/split'


# First time starting the bot
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to PayMeLah Bot!",
                             parse_mode='HTML')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Start the bill splitting process with one of the following commands: "
                                  + "\n\n/upload - Upload a receipt image to be parsed"
                                  + "\n/split - Begin bill splitting without receipt parsing")


PARSE = range(1)


def ask_for_receipt(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Send me image of your receipt",
                             parse_mode='HTML')
    return PARSE


def parse_receipt(update, context):
    receipt_photo = update.message.photo[-1]
    file_id = receipt_photo.file_id
    photo = context.bot.get_file(file_id)
    photo_file = photo.download("{}.jpg".format(file_id))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Parsing receipt",
                             parse_mode='HTML')

    output = callProcess(TABSCANNER_TOKEN, "{}.jpg".format(file_id))
    status = output['status']
    output_token = output['token']

    time.sleep(7)
    result = callResult(TABSCANNER_TOKEN, output_token)
    while (result['status'] == 'pending'):
        time.sleep(3)
        result = callResult(TABSCANNER_TOKEN, output_token)
    if (result['status'] == 'failed'):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Image parsing failed",
                                 parse_mode='HTML')
    else:
        data = {
            'lineItems': format_line_items(result),
            'chatId': update.effective_chat.id,
            'users': [update.effective_user.username]
        }
        stringified_data = json.dumps(data)
        encoded_utf = stringified_data.encode('utf-8')
        encoded_base64 = base64.b64encode(encoded_utf)
        url = "{}/{}".format(WEBAPP_LINK, str(encoded_base64)[2:-1])
        message = "Start your bill splitting process <a href='{}'>here</a>".format(url)
        print(message)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message,
                                 parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def cancel(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Upload cancelled",
                             parse_mode='HTML')
    return ConversationHandler.END
