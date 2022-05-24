from parcer import FeedUpdater
bot_username = input("Введите ник бота: ").replace("@", "").replace(" ", "")

url_base = f"https://t.me/{bot_username}?start="
for name in FeedUpdater.categories.keys():
    print(url_base+name.replace(" ", "_"))
