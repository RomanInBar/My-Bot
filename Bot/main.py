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
    filename='My-Bot/Bot/bot.log',
    format='%(asctime)s %(levelname)s:  %(message)s',
)

bot = Bot(token=TELEGRAMM_TOKEN)
updater = Updater(token=TELEGRAMM_TOKEN, use_context=True)
chat_id = CHAT_ID

weather_list = ['погода', 'погоду']


def get_news(update, context):
    first_new = get_content(update, category='news')
    text =  (
        f'{first_new["title"]}\n{first_new["content"]}\n'
        f'{first_new["img_src"]}\n{first_new["pretty_url"]}'
    )
    logging.info('Ответ "get_news" сформирован')
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    logging.info('Сообщение "get_news" отправлено.')


def get_images(update, context):
    first_new = get_content(update, category='images')
    text = f'{first_new["img_src"]}'
    logging.info('Ответ "get_images" сформирован')
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    logging.info('Сообщение "get_images" отправлено.')

def get_videos(update, context):
    first_new = get_content(update, category='videos')
    text = f'{first_new["url"]}'
    logging.info('Ответ "get_videos" сформирован')
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    logging.info('Сообщение "get_videos" отправлено.')

def get_content(update, category):
    message = (update.message.text).lower().strip().replace(' ', '%20')
    response = requests.get(
        f'https://searx.roughs.ru/search?q={message}&'
        f'format=json&categories={category}'
    ).json()
    first_new = response['results'][random.randint(1, 5)]
    return first_new

def get_weather(update, context):
    chat = update.effective_chat
    response = requests.get(
        f'http://api.openweathermap.org/data/2.5/'
        f'weather?q=Москва&appid={WEATHER_KEY}&lang=ru'
    ).json()
    weather = response['weather'][0]
    temp = round((response['main']['temp']) - 273.15, 1)
    text = f'{(weather["description"]).capitalize()}.\nТемпература: {temp}'
    logging.info('Ответ "get_weather" сформирован.')
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
updater.dispatcher.add_handler(
    MessageHandler(
        Filters.regex(re.compile(r'фот\w+|картин\w+', re.IGNORECASE)), get_images
    )
)
updater.dispatcher.add_handler(
    MessageHandler(
        Filters.regex(re.compile(r'видео', re.IGNORECASE)), get_videos
    )
)
updater.dispatcher.add_handler(MessageHandler(Filters.text, get_news))


updater.start_polling()
