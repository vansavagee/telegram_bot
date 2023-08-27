import telebot
from telebot import types
from database.dbapi import *
from src.bot import *

token = "6210146498:AAGi8YHpZWJCSKbl6R77iBb0esn2GQh1Wz0"
bot = telebot.TeleBot(token)
buffer = []


# db = DatabaseConnector('bot', 'tomatoaj', '', 'localhost','5433')
@bot.message_handler(commands=['start'])
def handle_start(message):
    start_menu = types.ReplyKeyboardMarkup(True, True)
    key_add = types.InlineKeyboardButton(text='/add')
    start_menu.add(key_add)
    key_delete = types.InlineKeyboardButton(text='/delete')
    start_menu.add(key_delete)
    key_list = types.InlineKeyboardButton(text='/list')
    start_menu.add(key_list)
    key_find = types.InlineKeyboardButton(text='/find')
    start_menu.add(key_find)
    key_borrow = types.InlineKeyboardButton(text='/borrow')
    start_menu.add(key_borrow)
    key_retrieve = types.InlineKeyboardButton(text='/retrieve')
    start_menu.add(key_retrieve)
    key_stats = types.InlineKeyboardButton(text='/stats')
    start_menu.add(key_stats)
    start_output = '''Что я могу сделать для вас?\n
/add - добавить новую книгу
/delete - удалить книгу
/list - вывести список книг
/find - найти книгу
/borrow - взять книгу
/retrieve - вернуть книгу
/stats - вывести статистику по книге'''
    bot.send_message(message.chat.id, start_output, reply_markup=start_menu)


@bot.message_handler(commands=['add', 'delete', 'list', 'find', 'borrow', 'retrieve', 'stats'])
def handle_cases(message):
    global buffer
    if len(buffer) != 0: buffer.clear()
    if message.text in ['/add', '/delete', '/find', '/borrow', '/stats']:
        buffer.append(message.text)
        bot.send_message(message.chat.id, "Введите название книги:")
        bot.register_next_step_handler(message, info_about_book__case_part_1)
    elif message.text == '/list':
        res = db.list_books()
        if len(res):
            output = "Текущий архив книг:\n"
            q = 1
            for i in res:
                output += str(q) + ". " + i[0] + " " + i[1] + " " + str(i[2])
                if len(i) == 3:
                    output += "\n"
                else:
                    output += i[3] + "\n"
                q += 1
            bot.send_message(message.chat.id, output)
        else:
            bot.send_message(message.chat.id, "Архив книг пуст!")
        handle_start(message)
    elif message.text == '/retrieve':
        if db.retrieve(message.from_user.id):
            bot.send_message(message.chat.id, "Книга успешно возвращена")
        else:
            bot.send_message(message.chat.id, "У вас нет взятых книг")
        handle_start(message)


def info_about_book__case_part_1(message):
    global buffer
    buffer.append(message.text)
    bot.send_message(message.chat.id, "Введите автора:")
    bot.register_next_step_handler(message, info_about_book__case_part_2)


def info_about_book__case_part_2(message):
    global buffer
    buffer.append(message.text)
    bot.send_message(message.chat.id, "Введите год издания:")
    bot.register_next_step_handler(message, info_about_book__case_part_3)


def info_about_book__case_part_3(message):
    global buffer
    buffer.append(message.text)
    if message.text.isdigit():
        if buffer[0] == "/add":
            res = db.add({"title": buffer[1], "author": buffer[2], "published": buffer[3]})
            if res:
                bot.send_message(message.chat.id, f'Книга добавлена, её id : {res}')
            else:
                bot.send_message(message.chat.id, 'Ошибка при добавлении книги')
            handle_start(message)

        elif buffer[0] == "/delete":
            if db.get_book({"title": buffer[1], "author": buffer[2], "published": buffer[3]}):
                bot.send_message(message.chat.id,
                                 f'Найдена книга: \"{buffer[1]}\", {buffer[2]}({buffer[3]} г.). Удаляем?')
                bot.register_next_step_handler(message, delete_part)
            else:
                bot.send_message(message.chat.id, 'Такой книги у нас нет')
                handle_start(message)
        elif buffer[0] == "/find":
            if db.get_book({"title": buffer[1], "author": buffer[2], "published": buffer[3]}):
                bot.send_message(message.chat.id, f'Найдена книга: \"{buffer[1]}\", {buffer[2]}({buffer[3]} г.)')
                handle_start(message)
            else:
                bot.send_message(message.chat.id, 'Такой книги у нас нет')
                handle_start(message)
        elif buffer[0] == "/borrow":
            if db.get_book({"title": buffer[1], "author": buffer[2], "published": buffer[3]}):
                bot.send_message(message.chat.id,
                                 f'Найдена книга: \"{buffer[1]}\", {buffer[2]}({buffer[3]} г.). Берем?')
                bot.register_next_step_handler(message, borrow_part)
            else:
                bot.send_message(message.chat.id, 'Такой книги у нас нет')
                handle_start(message)
        elif buffer[0] == "/stats":
            id = db.get_book({"title": buffer[1], "author": buffer[2], "published": buffer[3]})
            if id:
                text = f'Статистика доступна по [этому](http://127.0.0.1:5000//download/{id}) адресу'
                bot.send_message(message.chat.id, text, parse_mode='MarkdownV2')
            else:
                bot.send_message(message.chat.id, 'Такой книги у нас нет')
    else:
        bot.send_message(message.chat.id, 'Неверный ввод')
        handle_start(message)


def delete_part(message):
    if message.text.lower() == 'да':
        if db.delete({"title": buffer[1], "author": buffer[2], "published": buffer[3]}):
            bot.send_message(message.chat.id, ' Книга удалена')
        else:
            bot.send_message(message.chat.id, 'Невозможно удалить книгу')
        handle_start(message)
    elif message.text.lower() == 'нет':
        bot.send_message(message.chat.id, 'Удаление отменено')
        handle_start(message)
    elif message.text == '/start':
        handle_start(message)
    else:
        bot.send_message(message.chat.id,
                         'Выберите одну из достпуных опций(Да/Нет), "/start" - переход на начальное меню')
        bot.register_next_step_handler(message, delete_part)


def borrow_part(message):
    if message.text.lower() == 'да':
        if db.borrow({"title": buffer[1], "author": buffer[2], "published": buffer[3]}, message.from_user.id):
            bot.send_message(message.chat.id, 'Вы взяли книгу')
        else:
            bot.send_message(message.chat.id, 'Книгу сейчас невозможно взять')
        handle_start(message)
    elif message.text.lower() == 'нет':
        bot.send_message(message.chat.id, 'Создание брони отменено')
        handle_start(message)
    elif message.text == '/start':
        handle_start(message)
    else:
        bot.send_message(message.chat.id,
                         'Выберите одну из достпуных опций(Да/Нет), "/start" - переход на начальное меню')
        bot.register_next_step_handler(message, borrow_part)


bot.infinity_polling()
