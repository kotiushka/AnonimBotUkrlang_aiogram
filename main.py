import logging, config
import aiogram.utils.exceptions
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
from aiogram.dispatcher.filters.state import StatesGroup,State
from aiogram.dispatcher import FSMContext
from DB import Database
from aiogram.utils.callback_data import CallbackData
import pandas
from time import sleep
import requests

#-------------------------------------

class Register(StatesGroup):
    city = State()
    country = State()
    old = State()

class Add_channel(StatesGroup):
    channel_name = State()

class Change_channel(StatesGroup):
    channel_name = State()

class Add_admin(StatesGroup):
    username_admin = State()

class Change_admin(StatesGroup):
    username_admin = State()

class VIP_age(StatesGroup):
    age1 = State()
    age2 = State()

class Send(StatesGroup):
    send1 = State()
    send1_photo = State()

class Send2(StatesGroup):
    send2 = State()
    send2_photo = State()

class Send3(StatesGroup):
    send3 = State()
    send3_photo = State()



#-------------------------------------

# --------------- Связь с БД, ботом start
db = Database('anonims.db')
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
connection = sqlite3.connect('anonims.db')
cursor = connection.cursor()



cb_change_channel = CallbackData("channel", "channelname")
cb_delete_channel = CallbackData("channel2", "channelname2")
cb_country = CallbackData('country','countryname')
cb_change_admin = CallbackData("ch_admin", "ch_username")
cb_delete_admin = CallbackData("del_admin", "del_username")
vip_cb_country = CallbackData('vip_country','vip_countryname')


# --------------- Связь с БД, ботом end


# --------------- Проверки start

def keyboard_sub():
    i = 1
    buttons = []
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)
    check = types.InlineKeyboardButton(text="Подтвердить✅", callback_data="check_sub")
    for line in get_channel():
        buttons = types.InlineKeyboardButton(text=f"Канал #{i}", url=f"tg://resolve?domain={line[0]}")
        keyboard.add(buttons)
        i+=1
    keyboard.add(check)
    return keyboard

def check_status(chat_member):
    if chat_member["status"] != 'left':
        return True
    else:
        return False


def check_reports(mess):
    reportss = cursor.execute("SELECT `reports` FROM `users` WHERE `id` = ?",(mess,)).fetchmany(1)
    if int(reportss[0][0]) >= 7:
        return False
    return True


def check_admin(id):
    row_admins = cursor.execute(f"SELECT username FROM admins")
    admins = row_admins.fetchall()
    for admin in admins:
        if (admin[0]==id):
            return True
    return False

def get_channel():
    cursor.execute("SELECT channel_name FROM channel")
    res = cursor.fetchall()
    return res

def check_vip(mess):
    vip_status = cursor.execute('SELECT `VIP` FROM `users` WHERE id = ?',(mess,)).fetchone()
    if vip_status[0] == 'Нет':
        return False
    return True

#------------------- Проверки end


@dp.message_handler(commands="start")
async def start(message: types.Message):
    info = cursor.execute('SELECT id FROM users WHERE id=?', (message.chat.id,))
    if info.fetchone() is None:
        cursor.execute("INSERT INTO users(id,VIP,gender_search,age_search,country_search,city_search,reports) VALUES (?,?,?,?,?,?,?)", (message.chat.id,'Нет','Случайный','Случайный','Случайный','Случайный',0,))
        connection.commit()
        await bot.send_message(message.chat.id, f'Привіт, {message.from_user.username}! Пройди невеличку реєстрацію щоб продовжити♥️🇺🇦')
        await bot.send_message(message.chat.id, 'Обери свою стать', reply_markup=config.gender(), )
    else:
        await bot.send_message(message.chat.id,'<b>Меню</b>',parse_mode='html',reply_markup=config.start())


@dp.message_handler(commands=["stop"])
async def stop(message: types.Message):
    chat_info = db.get_active_chat(message.chat.id)
    if chat_info != False:
        db.delete_chat(chat_info[0])
        await bot.send_message(chat_info[1],'<b>💬 Співрозмовник залишив(а) чат</b>\n\n/next - знайти наступного\n/back - повернути співрозмовника\n/report - поскаржитися на спам\n',reply_markup=config.start(),parse_mode='html')
        await bot.send_message(message.chat.id,'<b>💬 Ви закінчили діалог з вашим співрозмовником</b>\n\n/next - знайти наступного\n/back - повернути співрозмовника\n/report - поскаржитися на спам',reply_markup=config.start(),parse_mode='html')
    else:
        await bot.send_message(message.chat.id,'Вы не почали чат!',reply_markup=config.start())

@dp.message_handler(text=["🛠 Профіль",'/profile'])
async def admin_menu(message: types.Message):
    v = ''
    city = cursor.execute('SELECT city FROM users WHERE id=?', (message.chat.id,))
    city = city.fetchone()
    all = cursor.execute('SELECT age,city,gender,country,VIP FROM users WHERE id=?', (message.chat.id,))
    all = all.fetchall()
    if all[0][4] == 'Нет':
        v = 'Ні'
    elif all[0][4] == 'Да':
        v = 'Так'
    await bot.send_message(message.chat.id,f'🎭Мій профіль\n\n<b>Стать:</b> {all[0][2]}\n<b>Вік:</b> {all[0][0]}\n<b>Місто:</b> {all[0][1]}\n\n<b>VIP:</b> {v}\n\n',reply_markup=config.change(),parse_mode='html')


@dp.message_handler(commands=['admin'])
async def admin_menu(message: types.Message):
    if(check_admin(message.from_user.username)):
        row_admins = cursor.execute(f"SELECT username FROM admins")
        admins = row_admins.fetchall()
        await message.answer(f"<b>Адмін меню</b>", reply_markup=config.ADMIN_MENU(), parse_mode='html')


@dp.message_handler(commands=['add_admin'])
async def admin_menu(message: types.Message):
    if(check_admin(message.from_user.username)):
        await message.answer('Введите username админа без "@"')
        await Add_admin.username_admin.set()
    else:
        await message.answer("Ошибка! Нет доступа.")

@dp.message_handler(state=Add_admin.username_admin)
async def setcity(message : types.Message,state : FSMContext):
    username_admin = message.text
    cursor.execute(f"INSERT INTO admins(username) VALUES (?)", (username_admin,))
    connection.commit()
    await state.finish()
    await message.answer("Успішно добавлено")

@dp.message_handler(commands=['add_channel'])
async def admin_menu(message: types.Message):
    if(check_admin(message.from_user.username)):
        await message.answer('Введите рекламный канал')
        await Add_channel.channel_name.set()
    else:
    
        await message.answer("Ошибка! Нет доступа.")

@dp.message_handler(state=Add_channel.channel_name)
async def setcity(message : types.Message,state : FSMContext):
    if(check_admin(message.from_user.username)):
        channel_name = message.text
        cursor.execute(f"INSERT INTO channel(channel_name) VALUES (?)", (channel_name,))
        connection.commit()
        await state.finish()
        await message.answer("Успешно добавлено")

@dp.message_handler(text="👨‍💼 Добавить/изменить/удалить админа")
async def admin_menu(message: types.Message):
    if(check_admin(message.from_user.username)):
        cur = cursor.execute(f"SELECT * FROM admins")
        admins = cur.fetchall()
        i=1
        for admin in admins:
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            buttons = [
                types.InlineKeyboardButton(text="Редактировать", callback_data=cb_change_admin.new(ch_username=admin[0])),
                types.InlineKeyboardButton(text="Удалить", callback_data=cb_delete_admin.new(del_username=admin[0]))
                ]
            keyboard.add(*buttons)
            await message.answer(f"<b>Админ #{i}</b>\n\n{admin[0]}", reply_markup=keyboard, parse_mode='html')
            i+=1
        await message.reply("Нажмите /add_admin, чтобы добавить рекламный канал")


@dp.message_handler(text="📝 Добавить/изменить/удалить рекламный канал")
async def admin_menu(message: types.Message):
    if(check_admin(message.from_user.username)):
        cur = cursor.execute(f"SELECT * FROM channel")
        channels = cur.fetchall()
        i=1
        for channel in channels:
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            buttons = [
                types.InlineKeyboardButton(text="Редактировать", callback_data=cb_change_channel.new(channelname=channel[0])),
                types.InlineKeyboardButton(text="Удалить", callback_data=cb_delete_channel.new(channelname2=channel[0]))
                ]
            keyboard.add(*buttons)
            await message.answer(f"<b>Канал #{i}</b>\n\n{channel[0]}", reply_markup=keyboard, parse_mode='html')
            i+=1
        await message.reply("Нажмите /add_channel, чтобы добавить рекламный канал")
    else:
        await message.answer("Ошибка! Нет доступа.")


@dp.message_handler(text="Рассылка 2")
async def admin_menu(message: types.Message):
    if(check_admin(message.from_user.username)):
        await bot.send_message(message.chat.id,'Выберите действие',reply_markup=config.send2())

@dp.message_handler(text="Рассылка 3")
async def admin_menu(message: types.Message):
    if (check_admin(message.from_user.username)):
        await bot.send_message(message.chat.id,'Выберите действие',reply_markup=config.send3())

@dp.message_handler(text="Настройки рассылки")
async def admin_menu(message: types.Message):
    if(check_admin(message.from_user.username)):
        await bot.send_message(message.chat.id,'Выберите номер рассылки',reply_markup=config.sends())

# Рассылка 1
@dp.message_handler(text="Рассылка 1")
async def admin_menu(message: types.Message):
    if (check_admin(message.from_user.username)):
        await bot.send_message(message.chat.id,'Выберите действие',reply_markup=config.send1())

@dp.message_handler(text="Просмотр рассылки 1")
async def admin_menu(message: types.Message):
    if (check_admin(message.from_user.username)):
        sendtext1 = cursor.execute("SELECT `send_text1` FROM `sendes`").fetchmany(1)[0][0]
        paragraph = sendtext1.split('#')[0]
        await bot.send_photo(message.chat.id,open('1.jpg','rb'),caption=paragraph,parse_mode='html',reply_markup=config.but(sendtext1))

@dp.message_handler(text="Изменить рассылку 1")
async def admin_menu(message: types.Message):
    if (check_admin(message.from_user.username)):
        await bot.send_message(message.chat.id,'Отправьте фото рассылки')
        await Send.send1_photo.set()

@dp.message_handler(text="Разослать рассылку 1")
async def admin_menu(message: types.Message):
    if (check_admin(message.from_user.username)):
        sendtext1 = cursor.execute("SELECT `send_text1` FROM `sendes`").fetchmany(1)[0][0]
        paragraph = sendtext1.split('#')[0]
        id = cursor.execute("SELECT `id` FROM `users` WHERE `VIP` != ?",('Да',)).fetchall()
        for row in id:
            try:
                await bot.send_photo(row[0], open('1.jpg','rb'),caption=paragraph, parse_mode='html', reply_markup=config.but(sendtext1))
                cursor.execute("UPDATE `users` SET `active` = ? WHERE `id` = ?",(1,row[0]))
                connection.commit()
            except aiogram.utils.exceptions.BotBlocked:
                cursor.execute("UPDATE `users` SET `active` = ? WHERE `id` = ?",(0,row[0]))
                connection.commit()
# Рассылка 2
@dp.message_handler(text="Просмотр рассылки 2")
async def admin_menu(message: types.Message):
    if (check_admin(message.from_user.username)):
        sendtext2 = cursor.execute("SELECT `send_text2` FROM `sendes`").fetchmany(1)[0][0]
        paragraph = sendtext2.split('#')[0]
        await bot.send_photo(message.chat.id,open('2.jpg','rb'),caption=paragraph,parse_mode='html',reply_markup=config.but(sendtext2))

@dp.message_handler(text="Изменить рассылку 2")
async def admin_menu(message: types.Message):
    if (check_admin(message.from_user.username)):
        await bot.send_message(message.chat.id,'Отправьте фото рассылки')
        await Send2.send2_photo.set()

@dp.message_handler(text="Разослать рассылку 2")
async def admin_menu(message: types.Message):
    if (check_admin(message.from_user.username)):
        sendtext1 = cursor.execute("SELECT `send_text2` FROM `sendes`").fetchmany(1)[0][0]
        paragraph = sendtext1.split('#')[0]
        id = cursor.execute("SELECT `id` FROM `users` WHERE `VIP` != ?",('Да',)).fetchall()
        for row in id:
            try:
                await bot.send_photo(row[0], open('2.jpg','rb'),caption=paragraph, parse_mode='html', reply_markup=config.but(sendtext1))
                cursor.execute("UPDATE `users` SET `active` = ? WHERE `id` = ?",(1,row[0]))
                connection.commit()
            except aiogram.utils.exceptions.BotBlocked:
                cursor.execute("UPDATE `users` SET `active` = ? WHERE `id` = ?",(0,row[0]))
                connection.commit()

# Рассылка 3
@dp.message_handler(text="Просмотр рассылки 3")
async def admin_menu(message: types.Message):
    if (check_admin(message.from_user.username)):
        sendtext2 = cursor.execute("SELECT `send_text3` FROM `sendes`").fetchmany(1)[0][0]
        paragraph = sendtext2.split('#')[0]
        await bot.send_message(message.chat.id,paragraph,parse_mode='html',reply_markup=config.but(sendtext2))

@dp.message_handler(text="Изменить рассылку 3")
async def admin_menu(message: types.Message):
    if (check_admin(message.from_user.username)):
        await bot.send_message(message.chat.id,'Напишите текст рассылки 3')
        await Send3.send3.set()

@dp.message_handler(text="Разослать рассылку 3")
async def admin_menu(message: types.Message):
    if (check_admin(message.from_user.username)):
        sendtext1 = cursor.execute("SELECT `send_text3` FROM `sendes`").fetchmany(1)[0][0]
        paragraph = sendtext1.split('#')[0]
        id = cursor.execute("SELECT `id` FROM `users` WHERE `VIP` != ?",('Да',)).fetchall()
        for row in id:
            try:
                await bot.send_message(row[0],paragraph, parse_mode='html', reply_markup=config.but(sendtext1))
                cursor.execute("UPDATE `users` SET `active` = ? WHERE `id` = ?",(1,row[0]))
                connection.commit()
            except aiogram.utils.exceptions.BotBlocked:
                cursor.execute("UPDATE `users` SET `active` = ? WHERE `id` = ?",(0,row[0]))
                connection.commit()
#

@dp.message_handler(text="Как добавлять рассылку")
async def admin_menu(message: types.Message):
    if(check_admin(message.from_user.username)):
        await bot.send_message(message.chat.id,'Соблюдайте такие правила:\n\nСначала идёт текст, в котором не должно быть #, этот символ должен быть только тогда, когда вы хотите сделать кнопку. В противном случае сообщение будет выглядеть не так как нужно.\n\nЧтобы сделать кнопки, придерживайтесь такого формата в конце текста: # Кнопка 1 Название # Ссылка кнопки 1 \n\nВ итоге должно получится так:\n\nТекст рекламы\n# Кнопка 1 Название # Ссылка кнопки 1\n\nРазрешается печатать с тегами html, бот воспримет как надо')

@dp.message_handler(text="Выгрузка таблицы 💾")
async def vip_menu(message: types.Message):
    if(check_admin(message.from_user.username)):
        df = pandas.read_sql('select * from `users`', connection)
        df.to_excel(r'anonims.xlsx', index=False)
        sleep(0.5)
        with open('anonims.xlsx','rb') as anonims:
            await bot.send_document(message.chat.id,anonims)

#

@dp.message_handler(text="Повернутись 🔚")
async def back(message: types.Message):
    if check_vip(message.chat.id):
        await bot.send_message(message.chat.id, '⚡️Выбери действие',reply_markup=config.start())

#--- Меню настроек вип поиска
@dp.message_handler(text="Дівчата 🙍‍♀️")
async def girls(message: types.Message):
    if check_vip(message.chat.id):
        cursor.execute("UPDATE `users` SET `gender_search` = ? WHERE `id` = ? ",('Женщина',message.chat.id,))
        await bot.send_message(message.chat.id,'Успішно <b>оновлено!</b>\nНатискай кнопку пошуку!',reply_markup=config.start(),parse_mode='html')
        connection.commit()


@dp.message_handler(text="Випадковий гендер ❔")
async def girls(message: types.Message):
    if check_vip(message.chat.id):
        cursor.execute("UPDATE `users` SET `gender_search` = ? WHERE `id` = ? ",('Случайный',message.chat.id,))
        await bot.send_message(message.chat.id,'Успішно <b>оновлено!</b>\nНатискай кнопку пошуку!',reply_markup=config.start(),parse_mode='html')
        connection.commit()

@dp.message_handler(commands=['report'])
async def reports(message: types.Message):
    last_chat = cursor.execute('SELECT `last_chat` FROM `users` WHERE `id`=?',(message.chat.id,)).fetchmany(1)
    reports = cursor.execute("SELECT `reports` FROM `users` WHERE id=?",(last_chat[0][0],)).fetchmany(1)
    if last_chat[0][0] != None:
        cursor.execute("UPDATE `users` SET `reports`=? WHERE id=?",(int(reports[0][0])+1,last_chat[0][0],))
        cursor.execute("UPDATE `users` SET `last_chat`=? WHERE id=?",(None,message.chat.id,))
        cursor.execute("UPDATE `users` SET `last_chat`=? WHERE id=?", (None, last_chat[0][0],))
        await bot.send_message(message.chat.id,
                               '📢 <b>Скарга відправлена.\n\n<em>🌸 Дякую що допомагаєте робити бота краще!</em></b>',
                               parse_mode='html')
        connection.commit()
    else:
        await bot.send_message(message.chat.id,'Співрозмовник не може прийняти <b>скаргу</b>, або скаргу <b>було</b> вже надіслано!',parse_mode='html')

@dp.message_handler(commands=['back'])
async def back(message: types.Message):
    if check_vip(message.chat.id):
        last_chat = cursor.execute('SELECT `last_chat` FROM `users` WHERE `id`=?', (message.chat.id,)).fetchmany(1)
        if last_chat[0][0] != None:
            if not db.get_active_chat(last_chat[0][0]):
                await bot.send_message(last_chat[0][0],"🍀 Ваш минулий співрозмовник відправив вам <b>запит на возз'єднання діалогу!</b>",reply_markup=config.back_to_chat_markups(),parse_mode='html')
                await bot.send_message(message.chat.id,'🍀 Співрозмовник <b>отримав</b> пропозицію про повернення!',parse_mode='html')
                cursor.execute("UPDATE `users` SET `last_chat`=? WHERE id=?", (None, message.chat.id,))
                connection.commit()
            else:
                await bot.send_message(message.chat.id,'🍀 <b>Співрозмовник вже має активний чат :( </b>\n\nСпробуйте знову пізніше!',parse_mode='html')
        else:
            await bot.send_message(message.chat.id,'🍀 Співрозмовник <b>не може</b> прийняти повідомлення! або ви вже надсилали запит!',parse_mode='html')
    else:
        await bot.send_message(message.chat.id,'''<em>
Щоб активувати функцію повернення потрібна VIP підписка!

Купуючи підписку, ви підтримуєте чат.
Переваги преміум-підписки:

📌 Пошук по гендеру
👩 Преміум підписники можуть шукати тільки дівчат або лише хлопців 
🦋 Преміум підписники мають змогу шукати по віку 
🌃 Також вони можуть шукати по місту 

📌 Відсутність реклами
📲 Ми не показуємо рекламу преміум підписникам

📌 Підтримка чату
🎁 Чим більше ви нас підтримуєте, тим більше нових функцій ми впровадимо, краще модерувати чат і купувати більше реклами для збільшення кількості співрозмовників!</em>
''',parse_mode='html')




@dp.message_handler(commands=['rules'])
async def rules(message: types.Message):
    await bot.send_message(message.chat.id,'''
    📌<em><b>Правила спілкування в анонімному чаті:</b></em>

<em>1. Будь-які згадки психоактивних речовин (наркотиків)
2. Обговорення політики
3. Дитяча порнографія (ЦП)
4. Шахрайство (Scam)
5. Будь-яка реклама, спам
6. Розова, статева, сексуальна, та будь-яка інша дискримінація
7. Продажі чогось (наприклад - продаж інтимних фотографій, відео)
8. Будь-які дії, що порушують правила Telegram
9. Образлива поведінка</em>

❌ <em><b>За порушення правил - блокування облікового запису</b></em>''',
                           parse_mode='html')

@dp.callback_query_handler(text='disagree')
async def agree(call: types.CallbackQuery):
    last_chat = cursor.execute('SELECT `last_chat` FROM `users` WHERE `id`=?',(call.from_user.id,)).fetchmany(1)
    cursor.execute("UPDATE `users` SET `last_chat`=? WHERE id=?", (None, call.from_user.id,))
    cursor.execute("UPDATE `users` SET `last_chat`=? WHERE id=?", (None, last_chat[0][0],))
    connection.commit()
    await bot.send_message(call.from_user.id,'🍀 Успішно відхилено!')
    await bot.send_message(last_chat[0][0],'🍀 Ваш минулий співрозмовник <b>відхилив запит!</b>',parse_mode='html')
    await bot.delete_message(call.from_user.id,call.message.message_id)



@dp.callback_query_handler(text='agree')
async def agree(call: types.CallbackQuery):
    last_chat = cursor.execute('SELECT `last_chat` FROM `users` WHERE `id`=?',(call.from_user.id,)).fetchmany(1)
    await bot.delete_message(call.from_user.id,call.message.message_id)
    if last_chat[0][0] != None:
        if db.create_chat(call.from_user.id, int(last_chat[0][0])) != False:
            mess = '🍀<b>Минулого співрозмовника знайдено. приємного спілкування!</b>\n\n/stop — закінчити діалог'
            await bot.send_message(call.from_user.id, mess, parse_mode='html', reply_markup=config.STOP())
            await bot.send_message(last_chat[0][0], mess, parse_mode='html', reply_markup=config.STOP())
            cursor.execute("UPDATE `users` SET `last_chat`=? WHERE id=?", (None, call.from_user.id,))
            connection.commit()
        else:
            await bot.send_message(call.from_user.id,'🍀 Співрозмовник не може прийняти повідомлення!')


@dp.message_handler(text="Хлопці 🙎‍♂️")
async def girls(message: types.Message):
    if check_vip(message.chat.id):
        cursor.execute("UPDATE `users` SET `gender_search` = ? WHERE `id` = ? ",('Мужчина',message.chat.id,))
        await bot.send_message(message.chat.id,'Успішно <b>оновлено!</b>\nНатискай кнопку пошуку!',reply_markup=config.start(),parse_mode='html')
        connection.commit()

@dp.message_handler(text="Змінити вік🙍‍♀️")
async def girls(message: types.Message):
    if check_vip(message.chat.id):
        await bot.send_message(message.chat.id, 'Введи початковий вік\nПриклад: 18')
        await VIP_age.age1.set()



@dp.message_handler(text="Змінити місто 🌆")
async def change_city(message: types.Message):
    if check_vip(message.chat.id):
        coun = []
        keyboard = types.InlineKeyboardMarkup(row_width=4)
        for country in config.countryes:
            coun.append(types.InlineKeyboardButton(text=country, callback_data=vip_cb_country.new(vip_countryname=country)))
        keyboard.add(*coun)
        await bot.send_message(message.chat.id, 'Оберіть місто для пошуку', reply_markup=keyboard)




@dp.message_handler(text="Випадкове місто ❔")
async def city(message: types.Message):
    if check_vip(message.chat.id):
        cursor.execute("UPDATE `users` SET `city_search` = ? WHERE `id` = ? ",('Случайный',message.chat.id,))
        await bot.send_message(message.chat.id,'Успішно <b>оновлено!</b>\nНатискай кнопку пошуку!',reply_markup=config.start(),parse_mode='html')
        connection.commit()


@dp.message_handler(text="Випадковий вік ❔")
async def girls(message: types.Message):
    if check_vip(message.chat.id):
        cursor.execute("UPDATE `users` SET `age_search` = ? WHERE `id` = ? ",('Случайный',message.chat.id,))
        await bot.send_message(message.chat.id,'Успішно <b>оновлено!</b>\nНатискай кнопку пошуку!',reply_markup=config.start(),parse_mode='html')
        connection.commit()


@dp.message_handler(text="🌸 Пошук по віку")
async def back(message: types.Message):
    if check_vip(message.chat.id):
        await bot.send_message(message.chat.id,'Обери параметри пошуку',parse_mode='html',reply_markup=config.age_search())
    else:
        await bot.send_message(message.chat.id,'''<em>
Щоб активувати функцію пошуку по віку потрібна VIP підписка!

Купуючи підписку, ви підтримуєте чат.
Переваги преміум-підписки:

📌 Пошук по гендеру
👩 Преміум підписники можуть шукати тільки дівчат або лише хлопців 
🦋 Преміум підписники мають змогу шукати по віку 
🌃 Також вони можуть шукати по місту 

📌 Відсутність реклами
📲 Ми не показуємо рекламу преміум підписникам

📌 Підтримка чату
🎁 Чим більше ви нас підтримуєте, тим більше нових функцій ми впровадимо, краще модерувати чат і купувати більше реклами для збільшення кількості співрозмовників!</em>
''',parse_mode='html')

@dp.message_handler(text="🌃 Пошук по місту")
async def back(message: types.Message):
    if check_vip(message.chat.id):
        await bot.send_message(message.chat.id,'Обери параметри пошуку',parse_mode='html',reply_markup=config.vip_city())
    else:
        await bot.send_message(message.chat.id,'''<em>
Щоб активувати функцію пошуку по місту потрібна VIP підписка!

Купуючи підписку, ви підтримуєте чат.
Переваги преміум-підписки:

📌 Пошук по гендеру
👩 Преміум підписники можуть шукати тільки дівчат або лише хлопців 
🦋 Преміум підписники мають змогу шукати по віку 
🌃 Також вони можуть шукати по місту 

📌 Відсутність реклами
📲 Ми не показуємо рекламу преміум підписникам

📌 Підтримка чату
🎁 Чим більше ви нас підтримуєте, тим більше нових функцій ми впровадимо, краще модерувати чат і купувати більше реклами для збільшення кількості співрозмовників!</em>
''',parse_mode='html')

        


@dp.message_handler(content_types=['photo'],state=Send.send1_photo)
async def setsend1(message : types.Message,state : FSMContext):
    await message.photo[-1].download('1.jpg')
    await bot.send_message(state.user,'Успешно изменено',reply_markup=config.send1())
    await bot.send_message(message.chat.id,'Введите текст рассылки')
    await Send.send1.set()

@dp.message_handler(state=Send.send1)
async def setsend1(message : types.Message,state : FSMContext):
    text = message.text
    cursor.execute("UPDATE `sendes` SET `send_text1` = ?",(text,)).fetchmany(1)
    connection.commit()
    await bot.send_message(message.chat.id,'Рассылка 1 успешно изменена.',reply_markup=config.send1())
    await state.finish()

@dp.message_handler(state=Send3.send3)
async def setsend3(message : types.Message,state : FSMContext):
    text = message.text
    cursor.execute("UPDATE `sendes` SET `send_text3` = ?",(text,)).fetchmany(1)
    connection.commit()
    await bot.send_message(message.chat.id,'Рассылка 3 успешно изменена.',reply_markup=config.send3())
    await state.finish()




@dp.message_handler(content_types=['photo'],state=Send2.send2_photo)
async def setsend2(message : types.Message,state : FSMContext):
    await message.photo[-1].download('2.jpg')
    await bot.send_message(state.user,'Успешно изменено')
    await bot.send_message(message.chat.id,'Введите текст рассылки')
    await Send2.send2.set()

@dp.message_handler(state=Send2.send2)
async def setsend1(message : types.Message,state : FSMContext):
    text = message.text
    cursor.execute("UPDATE `sendes` SET `send_text2` = ?",(text,)).fetchmany(1)
    connection.commit()
    await bot.send_message(message.chat.id,'Рассылка 2 успешно изменена.',reply_markup=config.send2())
    await state.finish()


@dp.message_handler(state=VIP_age.age1)
async def setage1(message : types.Message,state : FSMContext):
    config.AGE.clear()
    age_first = message.text
    if age_first.isdigit():
        config.AGE.append(age_first)
        await VIP_age.next()
        await message.answer("Введи кінечний вік\nПриклад: 24")
    else:
        await message.answer("Введите число!")  

@dp.message_handler(state=VIP_age.age2)
async def age2(message : types.Message,state : FSMContext):
    age_second = message.text
    if age_second.isdigit():
        if int(age_second) >= int(config.AGE[0]):
            config.AGE.append(age_second)
            cursor.execute(f"UPDATE users SET age_search=? WHERE id={message.from_user.id}", (f"{config.AGE[0]}-{config.AGE[1]}",))
            connection.commit()
            await state.finish()
            await bot.send_message(message.chat.id, 'Успішно <b>оновлено!</b>\nНатискай кнопку пошуку!', parse_mode='html',
                                   reply_markup=config.start())
        else:
            await message.answer("Вік має перевищувати попереднє число!")
    else:
        await message.answer("Введи число!")



@dp.message_handler(text="❤️ Пошук по гендеру")
async def search_params(message: types.Message):
    if check_vip(message.chat.id):
        await bot.send_message(message.chat.id,'Обери параметри пошуку',parse_mode='html',reply_markup=config.gen())
    else:
        await bot.send_message(message.chat.id,'''<em>
Щоб активувати функцію пошуку по гендеру VIP підписка!

Купуючи підписку, ви підтримуєте чат.
Переваги преміум-підписки:

📌 Пошук по гендеру
👩 Преміум підписники можуть шукати тільки дівчат або лише хлопців 
🦋 Преміум підписники мають змогу шукати по віку 
🌃 Також вони можуть шукати по місту 

📌 Відсутність реклами
📲 Ми не показуємо рекламу преміум підписникам

📌 Підтримка чату
🎁 Чим більше ви нас підтримуєте, тим більше нових функцій ми впровадимо, краще модерувати чат і купувати більше реклами для збільшення кількості співрозмовників!</em>
''',parse_mode='html')




@dp.message_handler(text="📈 Статистика")
async def admin_menu(message: types.Message):
    if(check_admin(message.from_user.username)):
        men = 0
        women = 0
        active = 0
        disactive = 0
        rows = cursor.execute(f"SELECT * FROM users")
        users = rows.fetchall()
        for user in users:
            if user[1]=='Мужчина':
                men+=1
            if user[1]=='Женщина':
                women+=1
            if user[12] == 1:
                active += 1
            else:
                disactive += 1

        await message.answer(f"<b>Статистика</b>\n\nВсего людей: {len(users)}\nАктивных: {active}\nНеактивных: {disactive}\n\nМужчин: {men}\nЖенщин: {women}", parse_mode='html')

@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    if message.chat.type == 'private':
        chat = cursor.execute("SELECT * FROM `rooms` WHERE `chat_id`=?", (message.chat.id,)).fetchone()
        if message.text == '⭐️ Пошук співрозмовника' or message.text == '/next' and chat == None:
            if check_reports(message.chat.id) == True or check_vip(message.chat.id) == True:
                # Проверка на подписку ----------------------------------------------------------
                for channel in get_channel():
                    if not check_status(await bot.get_chat_member(chat_id=f"@{channel[0]}", user_id=message.from_user.id)):
                         if check_vip(message.chat.id) != True:
                             await message.answer("✋ Щоб продовжити користуватися ботом, ви повинні підписатись наші канали",
                                                 reply_markup=keyboard_sub())
                             config.FLAG = False
                             break
                         else:
                             config.FLAG = True
                    else:
                        config.FLAG = True
                # Проверка на подписку ----------------------------------------------------------
                if config.FLAG != False:
                    user_info = db.get_info_search(message.chat.id)
                    chat_two = user_info[0]
                    if db.create_chat(message.chat.id,chat_two) == False:
                        db.add_queue(db.get_user(message.chat.id))
                        await message.answer("🔎 Пошук співрозмовника..", reply_markup=config.buttoncancel())
                    else:
                        cursor.execute('UPDATE `users` SET `last_chat`=? WHERE `id`=?',(chat_two,message.chat.id,))
                        cursor.execute('UPDATE `users` SET `last_chat`=? WHERE `id`=?',(message.chat.id,chat_two,))
                        connection.commit()
                        if check_vip(message.chat.id) != True:
                            mess = '🍀<b>Співрозмовника знайдено. приємного спілкування!</b>\n\n/stop - закінчити діалог\n/vip - отримати VIP'
                            await bot.send_message(message.chat.id, mess, reply_markup=config.STOP(), parse_mode='html')
                        else:
                            mess = '🍀<b>Співрозмовника знайдено. приємного спілкування!</b>\n\n/stop — закінчити діалог'
                            await bot.send_message(message.chat.id, mess, reply_markup=config.STOP(), parse_mode='html')
                        if check_vip(chat_two) != True:
                            mess = '🍀<b>Співрозмовника знайдено. приємного спілкування!</b>\n\n/stop - закінчити діалог\n/vip - отримати VIP'
                            await bot.send_message(chat_two, mess, reply_markup=config.STOP(), parse_mode='html')
                        else:
                            mess = '🍀<b>Співрозмовника знайдено. приємного спілкування!</b>\n\n/stop — закінчити діалог'
                            await bot.send_message(chat_two, mess, reply_markup=config.STOP(), parse_mode='html')
            else:
                await bot.send_message(message.chat.id,'<b>🍀 На вас поскаржилося 10 користувачів!</b>\n\nДоступ до спілкування обмежений!\nДля зняття блокування купіть VIP 🏆',parse_mode='html')
        elif message.text == '❌ Зупинити пошук':
            db.delete_queue(message.chat.id)
            await bot.send_message(message.chat.id,'Пошук <b>зупинено</b>',reply_markup=config.start(),parse_mode='html')


        else:
            if db.get_active_chat(message.chat.id) != False:
                chat_info = db.get_active_chat(message.chat.id)
                await bot.send_message(chat_info[1],message.text)
            else:
                await bot.send_message(message.chat.id,'<b>Я не розумію тебе ☹️</b>\n\nДля використання бота користуйся кнопками знизу або меню команд',parse_mode='html')


#----------------------------------------------------Отправка гиф,фото,видео,документ,войс,аудио start

@dp.message_handler(content_types=['audio'])
async def send_voice(message: types.Message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            if check_vip(message.chat.id) == True:
                await bot.send_audio(chat_info[1], message.audio.file_id)
            else:
                await bot.send_message(message.chat.id,
                                       ''''<em>Для відправки медіа потрібен VIP статус!

Купуючи підписку, ви підтримуєте чат.
Переваги преміум-підписки:

📌 Пошук по гендеру
👩 Преміум підписники можуть шукати тільки дівчат або лише хлопців 
🦋 Преміум підписники мають змогу шукати по віку 
🌃 Також вони можуть шукати по місту 

📌 Відсутність реклами
📲 Ми не показуємо рекламу преміум підписникам

📌 Підтримка чату
🎁 Чим більше ви нас підтримуєте, тим більше нових функцій ми впровадимо, краще модерувати чат і купувати більше реклами для збільшення кількості співрозмовників!</em>
''',                                     parse_mode='html')


@dp.message_handler(content_types=['sticker'])
async def send_voice(message: types.Message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            if check_vip(message.chat.id) == True:
                await bot.send_sticker(chat_info[1], message.sticker.file_id)
            else:
                await bot.send_message(message.chat.id,
                                       '''<em>Для відправки медіа потрібен VIP статус!

Купуючи підписку, ви підтримуєте чат.
Переваги преміум-підписки:

📌 Пошук по гендеру
👩 Преміум підписники можуть шукати тільки дівчат або лише хлопців 
🦋 Преміум підписники мають змогу шукати по віку 
🌃 Також вони можуть шукати по місту 

📌 Відсутність реклами
📲 Ми не показуємо рекламу преміум підписникам

📌 Підтримка чату
🎁 Чим більше ви нас підтримуєте, тим більше нових функцій ми впровадимо, краще модерувати чат і купувати більше реклами для збільшення кількості співрозмовників!</em>
''',
                                       parse_mode='html')


@dp.message_handler(content_types=['animation'])
async def send_voice(message: types.Message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            if check_vip(message.chat.id) == True:
                await bot.send_animation(chat_info[1], message.animation.file_id)
            else:
                await bot.send_message(message.chat.id,
                                       '''<em>Для відправки медіа потрібен VIP статус!

Купуючи підписку, ви підтримуєте чат.
Переваги преміум-підписки:

📌 Пошук по гендеру
👩 Преміум підписники можуть шукати тільки дівчат або лише хлопців 
🦋 Преміум підписники мають змогу шукати по віку 
🌃 Також вони можуть шукати по місту 

📌 Відсутність реклами
📲 Ми не показуємо рекламу преміум підписникам

📌 Підтримка чату
🎁 Чим більше ви нас підтримуєте, тим більше нових функцій ми впровадимо, краще модерувати чат і купувати більше реклами для збільшення кількості співрозмовників!</em>
''',
                                       parse_mode='html')


@dp.message_handler(content_types=['document'])
async def send_voice(message: types.Message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            if check_vip(message.chat.id) == True:
                await bot.send_document(chat_info[1], message.document.file_id)
            else:
                await bot.send_message(message.chat.id,
                                       '''<em>Для відправки медіа потрібен VIP статус!

Купуючи підписку, ви підтримуєте чат.
Переваги преміум-підписки:

📌 Пошук по гендеру
👩 Преміум підписники можуть шукати тільки дівчат або лише хлопців 
🦋 Преміум підписники мають змогу шукати по віку 
🌃 Також вони можуть шукати по місту 

📌 Відсутність реклами
📲 Ми не показуємо рекламу преміум підписникам

📌 Підтримка чату
🎁 Чим більше ви нас підтримуєте, тим більше нових функцій ми впровадимо, краще модерувати чат і купувати більше реклами для збільшення кількості співрозмовників!</em>
''',
                                       parse_mode='html')


@dp.message_handler(content_types=['video'])
async def send_voice(message: types.Message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            if check_vip(message.chat.id) == True:
                await bot.send_video(chat_info[1], message.video.file_id)
            else:
                await bot.send_message(message.chat.id,
                                       '''<em>Для відправки медіа потрібен VIP статус!

Купуючи підписку, ви підтримуєте чат.
Переваги преміум-підписки:

📌 Пошук по гендеру
👩 Преміум підписники можуть шукати тільки дівчат або лише хлопців 
🦋 Преміум підписники мають змогу шукати по віку 
🌃 Також вони можуть шукати по місту 

📌 Відсутність реклами
📲 Ми не показуємо рекламу преміум підписникам

📌 Підтримка чату
🎁 Чим більше ви нас підтримуєте, тим більше нових функцій ми впровадимо, краще модерувати чат і купувати більше реклами для збільшення кількості співрозмовників!</em>
''',
                                       parse_mode='html')


@dp.message_handler(content_types=['photo'])
async def send_voice(message: types.Message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            if check_vip(message.chat.id) == True:
                await bot.send_photo(chat_info[1], message.photo[-1].file_id)
            else:
                await bot.send_message(message.chat.id,
                                       '''<em>Для відправки медіа потрібен VIP статус!

Купуючи підписку, ви підтримуєте чат.
Переваги преміум-підписки:

📌 Пошук по гендеру
👩 Преміум підписники можуть шукати тільки дівчат або лише хлопців 
🦋 Преміум підписники мають змогу шукати по віку 
🌃 Також вони можуть шукати по місту 

📌 Відсутність реклами
📲 Ми не показуємо рекламу преміум підписникам

📌 Підтримка чату
🎁 Чим більше ви нас підтримуєте, тим більше нових функцій ми впровадимо, краще модерувати чат і купувати більше реклами для збільшення кількості співрозмовників!</em>
''',
                                       parse_mode='html')


@dp.message_handler(content_types=['voice'])
async def send_voice(message: types.Message):
    if message.chat.type == 'private':
        chat_info = db.get_active_chat(message.chat.id)
        if chat_info != False:
            if check_vip(message.chat.id) == True:
                await bot.send_voice(chat_info[1], message.voice.file_id)
            else:
                await bot.send_message(message.chat.id,
                                       '''<em>Для відправки медіа потрібен VIP статус!

Купуючи підписку, ви підтримуєте чат.
Переваги преміум-підписки:

📌 Пошук по гендеру
👩 Преміум підписники можуть шукати тільки дівчат або лише хлопців 
🦋 Преміум підписники мають змогу шукати по віку 
🌃 Також вони можуть шукати по місту 

📌 Відсутність реклами
📲 Ми не показуємо рекламу преміум підписникам

📌 Підтримка чату
🎁 Чим більше ви нас підтримуєте, тим більше нових функцій ми впровадимо, краще модерувати чат і купувати більше реклами для збільшення кількості співрозмовників!</em>
''',
                                       parse_mode='html')
#----------------------------------------------------Отправка гиф,фото,видео,документ,войс. end
# Калебк для гендера
@dp.callback_query_handler(text="man")
async def man(call: types.CallbackQuery):
    cursor.execute(f"UPDATE users SET gender='Мужчина' WHERE id=?", (call.from_user.id,))
    connection.commit()
    await call.message.delete()
    await bot.send_message(call.from_user.id,'Введи свій вік')
    await Register.old.set()

@dp.callback_query_handler(text="woman")
async def woman(call: types.CallbackQuery):
    cursor.execute(f"UPDATE users SET gender='Женщина' WHERE id=?", (call.from_user.id,))
    connection.commit()
    await call.message.delete()
    await bot.send_message(call.from_user.id, 'Введи свій вік')
    await Register.old.set()
#

@dp.message_handler(state=Register.old)
async def setold(message : types.Message,state : FSMContext):
    coun = []
    keyboard = types.InlineKeyboardMarkup(row_width=4)
    for country in config.countryes:
        coun.append(types.InlineKeyboardButton(text=country, callback_data=cb_country.new(countryname=country)))
    keyboard.add(*coun)
    old = message.text
    if old.isdigit() and 1 < int(old) <= 101:
        cursor.execute(f"UPDATE users SET age=? WHERE id=?", (old, state.user,))
        connection.commit()
        await state.finish()
        await message.answer(f"Обери найближче до тебе місто!", reply_markup=keyboard, parse_mode='html')
        await state.finish()
    else:
        await bot.send_message(state.user,'Невідоме значення, бот приймає вік в межах від 1 до 101 і лише цифрами')


@dp.callback_query_handler(text="change")
async def change(call : types.CallbackQuery):
    await call.message.delete()
    await bot.send_message(call.from_user.id, 'Обери стать', reply_markup=config.gender())

@dp.callback_query_handler(text="check_sub")
async def check_sub(call: types.CallbackQuery):
    for channel in get_channel():
        if not check_status(await bot.get_chat_member(chat_id=f"@{channel[0]}", user_id=call.from_user.id)):
            await call.answer("Ви не підписались на канали!", show_alert=True)
            config.FLAG = False
            break
        else:
            config.FLAG = True
    if config.FLAG == True:
        await call.answer("Успішно!", show_alert=True)
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await bot.send_message(call.from_user.id,'⚡️<b>Обери дію:</b>', parse_mode='html',reply_markup=config.start())

@dp.callback_query_handler(cb_country.filter())
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    contryname = callback_data['countryname']
    contryname = contryname.split()[0]
    cursor.execute(f'UPDATE users SET city=? WHERE id=?', (contryname,call.from_user.id,))
    connection.commit()
    await call.message.delete()
    await bot.send_message(call.from_user.id,'Успішно! Тепер ти можеш знайти собі співрозмовника!',reply_markup=config.start())


@dp.callback_query_handler(vip_cb_country.filter())
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    contryname = callback_data['vip_countryname']
    contryname = contryname.split()[0]
    cursor.execute(f'UPDATE users SET city_search=? WHERE id=?', (contryname, call.from_user.id,))
    connection.commit()
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await bot.send_message(call.from_user.id, "Успішно <b>оновлено!</b>\nНатискай кнопку пошуку!", parse_mode='html',reply_markup=config.start())

#Редактировать канал
@dp.callback_query_handler(cb_change_channel.filter())
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    old_channel = callback_data["channelname"]
    cursor.execute(f"UPDATE channel SET temp_name=? WHERE channel_name=?", (old_channel, old_channel))
    connection.commit()
    await bot.send_message(call.from_user.id, 'Введите новый рекламный канал')
    await Change_channel.channel_name.set()


@dp.message_handler(state=Change_channel.channel_name)
async def setcity(message : types.Message,state : FSMContext):
    channel_to_change = message.text
    cursor.execute(f"UPDATE channel SET channel_name=? WHERE channel_name=temp_name", (channel_to_change,))
    cursor.execute(f"UPDATE channel SET temp_name=NULL WHERE channel_name=?", (channel_to_change,))
    connection.commit()
    await state.finish()
    await message.answer("Успешно изменено")


#Удалить канал 
@dp.callback_query_handler(cb_delete_channel.filter())
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    channel_name = callback_data["channelname2"]
    cursor.execute(f"DELETE FROM channel WHERE channel_name='{channel_name}';")
    connection.commit()
    await call.answer("Успешно!", show_alert=True)

#Редактирова админа
@dp.callback_query_handler(cb_change_admin.filter())
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    old_admin = callback_data["ch_username"]
    cursor.execute(f"UPDATE admins SET temp_name=? WHERE username=?", (old_admin, old_admin))
    connection.commit()
    await bot.send_message(call.from_user.id, "Введите новый username админа без '@'")
    await Change_admin.username_admin.set()


@dp.message_handler(state=Change_admin.username_admin)
async def setcity(message : types.Message,state : FSMContext):
    admin_to_change = message.text
    cursor.execute(f"UPDATE admins SET username=? WHERE username=temp_name", (admin_to_change,))
    cursor.execute(f"UPDATE admins SET temp_name=NULL WHERE username=?", (admin_to_change,))
    connection.commit()
    await state.finish()
    await message.answer("Успешно изменено")

#Удалить админа
@dp.callback_query_handler(cb_delete_admin.filter())
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    username_admin = callback_data["del_username"]
    cursor.execute(f"DELETE FROM admins WHERE username='{username_admin}';")
    connection.commit()
    await call.answer("Успешно!", show_alert=True)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

