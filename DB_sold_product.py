#!/usr/bin/python
import os
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))


def read_sql_file(file_name):
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

def generate_query(data):
    print(data)
    product_type, created_on, price, materials = data
    materials_values = ', '.join(f"({material_id}, '{created_on}', (select id from write_product), {count})" for material_id, count in materials)

    query = f"""
    WITH write_product AS (
       INSERT INTO product_sold (type, created_on,  price)
             VALUES ('{product_type}','{created_on}', {price} ) RETURNING id
    ),

    write_material as(
        INSERT INTO material_sold (material_id, created_on, product_id, count )
             VALUES {materials_values} RETURNING id
    )
    select * from write_product, write_material;

    UPDATE product_sold
    SET prime_cost = (
        SELECT sum(price_for_one_unit)
        FROM product_sold ps
        LEFT JOIN material_sold ms ON ps.id = ms.product_id
        LEFT JOIN material m ON m.id = ms.material_id
    )
    """
    return query



def connection_to_db(data):
    print(f'-- Processed;')
    conn_src_f = get_conn_src_dst()
    with conn_src_f.cursor() as cursor_facade:
        query = generate_query(data)
        cursor_facade.execute(query)
        conn_src_f.commit()

