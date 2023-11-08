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


load_dotenv()

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
list_for_database = [] 

# Обработчик команд '/start' и '/help'
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('Створити матеріал')
    itembtn2 = telebot.types.KeyboardButton('Закуп матеріалу')
    itembtn3 = telebot.types.KeyboardButton('Продаж виробів')
    itembtn4 = telebot.types.KeyboardButton('Залишок по матеріалу')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    bot.send_message(message.chat.id, "Виберіть опцію:", reply_markup=markup)


# ----------------------------------------------------------------------------------------------------------------------------
# Обработчик для кнопки "Залишок по матеріалу"
@bot.message_handler(func=lambda message: message.text == 'Залишок по матеріалу')
def send_remainder_material(message):
    text = DB_cursor.connection_to_db(False, 'show_material.sql')

    header = ["ID", "Назва", "Розмір", "Натуральний", "Залишок", "Загальна ціна по залишку", "Ціна за шт"]
    table = tabulate(text, headers=header, tablefmt="plain")

    bot.send_message(message.chat.id, f"```\n{table}\n```", parse_mode="Markdown")



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


bot.polling()


