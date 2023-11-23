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
import io

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
        bot.register_next_step_handler(msg, process_quantity_material_step)
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть ціле число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, process_natural_step)


def process_quantity_material_step(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return    
    try:
        input_text = int(message.text)
        list_for_database.append(input_text)
        msg = bot.send_message(message.chat.id, f"Оберіть фото")
        bot.register_next_step_handler(msg, process_photo)
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, process_quantity_material_step)


def process_photo(message):
    try:
        # Получение ID файла фото
        file_id = message.photo[-1].file_id
        # Получение информации о файле
        file_info = bot.get_file(file_id)
        # Скачивание файла
        downloaded_file = bot.download_file(file_info.file_path)
        list_for_database.append(downloaded_file)
        msg = bot.send_message(message.chat.id, f"Вкажіть знак зодіаку!")
        bot.register_next_step_handler(msg, process_zodiac_step)  # Замените process_next_step на следующий шаг в вашем процессе
        # print(list_for_database)
    except AttributeError:
        msg = bot.send_message(message.chat.id, 'Будь ласка відправте фото. Спробуйте ще раз.')
        bot.register_next_step_handler(msg, process_photo)


def process_zodiac_step(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return    
    try:
        input_text = message.text
        list_for_database.append(input_text)
        msg = bot.send_message(message.chat.id, f"Вкажіть загальну ціну за вказану кількість метеріалу")
        bot.register_next_step_handler(msg, process_total_cost_step)
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Сталась помилка, спробуйте ще раз')
        bot.register_next_step_handler(msg, process_zodiac_step)



def process_total_cost_step(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return    
    try:
        input_text = float(message.text)
        list_for_database.append(input_text)
        print(len(list_for_database))
        DB_cursor.connection_to_db(tuple(list_for_database), 'created_material.sql')
        bot.send_message(message.chat.id, 
f'''
● Назва: {list_for_database[0]}
● Розмір: {list_for_database[1]}
● Натуральність: {list_for_database[2]}
● Кількість: {list_for_database[3]}
● Загальна вартість: {list_for_database[5]}
● Знак зодіаку: {list_for_database[5]}
  був створений.''')
        # Преобразование бинарных данных в байтовый поток
        photo_stream = io.BytesIO(list_for_database[4])

        # Отправка файла
        bot.send_photo(message.chat.id, photo_stream)
        list_for_database.clear()  # очистити список для наступного вводу
        msg = bot.send_message(message.chat.id, "Назва:")  # повернутися до початкового кроку
        bot.register_next_step_handler(msg, process_name_step)
                                                                             
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, process_total_cost_step)


# ----------------------------------------------------------------------------------------------------------------------------
# Обработчик для кнопки "Залишок по матеріалу"
@bot.message_handler(func=lambda message: message.text == 'Залишок по матеріалу')
def send_remainder_material(message, back = False):
    text = DB_cursor.connection_to_db([('-1',)], 'show_material.sql')
    # Видаляємо останні два елемента в кожному кортежі
    data = [(tup[:-2]) for tup in text]
    header = ["ID", "Назва", "Розмір", "Натуральний", "Залишок", "Загальна ціна по залишку", "Ціна за шт"]
    table = tabulate(data, headers=header, tablefmt="plain")
    bot.send_message(message.chat.id, f"```\n{table}\n```", parse_mode="Markdown")
    if back:
        return
    msg = bot.send_message(message.chat.id, f"Введіть ID матеріалу для деталей, або введіть 'стоп'", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_quantity_step)


def process_quantity_step(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return    
    try:
        input_text = int(message.text)
        list_for_database.append(input_text)
        result = DB_cursor.connection_to_db(tuple(list_for_database, ), 'show_material.sql')
        bot.send_message(message.chat.id, 
        
f'''
● Назва: {result[0][1]}
● Розмір: {result[0][2]}
● Натуральність: {result[0][3]}
● Залишок: {result[0][4]}
● Загальна вартість: {result[0][5]}
● Вартість за 1 штуку: {result[0][6]}
● Знак зодіаку: {result[0][7]}
  був створений.''')
        # Преобразование бинарных данных в байтовый поток
        photo_stream = io.BytesIO(result[0][8])

        # Отправка файла
        bot.send_photo(message.chat.id, photo_stream)
        msg = bot.send_message(message.chat.id, f"Введіть ID матеріалу для деталей, або введіть 'стоп'")
        bot.register_next_step_handler(msg, process_quantity_step)
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, process_quantity_step)


# ----------------------------------------------------------------------------------------------------------------------------
# Обработчик для кнопки "Видалити матеріал"
@bot.message_handler(func=lambda message: message.text == 'Видалити матеріал')
def deleted_material(message):
    # text = DB_cursor.connection_to_db(('-1', ), 'show_material.sql')
    send_remainder_material(message, back = True)
    # header = ["ID", "Назва", "Розмір", "Натуральний", "Залишок", "Загальна ціна по залишку", "Ціна за шт"]
    # table = tabulate(text, headers=header, tablefmt="plain")

    # bot.send_message(message.chat.id, f"```\n{table}\n```", parse_mode="Markdown")
    msg = bot.send_message(message.chat.id, f"Вкажіть ID матеріалу який бажаєте видалити.\nНе видаляйте матеріал якщо в нього є залежні записи в інших таблицях.", parse_mode="Markdown")
    bot.register_next_step_handler(msg, deleted_id_material)    

def deleted_id_material(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return
    else:
        DB_cursor.connection_to_db((input_text, ), 'deleted_material.sql')
        bot.send_message(message.chat.id, f"ID {input_text} Видалено", parse_mode="Markdown")



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
        print(list_for_database, 'запись')
        list_for_database.append(input_text)
        id_product = DB_cursor.connection_to_db(tuple(list_for_database), 'sold_product.sql')
        send_remainder_material(message, back = True)
        msg = bot.send_message(message.chat.id, f"Використаний матеріал. Формат ID к-сть, ID к-сть ...")
        print(list_for_database, 'ошибка тут')
        bot.register_next_step_handler(msg, lambda m: asc_material_used(m, id_product[0][0], list_for_database[1]))
    except:
        msg = bot.send_message(message.chat.id, 'Перевірте формат. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, ask_question_price)


def asc_material_used(message, id_product, date_product):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        id_name_count_product.clear()
        try:
            DB_cursor.connection_to_db((id_product, ), 'deleted_product.sql')
            return
        except Exception as e:
            print(e)
            return 
    pattern = re.compile(r'^(\d+\s\d+,\s)*\d+\s\d+$')
    # Проверка соответствия строки формату
    if not pattern.match(input_text):
        msg = bot.send_message(message.chat.id, 'Формат введений не коректно. Спробуйте ще раз')
        bot.register_next_step_handler(msg, asc_material_used)
    else:
        list_for_database.clear()    
        print(list_for_database, 'проверка')
        list_for_database.extend([tuple(map(int, pair.split())) + (id_product, date_product) for pair in input_text.split(', ')])
        print(list_for_database, 'проверка после')
        try:
            # Если материала несколько
            for i in list_for_database:
                print(list_for_database, 'записываем')
                DB_cursor.connection_to_db(i, 'sold_material.sql')
            DB_cursor.connection_to_db((id_product, id_product,), 'update_sold_material.sql')
            sold_product = DB_cursor.connection_to_db((id_product, ),'show_sold_product.sql')
            old_material = DB_cursor.connection_to_db((id_product, ),'show_sold_material.sql')
            print(sold_product)
            print(old_material)
            

            

            product_info = f"**Проданный товар:**\n- ID: {sold_product[0][0]}\n- Тип: {sold_product[0][1]}\n- Дата продажи: {sold_product[0][2]}\n- Себестоимость: {sold_product[0][3]}\n- Цена продажи: {sold_product[0][4]}\n\n**Используемые материалы:**"

            for material in old_material:
                product_info += f"\n\n- ID материала: {material[0]}\n- Название: {material[1]}\n- Количество: {material[2]}"

            bot.send_message(message.chat.id, product_info)
            list_for_database.clear()
            list_for_database.append('Браслет')
            msg = bot.send_message(message.chat.id, 'Дата продажу dd mm yyyy')  # сразу переходим к следующему шагу
            bot.register_next_step_handler(msg, ask_question_date)
        
        except Exception as e:
            list_for_database.clear()
            id_name_count_product.clear()
            msg = bot.send_message(message.chat.id, 'Помилка при запиті до БД. Можливо вказаний не вірний ID.', parse_mode="Markdown")
            bot.register_next_step_handler(msg, asc_material_used)
            print(f"Произошла ошибка: {e}")


# ----------------------------------------------------------------------------------------------------------------------------
# Обработчик для кнопки "Закуп матеріалу"


@bot.message_handler(func=lambda message: message.text == 'Закуп матеріалу')
def material_purchased(message):
    send_remainder_material(message, back = True)
    msg = bot.send_message(message.chat.id, "ID Матеріалу:")
    bot.register_next_step_handler(msg, process_id_purchased_step)


def process_id_purchased_step(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return
    try:
        input_text = int(message.text)
        list_for_database.append(input_text)
        msg = bot.send_message(message.chat.id, f"Дата закупу dd mm yyyy")
        bot.register_next_step_handler(msg, ask_question_purchased_date) 
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, process_id_purchased_step)


def ask_question_purchased_date(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return
    date_pattern = r"^(0[1-9]|[12][0-9]|3[01]) (0[1-9]|1[0-2]) \d{4}$"
    if not re.match(date_pattern, input_text):
        msg = bot.send_message(message.chat.id, 'Формат дати введений не коректно. Спробуйте ще раз')
        bot.register_next_step_handler(msg, ask_question_purchased_date)
    else:
        day, month, year = map(int, input_text.split())
        formatted_date = f"{year:04d}-{month:02d}-{day:02d}"
        print(formatted_date)
        list_for_database.append(formatted_date)
        msg = bot.send_message(message.chat.id, 'Кількість матеріалу')
        print(list_for_database)
        bot.register_next_step_handler(msg, quantity_material_purchased_step)


def quantity_material_purchased_step(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return    
    try:
        input_text = int(message.text)
        list_for_database.append(input_text)
        msg = bot.send_message(message.chat.id, f"Вкажіть загальну ціну придбаного матеріалу")
        bot.register_next_step_handler(msg, process_total_cost_step_purchased)
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, quantity_material_purchased_step)


def process_total_cost_step_purchased(message):
    input_text = message.text
    if input_text.lower() == 'стоп':
        list_for_database.clear()
        return    
    try:
        input_text = float(message.text)
        list_for_database.append(input_text)
        print(len(list_for_database))
        material_purchased_id = DB_cursor.connection_to_db(tuple(list_for_database), 'created_purchased_material.sql')
        DB_cursor.connection_to_db(material_purchased_id[0], 'update_purchased_material.sql')

        print(material_purchased_id)
        bot.send_message(message.chat.id, 
f'''
Матеріал був доданий!''')

        list_for_database.clear()  # очистити список для наступного вводу
        send_remainder_material(message, back = True)
        msg = bot.send_message(message.chat.id, "ID Матеріалу:")  # повернутися до початкового кроку
        bot.register_next_step_handler(msg, process_id_purchased_step)
                                                                             
    except ValueError:
        msg = bot.send_message(message.chat.id, 'Введіть число. Спробуйте ще раз:')
        bot.register_next_step_handler(msg, process_total_cost_step_purchased)




bot.polling()




