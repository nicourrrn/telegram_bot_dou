import datetime

import asyncio

import yaml
import sqlalchemy.orm.query
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message
import database as db
import parcer

with open("config.yml", 'r') as file:
    config = yaml.safe_load(file)

bot_token = config["bot_token"]
admin_ids = config["admin_ids"]
bot = AsyncTeleBot(bot_token)

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


@bot.message_handler(commands=['start'])
async def start(message: Message):
    profession = message.text.replace("_", " ").split(" ")
    if len(profession) < 2:
        await bot.reply_to(message, "Incorrect link, please, input command /start [YOUR_PROFESSION]")
        return
    if " ".join(profession[1:]) not in categories.keys():
        await bot.reply_to(message, f"Profession {' '.join(profession[1:])} not found")
        return
    await bot.reply_to(message, f"Hello, {message.from_user.first_name}, from work bot, you added to list")
    new_client = db.Client(id=message.from_user.id,
                           category=" ".join(profession[1:]),
                           name=message.from_user.first_name,
                           last_vacancy_time=datetime.datetime.now())
    with db.Session() as session:
        if user := session.get(db.Client, message.from_user.id):
            user.category = new_client.category
            session.add(user)
        else:
            session.add(new_client)
        session.commit()


@bot.message_handler(commands=['stop'])
async def stop(message: Message):
    with db.Session() as session:
        session.delete(session.get(db.Client, message.from_user.id))
        session.commit()


async def send_vacancies():
    while True:
        await asyncio.sleep(10)
        session = db.Session()
        for category, params in categories.items():
            last_vacancy = (await parcer.get_feeds(*params))[0]
            clients: sqlalchemy.orm.query.Query = session.query(db.Client) \
                .filter(db.Client.category == category)
                        # db.Client.last_vacancy_time < last_vacancy.published_parsed)
            for client in clients:
                await bot.send_message(client.id, last_vacancy["title"])
                client.last_vacancy_time = datetime.datetime.now()
                session.add(client)
        session.commit()
        session.close()
        await asyncio.sleep(50)


async def main():
    tasks = [bot.polling(), send_vacancies()]
    await asyncio.gather(*tasks)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Good bye")
