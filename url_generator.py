bot_username = input("Введите ник бота: ").replace("@", "").replace(" ", "")
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
url_base = f"https://t.me/{bot_username}?start="
for name in categories.keys():
    print(url_base+name.replace(" ", "_"))
