from datetime import datetime, timedelta
import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message

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


@dp.message_handler(commands=['start'])
async def start(message: Message):
    profession = message.text.replace("_", " ").split(" ")
    if len(profession) < 2:
        await message.reply("Incorrect link, please, input command /start [YOUR_PROFESSION]")
        return
    if " ".join(profession[1:]) not in categories.keys():
        await message.reply(f"Profession {' '.join(profession[1:])} not found")
        return
    await message.answer(f"Hello, {message.from_user.first_name}, from work bot, you added to list")

    new_client = db.Client(id=message.from_user.id,
                           category=" ".join(profession[1:]),
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
