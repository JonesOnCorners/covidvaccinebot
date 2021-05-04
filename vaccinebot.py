import requests
import json
import io
from dataclasses import  dataclass
from typing import List
from telegram.ext import *
import datetime
from time import sleep
import logging


logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

@dataclass()
class Appointment:
    center_name: str = None
    fee_type: str = None
    vaccine_name: str = None
    available_capacity: str = None
    date: str = None
    slots: List[str] = None


key = <REACH OUT FOR THIS>

def get_slot(date, pincode):
    list_of_appointements = []
    url = f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={pincode}&date={date}'
    # apnt = Appointment()
    a = requests.request(method="GET",url=url,)
    if a.status_code == 200:
        fix_bytes_value = a.content.replace(b"'", b'"')
        my_json = json.load(io.BytesIO(fix_bytes_value))
        for x in my_json["centers"]:
            for y in x["sessions"]:
                if y["min_age_limit"] == 18 and y['available_capacity'] > 0:
                    appointment = Appointment(center_name=x['name'],
                                              fee_type=x['fee_type'],
                                              vaccine_name=y['vaccine'],
                                              slots = y['slots'],
                                              date = y['date'],
                                              available_capacity = y['available_capacity']
                                              )
                    list_of_appointements.append(appointment)
    # print(list_of_appointements)
    return list_of_appointements


def start_command(update, context):
    update.message.reply_text('Enter the pincode and you can see slots available slots for the next 7 days for 18-44 age bracket')

def help_command(update, context):
    update.message.reply_text('Just ask what you need.')

def handle_image(update, context):
    update.message.reply_text("Image/Photo sharing Not allowed...DELETING")
    update.message.delete()

def handle_video(update, context):
    update.message.reply_text("Video sharing Not allowed...DELETING")
    update.message.delete()

def handle_voice(update, context):
    update.message.reply_text("Voice notes sharing Not allowed...DELETING")
    update.message.delete()


def handle_input(update, context):
    pincode = str(update.message.text).lower()
    if pincode.isdecimal() and len(pincode) == 6:
        date = datetime.datetime.today().strftime("%d-%m-%Y")
        list_of_appointements = get_slot(date, pincode)
        if not list_of_appointements:
            update.message.reply_text(f"No slots currently available for your pincode {pincode}."
                                      f"Will retry in 2 minutes")
            sleep(120)
            handle_input(update, context)
        else:
            for apnt in list_of_appointements:
                msg_text = f"Center:- {apnt.center_name} \n" \
                           f"Fee Type:- {apnt.fee_type}  \n" \
                           f"Vaccine:- {apnt.vaccine_name} \n" \
                           f"Date:- {apnt.date} \n"\
                           f"Date:- {apnt.available_capacity} \n"\
                           f"Slots:-   {' || '.join(apnt.slots)}"
                update.message.reply_text(msg_text)
            update.message.reply_text("Schedule Appointment Now:- " + 'https://www.cowin.gov.in')
    else:
        update.message.reply_text(f"Entered [pincode={pincode}] is either invalid or not numeric")

def main():
    logging.info("Bot starting...")
    updater = Updater(key)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.photo, handle_image))
    dp.add_handler(MessageHandler(Filters.video, handle_video))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))
    dp.add_handler(MessageHandler(Filters.text, handle_input))
    updater.start_polling()

main()
