from uuid import uuid4

from telegram.ext import ConversationHandler
from telegram import ParseMode, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton
from tabscanner_functions import callProcess, callResult
from helper_functions import format_line_items
from db_functions import *
import os
import time
import json
import base64

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

    if not user_exists(update.message.effective_user.username):
        print("Creating new user")
        create_new_user_record(update.message.effective_user.username)


ADDING, PARSE = range(2)


def ask_for_receipt(update, context):
    user_data = context.user_data
    if "receipts" in user_data:
        receipts = context.user_data["receipts"]
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please send me a clear image of the next {} Receipt {}".format(receipt_emoji,
                                                                                                  receipt_emoji))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Please send me a clear image of your {} Receipt {}".format(receipt_emoji,
                                                                                                  receipt_emoji))
        context.user_data["receipts"] = []
    return ADDING


def add_receipts(update, context):
    receipt_photo = update.message.photo[-1]
    file_id = receipt_photo.file_id

    photos = context.user_data["receipts"]
    photos.append(file_id)
    context.user_data["receipts"] = photos

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Do you wish to upload another receipt?",
                             reply_markup=add_suggested_actions(update, context))


def parse_receipts(update, context):
    photos = context.user_data["receipts"]
    output_tokens = []
    compiled_line_items = []
    username = update.effective_user.username

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="The {}Robots{} have begun parsing your receipt...".format(robot_emoji, robot_emoji),
                             parse_mode='HTML')
    for file_id in photos:
        photo = context.bot.get_file(file_id)
        photo.download("{}.jpg".format(file_id))
        output = callProcess(TABSCANNER_TOKEN, "{}.jpg".format(file_id))
        status = output['status']
        output_token = output['token']
        output_tokens.append(output_token)

        if user_exists(username):
            print("Updating user activity")
            update_total_activity()
            update_user_activity(username)
        else:
            print("Creating new user")
            create_new_user_record(username)
            update_total_activity()
            update_user_activity(username)

        if status != 'success':
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Image parsing failed {}".format(sad_shocked_emoji),
                                     parse_mode='HTML')

    countdown(update, context, 7)

    for output_token in output_tokens:
        result = callResult(TABSCANNER_TOKEN, output_token)
        while result['status'] == 'pending':
            time.sleep(2)
            result = callResult(TABSCANNER_TOKEN, output_token)
        if result['status'] == 'failed':
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Image parsing failed {}".format(sad_shocked_emoji),
                                     parse_mode='HTML')
            return ConversationHandler.END
        else:
            line_items = format_line_items(result)
            if len(line_items) < 1:
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Image parsing failed {}... Try sending a clearer image or use /split to "
                                              "start splitting anyway".format(sad_shocked_emoji),
                                         parse_mode='HTML')
                return ConversationHandler.END
            compiled_line_items.extend(line_items)

    data = {
        'lineItems': compiled_line_items,
        'chatId': update.effective_chat.id,
        'users': [update.effective_user.username]
    }

    if user_exists(username):
        print("Adding Receipt Data")
        add_receipt_data(update.effective_user.username, data['lineItems'])

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
                                  "After which, we will drop you a link to our bill splitting web application to continue "
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


def add_suggested_actions(update, context):
    options = []

    options.append(InlineKeyboardButton('Yes', callback_data='y'))
    options.append(InlineKeyboardButton('No', callback_data='n'))

    reply_markup = InlineKeyboardMarkup([options])
    return reply_markup


def manage_query(update, context):
    query = update.callback_query
    query.answer()

    context.bot.edit_message_reply_markup(chat_id=update.effective_chat.id,
                                          message_id=query.message.message_id,
                                          reply_markup=InlineKeyboardMarkup([]))

    if query.data == 'y':
        ask_for_receipt(update, context)
    else:
        parse_receipts(update, context)


def msg_amos(context):
    print("Fetching global data")
    data = get_total_activity()
    message = "Total Activity: " + str(data["total_usage"]) + "\nUnique Users: " + str(data["unique_users"])

    sent_message = context.bot.send_message(chat_id="26206762", text=message)

    # context.bot.delete_message(
    #     chat_id="26206762",
    #     message_id=sent_message.message_id
    # )