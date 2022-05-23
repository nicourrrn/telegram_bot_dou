## Запуск
### 1 вариант - poetry
1. Установить [Poetry](https://python-poetry.org/docs/)
2. `poetry shell`
3. `poetry install`
4. `python main.py`
### 2 вариант - стандартный
1. `pip install -r requirements.txt`
2. `python main.py`

## Настройка
Для использования бота нужно в [BotFather](https://t.me/BotFather)
и скопировать ApiToken и вставить в main.py (я там обозначит поле, куда надо)
[Статейка на Medium](https://medium.com/shibinco/create-a-telegram-bot-using-botfather-and-get-the-api-token-900ba00e0f39)

В такой же строчке ниже можно настроить паузу между обновлениями вакансий (`send_vacancies...`) в секундах.
В данном случае задержка - 10 секунд
    await asyncio.gather(dp.start_polling(), send_vacancies_by_period(10))

## Генерация ссылок
Для генерации ссылок следует использовать url_generator
`python url_generator.py`