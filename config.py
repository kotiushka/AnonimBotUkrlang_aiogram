from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from aiogram import types


TOKEN = 'YOUR TOKEN'

def start():
    b1 = KeyboardButton('⭐️ Пошук співрозмовника')
    b2 = KeyboardButton('❤️ Пошук по гендеру')
    b3 = KeyboardButton('🌸 Пошук по віку')
    b4 = KeyboardButton('🛠 Профіль')
    b5 = KeyboardButton('🌃 Пошук по місту')
    b1_start = ReplyKeyboardMarkup(resize_keyboard=True)
    b1_start.add(b1).add(b2).insert(b3).add(b4).insert(b5)
    return b1_start


def params():
    b1 = KeyboardButton('Пол 👨')
    b2 = KeyboardButton('Возраст 👩')
    b3 = KeyboardButton('Місто 📝')
    b5 = KeyboardButton('Повернутись 🔚')
    param = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    param.insert(b1).insert(b2).insert(b3).insert(b5)
    return param

def gen():
    b1 = KeyboardButton('Дівчата 🙍‍♀️')
    b2 = KeyboardButton('Хлопці 🙎‍♂️')
    b3 = KeyboardButton('Випадковий гендер ❔')
    b4 = KeyboardButton('Повернутись 🔚')
    param = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    param.insert(b1).insert(b2).insert(b3).insert(b4)
    return param

def buttonscountry():
    b1 = KeyboardButton('Изменить страну 🌐')
    b2 = KeyboardButton('Випадкове місто ❔')
    b3 = KeyboardButton('Повернутись 🔚')
    param = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    param.insert(b1).insert(b2).insert(b3)
    return param

def gender():
    buttons = [
        InlineKeyboardButton(text="🙋‍♂️Чоловіча", callback_data="man"),
        InlineKeyboardButton(text="🙋‍♀️Жіноча", callback_data="woman")
    ]
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(*buttons)
    return keyboard


def buttonsmain():
    b1 = KeyboardButton('⭐️ Пошук співрозмовника')
    b2 = KeyboardButton('❤️ Поиск по полу')
    b3 = KeyboardButton('😈 Пошлый чат')
    b4 = KeyboardButton('🛠 Профіль')
    b5 = KeyboardButton('🏆 VIP доступ')
    b1_start = ReplyKeyboardMarkup(resize_keyboard=True)
    b1_start.add(b1).add(b2).insert(b3).add(b4).insert(b5)
    return b1_start

def age_search():
    b1 = KeyboardButton('Змінити вік🙍‍♀️')
    b2 = KeyboardButton('Випадковий вік ❔')
    b3 = KeyboardButton('Повернутись 🔚')
    param = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    param.insert(b1).insert(b2).insert(b3)
    return param

def change():
    buttons = [
        InlineKeyboardButton(text="⚙️ Редагувати", callback_data="change")
    ]
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(*buttons)
    return keyboard


def buttoncancel():
    b1 = KeyboardButton('❌ Зупинити пошук')
    b1_start = ReplyKeyboardMarkup(resize_keyboard=True)
    b1_start.add(b1)
    return b1_start


def STOP():
    b1 = KeyboardButton('/stop')
    b1_start = ReplyKeyboardMarkup(resize_keyboard=True)
    b1_start.add(b1)
    return b1_start

def vip_city():
    b1 = KeyboardButton('Змінити місто 🌆')
    b2 = KeyboardButton("Випадкове місто ❔")
    b3 = KeyboardButton('Повернутись 🔚')
    vip_city = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    vip_city.insert(b1).insert(b2).insert(b3)
    return vip_city


def back_to_chat_markups():
    buttons = [
        InlineKeyboardButton(text="Принять ✅", callback_data="agree"),
        InlineKeyboardButton(text="Отказать ❌", callback_data="disagree")
    ]
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(*buttons)
    return keyboard

def send1():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = ['Изменить рассылку 1', 'Разослать рассылку 1', 'Просмотр рассылки 1','/admin (назад)' ]
    keyboard.add(*buttons)
    return keyboard

def send2():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = ['Изменить рассылку 2', 'Разослать рассылку 2', 'Просмотр рассылки 2','/admin (назад)' ]
    keyboard.add(*buttons)
    return keyboard

def send3():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    buttons = ['Изменить рассылку 3', 'Разослать рассылку 3', 'Просмотр рассылки 3','/admin (назад)' ]
    keyboard.add(*buttons)
    return keyboard

def ADMIN_MENU():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = ["👨‍💼 Добавить/изменить/удалить админа", "📝 Добавить/изменить/удалить рекламный канал", "📈 Статистика",'Выгрузка таблицы 💾','Настройки рассылки','/start (главное меню)']
    keyboard.add(*buttons)
    return keyboard

def sends():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = ['Рассылка 1','Рассылка 2','Рассылка 3','Как добавлять рассылку']
    keyboard.add(*buttons)
    return keyboard


def but(x):
    x = x.split('#')
    c, q, d = 0, 0, 1
    urlb = InlineKeyboardMarkup(row_width=1)
    try:
        buttons = (len(x) - 1) / 2
        while c != buttons:
            buttons = InlineKeyboardButton(text=x[q + 1], url=x[d + 1].strip())
            urlb.add(buttons)
            q += 2
            d += 2
            c += 2
        return urlb
    except:
        return urlb
AGE = []

FLAG = True




countryes = ['Київ',
             'Харків',
             'Одеса',
             'Дніпро',
             'Донецьк',
             'Запоріжжя',
             'Львів',
             'Кривий Ріг',
             'Миколаїв',
             'Севастополь',
             'Маріуполь',
             'Луганськ',
             'Вінниця',
             'Сімферополь',
             'Херсон',
             'Хмельницький',
             'Полтава',
             'Черкаси',
             'Суми',
             'Чернівці'
             ]
