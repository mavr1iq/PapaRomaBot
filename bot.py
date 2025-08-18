import handlers
import schedule

from config import *
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Прівєт. Цей бот створений як колектор для забирання грошей на спотіфай преміум')


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
    if update:
        if update.message:
            if update.message.chat.type == 'private':
                await context.bot.send_message(update.message.chat.id, 'ти єблан')


print('Bot started')


def main():
    app = Application.builder().token(API_TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT, handlers.handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handlers.handle_voice))
    app.add_handler(MessageHandler(filters.VIDEO_NOTE, handlers.handle_voice))
    app.add_error_handler(error)
    job_queue = app.job_queue

    schedule.queue(job_queue)

    print('Polling')

    app.run_polling(poll_interval=3)


if __name__ == '__main__':
    main()
