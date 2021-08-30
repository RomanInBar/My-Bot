import logging
import os
import random
import re

import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

load_dotenv()

WEATHER_KEY = os.getenv('weather_api_key')
TELEGRAMM_TOKEN = os.getenv('TELEGRAMM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

logging.basicConfig(
    level=logging.INFO,
    filename='bot.log',
    format='%(asctime)s %(levelname)s:  %(message)s',
)

bot = Bot(token=TELEGRAMM_TOKEN)
updater = Updater(token=TELEGRAMM_TOKEN, use_context=True)
chat_id = CHAT_ID

weather_list = ['погода', 'погоду']


def searh_func(update, context):
    chat = update.effective_chat
    message = (update.message.text).lower()
    asc = message.strip().replace(' ', '%20')
    response = requests.get(
        f'https://searx.roughs.ru/search?q={asc}&format=json&categories=news'
    ).json()
    num_new = random.randint(1, 5)
    first_new = response['results'][num_new]
    text = (
        f'{first_new["title"]}\n{first_new["content"]}\n'
        f'{first_new["img_src"]}\n{first_new["pretty_url"]}'
    )
    logging.info('Ответ "запрос/поиск" сформирован')
    context.bot.send_message(chat_id=chat.id, text=text)
    logging.info('Сообщение "searh_func" отправлено.')


def get_weather(update, context):
    chat = update.effective_chat
    response = requests.get(
        f'http://api.openweathermap.org/data/2.5/'
        f'weather?q=Москва&appid={WEATHER_KEY}&lang=ru'
    ).json()
    weather = response['weather'][0]
    temp = round((response['main']['temp']) - 273.15, 1)
    text = f'{(weather["description"]).capitalize()}.\nТемпература: {temp}'
    logging.info('Ответ "погода" сформирован.')
    context.bot.send_message(chat_id=chat.id, text=text)
    logging.info('Сообщение "get_weather" отправлено.')


def wake_up(update, context):
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id, text='Спасибо что включили меня! :)'
    )
    logging.info('Сообщение "wake_up" отправлено.')


updater.dispatcher.add_handler(CommandHandler('start', wake_up))
updater.dispatcher.add_handler(
    MessageHandler(
        Filters.regex(re.compile(r'погод.', re.IGNORECASE)), get_weather
    )
)
updater.dispatcher.add_handler(MessageHandler(Filters.text, searh_func))


updater.start_polling()
