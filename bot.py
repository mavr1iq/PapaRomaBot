import time

import handlers
import schedule

from config import *
from telegram import Update
from telegram.constants import ReactionEmoji
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    await update.message.reply_text('Прівєт. Цей бот створений як колектор для забирання грошей на спотіфай преміум')
    await update.message.reply_text('Привіт. Це тест для лабораторної')

async def like_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        print(
            f"[ {update.message.date.strftime('%Y-%m-%d %H:%M:%S')} ] Sending like reaction to message {update.message.reply_to_message.text} ")
        await update.message.reply_to_message.set_reaction(ReactionEmoji.RED_HEART)
        time.sleep(1)
        await update.message.delete()
    else:
        print(
            f"[ {update.message.date.strftime('%Y-%m-%d %H:%M:%S')} ] Sending like reaction to message {update.message.text} ")
        await update.message.set_reaction(ReactionEmoji.RED_HEART)

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        print(
            f"[ {update.message.date.strftime('%Y-%m-%d %H:%M:%S')} ] Sending message to admin(Matvili Popa) {update.message.reply_to_message.text} ")
        await context.bot.send_message(chat_id=857879424, text=update.message.reply_to_message.text)

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
    app.add_handler(CommandHandler('like', like_command))
    app.add_handler(CommandHandler('report', report_command))
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
