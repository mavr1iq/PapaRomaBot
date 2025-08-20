import pytz
import csv
import handlers

from datetime import datetime, date
from telegram.ext import ContextTypes

scheduled = ''
users = []
global job_queued

#Schedule
def get_csvs():
    global scheduled
    with open('csv/schedule.csv', newline='') as csvfile:
        text = csv.reader(csvfile)
        for row in text:
            if row[0] != 'date':
                scheduled = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                scheduled = scheduled.replace(tzinfo=pytz.timezone('Etc/GMT-3'))
# Users

    with open('csv/users.csv', newline='') as csvfile:
        text = csv.reader(csvfile)
        for row in text:
            users.append(row)
        users.pop(0)


async def callback_month(context: ContextTypes.DEFAULT_TYPE):
    with open('csv/schedule.csv', 'w', newline='') as csvfile:
        fieldnames = ['date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'date':f'{(datetime(date.today().year, date.today().month+1, date.today().day, 9, 0, 10)).strftime("%Y-%m-%d %H:%M:%S")}'})
    chat_id = '-1002427995110'

    await context.bot.send_message(chat_id=chat_id, text=await handlers.handle_response('@all', chat_id, True))
    queue(job_queued)


# Queue
def queue(job_queue):
    global job_queued
    job_queued = job_queue
    get_csvs()
    print(scheduled)
    job_queue.run_once(callback_month, when=scheduled)