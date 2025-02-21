import webuntis
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext, JobQueue
from time import sleep
import threading
import asyncio
import json
import os
from urllib.parse import quote
import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

#variables:
school_name = 
my_secret =  #telegram bot token
username = 
password = 
server =  #basically the domain of webuntis for most schools
chat_id =  #chat id to the telegram channel the bot should send the messages in
substText =  #every school seems to handle cancelled lessons differently. this was made to check subst text and if it matches the given one, the lesson will be considered as cancelled
pKlasse =  #the class you're currently attending

#encode school name to get 
encoded_school_name = quote(school_name)
first_try = True

async def send_update_message(context: CallbackContext):
    global first_try
    if(datetime.datetime.utcnow().hour == 6):
        if first_try == True:
            with webuntis.Session(
                username=username,
                password=password,
                server=server,
                school=encoded_school_name,
                useragent='WebUntis Test'
            ).login() as s:
                today = datetime.date.today()
                klasse = s.klassen().filter(name=pKlasse)[0]
                table = s.timetable_extended(klasse=klasse, start=today, end=today).to_table()
                bot_text = ""
                cancelled = False
                for time, row in table:
                    for date, cell in row:
                        for period in cell:
                            if period.substText == substText:
                                bot_text += (', '.join(su.long_name for su in period.subjects) + "   " + str(period.original_teachers[0]))
                                #print(period.substText)
                                bot_text += ("\nStartzeit: " + str(period.start).split()[-1] + "\nEndzeit: " + str(period.end).split()[-1] + "\n\n")
                                cancelled = True

                if cancelled == True:
                    cancelled = False
                    while first_try == True:
                        try:
                            await context.bot.send_message(chat_id=chat_id, text=bot_text)
                            first_try = False
                        except:
                            sleep(10)
                            pass
                    s.logout()
                else:
                    s.logout()
                    first_try = False

    else:
        first_try = True

if __name__ == '__main__':
    application = ApplicationBuilder().token(my_secret).build()

    # Start the send_update_message function in a new thread
    threading.Thread(target=asyncio.run, args=(send_update_message(application),)).start()

    application.run_polling()

