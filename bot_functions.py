from telegram.ext import ConversationHandler
from telegram import ParseMode
import os
import time
import json
import base64
from tabscanner_functions import callProcess, callResult
from helper_functions import format_line_items

TABSCANNER_TOKEN = os.environ['TABSCANNER_TOKEN']
WEBAPP_LINK = 'https://paymelah.vercel.app/split'

money_emoji = '\U0001F4B8'
receipt_emoji = '\U0001F9FE'
divide_emoji = '\U00002797'
sad_shocked_emoji = '\U0001F616'
hourglass_emoji = '\U0000231B'
robot_emoji = '\U0001F916'


# First time starting the bot
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to PayMeLah Bot! {}{}{}{}{}".format(money_emoji, money_emoji, money_emoji,
                                                                               money_emoji, money_emoji))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Start the bill splitting process with one of the following commands: "
                                  + "\n\n/upload {} - Upload a receipt image to be parsed".format(receipt_emoji)
                                  + "\n/split {} - Begin bill splitting without receipt parsing".format(divide_emoji))


PARSE = range(1)


def ask_for_receipt(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Please send me a clear image of your {} Receipt {}".format(receipt_emoji,
                                                                                              receipt_emoji))
    return PARSE


def parse_receipt(update, context):
    receipt_photo = update.message.photo[-1]
    file_id = receipt_photo.file_id
    photo = context.bot.get_file(file_id)
    photo.download("{}.jpg".format(file_id))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="The {}Robots{} have begun parsing your receipt...".format(robot_emoji, robot_emoji),
                             parse_mode='HTML')

    output = callProcess(TABSCANNER_TOKEN, "{}.jpg".format(file_id))
    status = output['status']
    output_token = output['token']

    if status != 'success':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Image parsing failed {}".format(sad_shocked_emoji),
                                 parse_mode='HTML')

    countdown(update, context, 7)

    result = callResult(TABSCANNER_TOKEN, output_token)
    while result['status'] == 'pending':
        time.sleep(2)
        result = callResult(TABSCANNER_TOKEN, output_token)
    if result['status'] == 'failed':
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Image parsing failed {}".format(sad_shocked_emoji),
                                 parse_mode='HTML')
    else:
        data = {
            'lineItems': format_line_items(result),
            'chatId': update.effective_chat.id,
            'users': [update.effective_user.username]
        }
        if len(data['lineItems']) < 1:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Image parsing failed {}... Try sending a clearer image or use /split to "
                                          "start splitting anyway".format(sad_shocked_emoji),
                                     parse_mode='HTML')
            return ConversationHandler.END
        stringified_data = json.dumps(data)
        encoded_utf = stringified_data.encode('utf-8')
        encoded_base64 = base64.b64encode(encoded_utf)
        url = "{}/{}".format(WEBAPP_LINK, str(encoded_base64)[2:-1])
        message = "Start your bill splitting process <a href='{}'>here</a>".format(url)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=message,
                                 parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def split(update, context):
    data = {
        'lineItems': [],
        'chatId': update.effective_chat.id,
        'users': [update.effective_user.username]
    }
    stringified_data = json.dumps(data)
    encoded_utf = stringified_data.encode('utf-8')
    encoded_base64 = base64.b64encode(encoded_utf)
    url = "{}/{}".format(WEBAPP_LINK, str(encoded_base64)[2:-1])
    message = "Start your bill splitting process <a href='{}'>here</a>".format(url)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message,
                             parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def cancel(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Upload cancelled",
                             parse_mode='HTML')
    return ConversationHandler.END


def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="<b>Welcome to PayMeLah Bot!\n\nThere are 2 simple ways "
                                  "to get me to help you! </b>\n\n<b>/upload : </b>"
                                  "Upload an image of the receipt that you wish to split and let us parse it for you! "
                                  "After which, we will drop you a link to our bill splitting web application to continue"
                                  "the bill splitting process!"
                                  "\n\n<b>/split : </b>"
                                  "Simply tap on the link sent to you and you can begin your bill splitting process!"
                                  "\n\n<b>/cancel : </b>"
                                  "Use this command to cancel any ongoing command!",
                             parse_mode='HTML')


def countdown(update, context, seconds):
    timer = seconds
    sent_message = context.bot.send_message(chat_id=update.effective_chat.id,
                                            text="{}".format(hourglass_emoji * timer),
                                            parse_mode='HTML')
    message_id = sent_message.message_id
    while timer > 1:
        time.sleep(1)
        timer -= 1
        context.bot.edit_message_text("{}".format(hourglass_emoji * timer),
                                      chat_id=update.effective_chat.id
                                      , message_id=message_id)
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
