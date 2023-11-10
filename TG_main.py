import pkg_resources
import subprocess
import sys

def install_packages():
    with open('requirements.txt', 'r') as f:
        packages = f.readlines()

    for package in packages:
        package = package.strip()
        try:
            dist = pkg_resources.get_distribution(package)
            print('{} ({}) is installed'.format(dist.key, dist.version))
        except pkg_resources.DistributionNotFound:
            print('{} is NOT installed'.format(package))
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    install_packages()

import telebot
from telebot import types
import os
from dotenv import load_dotenv
from tabulate import tabulate
import DB_cursor
import DB_sold_product
import re

load_dotenv()

TOKEN = os.environ.get('TOKEN_DB')
bot = telebot.TeleBot(TOKEN)
list_for_database = [] 
id_name_count_product = {}

# Обработчик команд '/start' и '/help'
@bot.message_handler(commands=['start', 'стоп'])
def send_welcome(message):
    list_for_database.clear()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    itembtn1 = telebot.types.KeyboardButton('Створити матеріал')
    itembtn2 = telebot.types.KeyboardButton('Закуп матеріалу')
    itembtn3 = telebot.types.KeyboardButton('Видалити матеріал')
    itembtn4 = telebot.types.KeyboardButton('Продаж виробів')
    itembtn5 = telebot.types.KeyboardButton('Залишок по матеріалу')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5)
    bot.send_message(message.chat.id, "Виберіть опцію:", reply_markup=markup)



# ----------------------------------------------------------------------------------------------------------------------------
# Обработчик для кнопки "Створити матеріал"
@bot.message_handler(func=lambda message: message.text == 'Створити матеріал')
def handle_message(message):
    msg = bot.send_message(message.chat.id, "Назва:")
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return
    if len(input_text) > 1:
        list_for_database.append(input_text)
        msg = bot.send_message(message.chat.id, 'Введіть розмір:')
        bot.register_next_step_handler(msg, process_size_step)  # Исправленная строка
    else: 
        msg_error = bot.send_message(message.chat.id, 'Значення не може бути меншим за 1 символ. Спробуйте ще раз:')
        bot.register_next_step_handler(msg_error, process_name_step)


def process_size_step(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return
    try:
        input_text = int(message.text)
        list_for_database.append(input_text)
        msg = bot.send_message(message.chat.id, f"Натуральний (1/0)")
        bot.register_next_step_handler(msg, process_natural_step) 
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, process_size_step)


def process_natural_step(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return
    try:
        input_text = int(message.text)
        list_for_database.append(input_text)
        msg = bot.send_message(message.chat.id, f"Кількість")
        bot.register_next_step_handler(msg, process_quantity_step)
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть ціле число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, process_natural_step)


def process_quantity_step(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return    
    try:
        input_text = int(message.text)
        list_for_database.append(input_text)
        msg = bot.send_message(message.chat.id, f"Загальна ціна вказаної кількості")
        bot.register_next_step_handler(msg, process_total_cost_step)
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, process_quantity_step)


def process_total_cost_step(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return    
    try:
        input_text = float(message.text)
        list_for_database.append(input_text)
        DB_cursor.connection_to_db([tuple(list_for_database)], 'write_material.sql')
        bot.send_message(message.chat.id, 
f'''
● Назва: {list_for_database[0]}
● Розмір: {list_for_database[1]}
● Натуральність: {list_for_database[2]}
● Кількість: {list_for_database[3]}
● Загальна вартість: {list_for_database[4]}
  був створений.''')
        list_for_database.clear()  # очистити список для наступного вводу
        msg = bot.send_message(message.chat.id, "Назва:")  # повернутися до початкового кроку
        bot.register_next_step_handler(msg, process_name_step)
                                                                             
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, process_total_cost_step)




# ----------------------------------------------------------------------------------------------------------------------------
# Обработчик для кнопки "Видалити матеріал"
@bot.message_handler(func=lambda message: message.text == 'Видалити матеріал')
def send_remainder_material(message):
    text = DB_cursor.connection_to_db([('-1', )], 'show_material.sql')

    header = ["ID", "Назва", "Розмір", "Натуральний", "Залишок", "Загальна ціна по залишку", "Ціна за шт"]
    table = tabulate(text, headers=header, tablefmt="plain")

    bot.send_message(message.chat.id, f"```\n{table}\n```", parse_mode="Markdown")
    msg = bot.send_message(message.chat.id, f"Вкажіть ID матеріалу який бажаєте видалити.\nНе видаляйте матеріал якщо в нього є залежні записи в інших таблицях.", parse_mode="Markdown")
    bot.register_next_step_handler(msg, deleted_id_material)    

def deleted_id_material(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return
    else:
        DB_cursor.connection_to_db([(input_text)], 'deleted_material.sql')
        bot.send_message(message.chat.id, f"ID {input_text} Видалено", parse_mode="Markdown")


# ----------------------------------------------------------------------------------------------------------------------------
# Обработчик для кнопки "Залишок по матеріалу"
@bot.message_handler(func=lambda message: message.text == 'Залишок по матеріалу')
def send_remainder_material(message):
    text = DB_cursor.connection_to_db([('-1',)], 'show_material.sql')

    header = ["ID", "Назва", "Розмір", "Натуральний", "Залишок", "Загальна ціна по залишку", "Ціна за шт"]
    table = tabulate(text, headers=header, tablefmt="plain")

    bot.send_message(message.chat.id, f"```\n{table}\n```", parse_mode="Markdown")


# ----------------------------------------------------------------------------------------------------------------------------
# Обработчик для кнопки "Продаж виробів"
@bot.message_handler(func=lambda message: message.text == 'Продаж виробів')
def send_welcome(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="Корона", callback_data="Корона")
    button2 = telebot.types.InlineKeyboardButton(text="Браслет", callback_data="Браслет")
    keyboard.add(button1, button2)
    bot.send_message(message.chat.id, "Привіт! Обери тип продукту.", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def ask_type_material(call):

    if call.data == "Корона":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Поки що не працює")
        # msg = bot.send_message(call.message.chat.id, 'Вопрос 1')
        # bot.register_next_step_handler(msg, ask_question_2)
    elif call.data == "Браслет":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы обрали браслет")
        list_for_database.append('Браслет')
        msg = bot.send_message(call.message.chat.id, 'Дата продажу dd mm yyyy')
        bot.register_next_step_handler(msg, ask_question_date)


def ask_question_date(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return
    date_pattern = r"^(0[1-9]|[12][0-9]|3[01]) (0[1-9]|1[0-2]) \d{4}$"
    if not re.match(date_pattern, input_text):
        msg = bot.send_message(message.chat.id, 'Формат дати введений не коректно. Спробуйте ще раз')
        bot.register_next_step_handler(msg, ask_question_date)
    else:
        day, month, year = map(int, input_text.split())
        formatted_date = f"{year:04d}-{month:02d}-{day:02d}"
        print(formatted_date)
        list_for_database.append(formatted_date)
        msg = bot.send_message(message.chat.id, 'Ціна продажу')
        print(list_for_database)
        bot.register_next_step_handler(msg, ask_question_price)


def ask_question_price(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return
    try:
        input_text = float(message.text)
        send_remainder_material(message)
        msg = bot.send_message(message.chat.id, f"Використаний матеріал. Формат ID к-сть, ID к-сть ...")
        bot.register_next_step_handler(msg, asc_material_used)
        list_for_database.append(input_text)
        print(list_for_database)

    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, ask_question_price)


def asc_material_used(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        id_name_count_product.clear()
        return
    pattern = re.compile(r'^(\d+\s\d+,\s)*\d+\s\d+$')
    # Проверка соответствия строки формату
    if not pattern.match(input_text):
        msg = bot.send_message(message.chat.id, 'Формат дати введений не коректно. Спробуйте ще раз')
        bot.register_next_step_handler(msg, asc_material_used)
    else:
        
        print(list_for_database, 'list')
        list_for_database.append([tuple(map(int, pair.strip().split())) for pair in input_text.split(',')])
        try:
            for i in range(len(list_for_database[3])):


                print(list_for_database, 'то что нужно')


                result = DB_cursor.connection_to_db([(list_for_database[3][i][0], )], 'show_material.sql')


                id_name_count_product[result[0][0]] = [result[0][1], str(list_for_database[3][i][1]) + ' шт.']

                DB_sold_product.connection_to_db(list_for_database)

                materials = "\n".join([f"ID: {id}; {name[0]}; {name[1]}" for id, name in id_name_count_product.items()])
                # Создаем таблицу

                table_data = [
                    ["Тип", list_for_database[0]],
                    ["Дата", list_for_database[1]],
                    ["Ціна", list_for_database[2]],
                    ["Матеріал", materials]
                ]
                table = tabulate(table_data, tablefmt="plain")
                print(list_for_database)

            bot.send_message(message.chat.id, f"```\n{table}\n```", parse_mode="Markdown")
            msg = bot.send_message(message.chat.id, 'Дата продажу dd mm yyyy')  # сразу переходим к следующему шагу
            bot.register_next_step_handler(msg, ask_question_date)
        except:
            list_for_database.clear()
            id_name_count_product.clear()
            msg = bot.send_message(message.chat.id, 'Помилка при запиті до БД. Можливо вказаний не вірний ID.', parse_mode="Markdown")
            bot.register_next_step_handler(msg, asc_material_used)





bot.polling()




