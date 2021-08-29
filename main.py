from telegram import Bot
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
import logging
import requests
import os
import random

from dotenv import load_dotenv

load_dotenv()

WEATHER_KEY = os.getenv('weather_api_key')
TELEGRAMM_TOKEN = os.getenv('TELEGRAMM_TOKEN')

logging.basicConfig(
    level=logging.INFO,
    filename='bot.log',
    format='%(asctime)s %(levelname)s:  %(message)s'
)

bot = Bot(token=TELEGRAMM_TOKEN)
updater = Updater(token=TELEGRAMM_TOKEN, use_context=True)
chat_id = 878886959

weather_list = ['погода', 'погоду']


def searh_func(message):
    asc = message[0]
    logging.info(asc)
    response = requests.get(f'https://searx.roughs.ru/search?q={asc}&format=json&categories=news').json()
    num_new = random.randint(1, 5)
    first_new = response['results'][num_new]
    logging.info(response['results'][0])
    return f'{first_new["title"]}\n{first_new["content"]}\n{first_new["img_src"]}\n{first_new["pretty_url"]}'


def get_weather():
    response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q=Москва&appid={WEATHER_KEY}&lang=ru').json()
    weather = response['weather'][0]
    temp = round((response['main']['temp']) - 273.15, 1)
    logging.info('Ответ "погода" сформирован')
    return f'{weather["description"]}.\nТемпература: {temp}'
    

def say_hi(update, context):
    chat = update.effective_chat
    message = (update.message.text).lower().split()
    if [x for x in weather_list if x in message]:
        text = get_weather()
    else:
        text = searh_func(message)
    context.bot.send_message(chat_id=chat.id, text=text)
    logging.info('Сообщение отправлено.')

def wake_up(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text='Спасибо что включили меня! :)')

updater.dispatcher.add_handler(CommandHandler('start', wake_up))
updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))

updater.start_polling()
