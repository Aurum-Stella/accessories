#!/usr/bin/python
import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__)) # Отримання поточного каталогу скрипта

def read_sql_file(file_name):
    # Функція для зчитування SQL файлів
    with open(file_name, 'r', encoding='utf-8') as file:
        return file.read()
    

def get_conn_src_dst() -> psycopg2.connect:
    connection = psycopg2.connect(
        host=os.environ.get('HOST_DB'),
        user=os.environ.get('USER_DB'),
        password=os.environ.get('PASSWORD_DB'),
        database=os.environ.get('DB_NAME_DB'), 
        port=os.environ.get('PORT_DB'),
    )
    return connection


def queryng_sql(cursor, data, sql_file):
    fetch_loan_ids_query = read_sql_file(os.path.join(current_dir, "sql", sql_file))
    if data:
        cursor.executemany(fetch_loan_ids_query, data)
    else:
        cursor.execute(fetch_loan_ids_query)





def connection_to_db(input_data, sql_file):
    print(f'-- Processed;')
    print(input_data)
    conn_src_f = get_conn_src_dst()
    with conn_src_f.cursor() as cursor_facade:
        queryng_sql(cursor_facade, input_data, sql_file)
        try:
            return_data = cursor_facade.fetchall()
            return return_data
        except:
            pass
        finally:
            conn_src_f.commit() 


