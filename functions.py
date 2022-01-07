from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, InlineQueryHandler, \
    CallbackQueryHandler, DictPersistence
import os
from tabscanner_functions import callProcess


TABSCANNER_TOKEN = os.environ['TABSCANNER_TOKEN']


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
    receipt_photo = update.message.photo[0]
    file_id = receipt_photo.file_id
    photo_file = context.bot.get_file(file_id).download("{}.jpg".format(file_id))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Parsing receipt",
                             parse_mode='HTML')

    # output = callProcess(TABSCANNER_TOKEN, "{}.jpg".format(file_id))
    # print(output)
    print(open("{}.jpg".format(file_id)))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Start your bill splitting process here: \nLink Here",
                             parse_mode='HTML')
    return ConversationHandler.END


def cancel(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Upload cancelled",
                             parse_mode='HTML')
    return ConversationHandler.END