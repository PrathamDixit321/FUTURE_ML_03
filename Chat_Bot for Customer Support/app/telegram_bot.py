import os
import logging
from dotenv import load_dotenv

load_dotenv()

from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

from app.chatbot import Chatbot

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
FAQ_CSV = os.getenv('FAQ_CSV', 'data/sample_faqs.csv')

logging.basicConfig(level=logging.INFO)


def start_bot():
    if not TELEGRAM_TOKEN:
        logging.error('TELEGRAM_TOKEN not set')
        return
    bot = Chatbot(FAQ_CSV)
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    def handle_message(update, context):
        user_text = update.message.text
        resp = bot.get_response(user_text)
        update.message.reply_text(resp['answer'])

    def start(update, context):
        update.message.reply_text("Hi! How can I help you today?")

    def ticket_cmd(update, context):
        text = ' '.join(context.args) if context.args else None
        if not text:
            update.message.reply_text("Usage: /ticket <describe your issue>")
            return
        ticket = bot.create_ticket(text, contact=str(update.message.from_user.id))
        update.message.reply_text(f"Ticket created: {ticket['id']}. Our team will follow up.")

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('ticket', ticket_cmd))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    logging.info('Starting Telegram bot polling...')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start_bot()
