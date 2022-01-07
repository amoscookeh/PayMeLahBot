from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, InlineQueryHandler, \
    CallbackQueryHandler, DictPersistence
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
import os
import logging

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ['TOKEN']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


# First time starting the bot
def start(update, context):
    # format_user_data(update, context)
    print("Here")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to PayMeLah Bot! U+2728",
                             parse_mode='HTML')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Start the bill splitting process with one of the following commands: "
                                  + "\n\n/upload - Upload an image to be parsed"
                                  + "\n/split - Begin bill splitting without receipt parsing")
    # return USERNAME


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # dispatcher.add_handler(registration_handler)
    # dispatcher.add_handler(conv_handler)
    # dispatcher.add_handler(InlineQueryHandler(inlinequery))
    # dispatcher.add_handler(CallbackQueryHandler(callbackhandle))
    # dispatcher.add_handler(CommandHandler('help', help))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://paymelahbot.herokuapp.com/' + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
