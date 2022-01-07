from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, InlineQueryHandler, \
    CallbackQueryHandler, DictPersistence
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from functions import start, ask_for_receipt, parse_receipt, cancel
import os
import logging

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ['TOKEN']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


# Receipt Parsing Conversation
PARSE = range(1)
receipt_parsing = ConversationHandler(
    entry_points=[CommandHandler('upload', ask_for_receipt)],
    states={
        PARSE: [
            MessageHandler(
                Filters.document.mime_type("image/jpeg"), parse_receipt
            )
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    conversation_timeout=300
)


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # dispatcher.add_handler(registration_handler)
    dispatcher.add_handler(receipt_parsing)
    # dispatcher.add_handler(InlineQueryHandler(inlinequery))
    # dispatcher.add_handler(CallbackQueryHandler(callbackhandle))
    # dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('start', start))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://paymelahbot.herokuapp.com/' + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
