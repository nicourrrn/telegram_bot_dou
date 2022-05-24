from datetime import datetime, timedelta
import asyncio

import sqlalchemy.orm.query
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import database as db
from parcer import FeedUpdater

# В строку ниже нужно вставить токен
bot_token = "1285311895:AAEW8x29YCw3Ux_5yx6e1wVW4VVbpVvKHg4"
bot = Bot(bot_token)
dp = Dispatcher(bot)
fu = FeedUpdater()

keyboard = ReplyKeyboardMarkup([
    [KeyboardButton("Project Manager"), KeyboardButton("DevOps"), KeyboardButton("QA Engineer")],
    [KeyboardButton("Business Analyst"), KeyboardButton("UI/UX Designer"), KeyboardButton("HR")],
    [KeyboardButton("Software Architect"), KeyboardButton("Developer")]
])


@dp.message_handler(commands=['start'])
async def start(message: Message):
    message_words = message.text.replace("_", " ").split(" ")
    category = ""
    if len(message_words) < 2 and " ".join(message_words[1:]) not in FeedUpdater.categories.keys():
        await message.reply("Please, select your profession",
                            reply_markup=keyboard)
    else:
        await message.answer(f"Hello, {message.from_user.first_name}, from work bot, you added to list")
        await message.answer(f"Please wait vacancies")
        # await message.answer(f"{last_vacancy['title']}\n{last_vacancy['link']}")
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


@dp.message_handler(lambda message: message.text in fu.categories.keys())
async def get_category(message: Message):
    await message.answer("Thanks! Wait new vacancies", reply_markup=ReplyKeyboardRemove())
    # await message.answer(f"{last_vacancy['title']}\n{last_vacancy['link']}")
    with db.Session() as session:
        client = session.get(db.Client, message.from_user.id)
        client.category = message.text
        client.last_vacancy_time = datetime.now()
        session.add(client)
        session.commit()


async def send_vacancies():
    session = db.Session()
    for category in fu.categories.keys():
        print(category)
        last_vacancy = await fu.pop_category(category)
        print(last_vacancy)
        clients: sqlalchemy.orm.Query = session.query(db.Client) \
            .filter_by(category=category)
        clients = clients.all()
        for client in clients:
            await bot.send_message(client.id, f"{last_vacancy['title']}\n{last_vacancy['link']}")
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
    await asyncio.gather(send_vacancies_by_period(15), dp.start_polling())


try:
    executor.start(dp, main())
except KeyboardInterrupt:
    print("Good bye")
except Exception as e:
    print(e)
