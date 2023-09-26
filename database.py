import os
import logging
import sqlite3
#import redis
#import ujson

import config


# # класс наследуется от redis.StrictRedis
# class Cache(redis.StrictRedis):
#     def __init__(self, host, port, password,
#                  charset="utf-8",
#                  decode_responses=True):
#         super(Cache, self).__init__(host, port,
#                                     password=password,
#                                     charset=charset,
#                                     decode_responses=decode_responses)
#         logging.info("Redis start")

#     def jset(self, name, value, ex=0):
#         """функция конвертирует python-объект в Json и сохранит"""
#         return self.setex(name, ex, ujson.dumps(value))

#     def jget(self, name):
#         """функция возвращает Json и конвертирует в python-объект"""
#         r = self.get(name)
#         if r is None:
#             return r
#         return ujson.loads(r)

""" Класс работы с базой данных """
class Database:
    """ Подключение """
    def __init__(self, name):
        self.name = name
        self._conn = self.connection()
        logging.info("Database connection established")

    def create_db(self):
        connection = sqlite3.connect(f"{self.name}.db")
        logging.info("Database created")
        cursor = connection.cursor()
        cursor.executescript('''
            CREATE TABLE products 
                (
                    id INTEGER PRIMARY KEY,
                    id_ozon INTEGER NOT NULL,
                    name_ozon VARCHAR NOT NULL,
                    processed_dttm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_flag BLOB DEFAULT false
                );
            CREATE TABLE users 
                (
                    id INTEGER NOT NULL,
                    user_name VARCHAR NOT NULL,
                    is_active BLOB DEFAULT true,
                    processed_dttm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_flag BLOB DEFAULT false
                );
            CREATE TABLE watch_lists 
                (
                    id INTEGER PRIMARY KEY,
                    id_user INTEGER NOT NULL,
                    id_product INTEGER NOT NULL,
                    is_active BLOB DEFAULT false,
                    processed_dttm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_flag BLOB DEFAULT false
                );
            CREATE TABLE product_prices 
                (
                    id INTEGER PRIMARY KEY,
                    id_product INTEGER NOT NULL,
                    is_avaialble BLOB DEFAULT false,
                    price REAL NULL,
                    processed_dttm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_flag BLOB DEFAULT false
                );
            CREATE VIEW active_products 
            AS 
            select distinct id_ozon from products
            where deleted_flag = false;
            ''')
        connection.commit()
        cursor.close()

    def connection(self):
        db_path = os.path.join(os.getcwd(), f"{self.name}.db")
        if not os.path.exists(db_path):
            self.create_db()
        return sqlite3.connect(f"{self.name}.db")

    def _execute_query(self, query, select=False):
        cursor = self._conn.cursor()
        cursor.execute(query)
        if select:
            records = cursor.fetchone()
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()
    def _execute_query_select_all(self, query, select=False):
        cursor = self._conn.cursor()
        cursor.execute(query)
        if select:
            records = cursor.fetchall()
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()

    """ Команды """
    #Пользователи
    async def add_user(self, user_id: int, username: str):
        insert_query = f"""INSERT INTO users (id, user_name)
                           VALUES ({user_id}, "{username}")"""
        self._execute_query(insert_query)
        logging.info(f"{user_id} added")

    async def check_user(self, user_id: int):
        select_query = f"""select user_name from users
                            where id = {user_id}"""
        record = self._execute_query(select_query, select=True)
        return record
    #Продукты
    async def check_product(self, product_id: int):
        select_query = f"""select id_ozon, deleted_flag from products
                            where id_ozon = {product_id}"""
        record = self._execute_query(select_query, select=True)
        return record
    async def add_product(self, id_ozon: int, name_ozon: str):
        insert_query = f"""INSERT INTO products (id_ozon, name_ozon)
                            VALUES ({id_ozon}, "{name_ozon}")"""
        self._execute_query(insert_query)
    def qget_active_products(self):
        select_query = f"""select * from active_products"""
        record = self._execute_query_select_all(select_query, select=True)
        return record
    #Цены
    def save_price(self,id,available,price):
        insert_query = f"""INSERT INTO product_prices (id_product, is_avaialble, price)
                            VALUES ({id}, {available}, {price})"""
        self._execute_query(insert_query)

    

    
    async def insert_products(self, product_name: str, product_link: str):
        insert_query = f"""INSERT INTO products (name, link)
                           VALUES ({product_name}, "{product_link}")"""
        self._execute_query(insert_query)
        logging.info(f"{product_name} added")

    # async def select_users(self, user_id: int):
    #     select_query = f"""SELECT leagues from users 
    #                        where id = {user_id}"""
    #     record = self._execute_query(select_query, select=True)
    #     return record

    # async def update_users(self, user_id: int, leagues: str):
    #     update_query = f"""Update users 
    #                           set leagues = "{leagues}" where id = {user_id}"""
    #     self._execute_query(update_query)
    #     logging.info(f"Leagues for user {user_id} updated")

    async def delete_products(self, product_id: int):
        delete_query = f"""Update products set deleted_flag = true WHERE id = {product_id}"""
        self._execute_query(delete_query)
        logging.info(f"Product {product_id} deleted")

    # async def insert_or_update_users(self, user_id: int, leagues: str):
    #     user_leagues = await self.select_users(user_id)
    #     if user_leagues is not None:
    #         await self.update_users(user_id, leagues)
    #     else:
    #         await self.insert_users(user_id, leagues)


# создание объектов cache и database
# cache = Cache(
#     host=config.REDIS_HOST,
#     port=config.REDIS_PORT,
#     password=config.REDIS_PASSWORD
# )
database = Database(config.BOT_DB_NAME)
