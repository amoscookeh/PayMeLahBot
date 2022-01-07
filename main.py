from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from bot_functions import start, ask_for_receipt, parse_receipts, split, cancel, help, add_receipts
import os
import logging

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ['TOKEN']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Receipt Parsing Conversation
ADDING, PARSE = range(2)
receipt_parsing = ConversationHandler(
    entry_points=[CommandHandler('upload', ask_for_receipt)],
    states={
        ADDING: [
            MessageHandler(
                Filters.photo, add_receipts
            )
        ],
        PARSE: [
            MessageHandler(
                Filters.text & (~Filters.command), parse_receipts
            )
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    conversation_timeout=300
)


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(receipt_parsing)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('split', split))
    dispatcher.add_handler(CommandHandler('help', help))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://paymelahbot.herokuapp.com/' + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()
