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
    filename='Bot/bot.log',
    format='%(asctime)s %(levelname)s:  %(message)s',
)

bot = Bot(token=TELEGRAMM_TOKEN)
updater = Updater(token=TELEGRAMM_TOKEN, use_context=True)
chat_id = CHAT_ID


def get_news(update, context):
    first_new = get_content(update, category='news')
    text = (
        f'{first_new["title"]}\n{first_new["content"]}\n'
        f'{first_new["img_src"]}\n{first_new["pretty_url"]}'
    )
    push_message(update, context, text, func_name='get_news')


def get_images(update, context):
    first_new = get_content(update, category='images')
    text = f'{first_new["img_src"]}'
    push_message(update, context, text, func_name='get_images')


def get_videos(update, context):
    first_new = get_content(update, category='videos')
    text = f'{first_new["url"]}'
    push_message(update, context, text, func_name='get_videos')


def get_content(update, category):
    message = (update.message.text).lower().strip().replace(' ', '%20')
    response = requests.get(
        f'https://searx.roughs.ru/search?q={message}&'
        f'format=json&categories={category}'
    ).json()
    first_new = response['results'][random.randint(1, 5)]
    return first_new


def get_weather(update, context):
    response = requests.get(
        f'http://api.openweathermap.org/data/2.5/'
        f'weather?q=Москва&appid={WEATHER_KEY}&lang=ru'
    ).json()
    weather = response['weather'][0]
    temp = round((response['main']['temp']) - 273.15, 1)
    text = f'{(weather["description"]).capitalize()}.\nТемпература: {temp}'
    push_message(update, context, text, func_name='get_weather')


def wake_up(update, context):
    text = 'Спасибо что включили меня! :)'
    push_message(update, context, text, func_name='wake_up')


def push_message(update, context, text, func_name):
    logging.info(f'Ответ "{func_name}" сформирован')
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    logging.info(f'Сообщение "{func_name}" отправлено.')


updater.dispatcher.add_handler(CommandHandler('start', wake_up))
updater.dispatcher.add_handler(
    MessageHandler(
        Filters.regex(re.compile(r'погод.', re.IGNORECASE)), get_weather
    )
)
updater.dispatcher.add_handler(
    MessageHandler(
        Filters.regex(
            re.compile(r'фот\w+ {1,5}|картин\w+ {1,5}', re.IGNORECASE)
        ),
        get_images,
    )
)
updater.dispatcher.add_handler(
    MessageHandler(
        Filters.regex(re.compile(r'видео', re.IGNORECASE)), get_videos
    )
)
updater.dispatcher.add_handler(MessageHandler(Filters.text, get_news))


updater.start_polling()
