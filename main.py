from datetime import datetime, timedelta
import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import database as db
import parcer

# В строку ниже нужно вставить токен
bot_token = ""
bot = Bot(bot_token)
dp = Dispatcher(bot)

categories = {
    "Project Manager": ("Project+Manager", ""),
    "Software Architect": ("Architect", ""),
    "UI/UX Designer": ("Design", "UX+UI"),
    "QA Engineer": ("QA", ""),
    "HR": ("HR", ""),
    "DevOps": ("DevOps", ""),
    "Business Analyst": ("", "Business+Analyst"),
    "Developer": ("", "Developer")
}

keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("Project Manager"), KeyboardButton("DevOps"), KeyboardButton("QA Engineer")],
    [KeyboardButton("Business Analyst"), KeyboardButton("UI/UX Designer"), KeyboardButton("HR")],
    [KeyboardButton("Software Architect"), KeyboardButton("Developer")]
])


@dp.message_handler(commands=['start'])
async def start(message: Message):
    message_words = message.text.replace("_", " ").split(" ")
    category = ""
    if len(message_words) < 2 and " ".join(message_words[1:]) not in categories.keys():
        await message.reply("Please, select your profession",
                            reply_markup=keyboard)
    else:
        await message.answer(f"Hello, {message.from_user.first_name}, from work bot, you added to list")
        last_vacancy = (await parcer.get_feeds(*categories[" ".join(message_words[1:])]))[0]
        await message.answer(f"{last_vacancy['title']}\n{last_vacancy['link']}")
    new_client = db.Client(id=message.from_user.id,
                           category=category,
                           name=message.from_user.first_name,
                           last_vacancy_time=datetime.now() - timedelta(days=1))
    with db.Session() as session:
        if user := session.get(db.Client, message.from_user.id):
            user.category = new_client.category
            session.add(user)
        else:
            session.add(new_client)
        session.commit()


@dp.message_handler(commands=['stop'])
async def stop(message: Message):
    with db.Session() as session:
        session.delete(session.get(db.Client, message.from_user.id))
        session.commit()
        await message.answer("Bye!")


@dp.message_handler(lambda message: message.text in categories.keys())
async def get_category(message: Message):
    await message.answer("Thanks!", reply_markup=ReplyKeyboardRemove())
    last_vacancy = (await parcer.get_feeds(*categories[message.text]))[0]
    await message.answer(f"{last_vacancy['title']}\n{last_vacancy['link']}")
    with db.Session() as session:
        client = session.get(db.Client, message.from_user.id)
        client.category = message.text
        client.last_vacancy_time = datetime.now()
        session.add(client)
        session.commit()

async def send_vacancies():
    session = db.Session()
    for category, params in categories.items():
        last_vacancy = (await parcer.get_feeds(*params))[0]
        clients = session.query(db.Client) \
            .filter(db.Client.category == category,
                    db.Client.last_vacancy_time < last_vacancy.published_parsed)
        for client in clients:
            await bot.send_message(client.id, f"{last_vacancy['title']}\n{last_vacancy['link']}")
            client.last_vacancy_time = datetime.now()
            session.add(client)
    session.commit()
    session.close()


async def send_vacancies_by_period(period=60):
    while True:
        try:
            await send_vacancies()
        except Exception as e:
            print(e)
        await asyncio.sleep(period)


async def main():
    await asyncio.gather(dp.start_polling(), send_vacancies_by_period(10))

try:
    executor.start(dp, main())
except KeyboardInterrupt:
    print("Good bye")
