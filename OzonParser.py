from bs4 import BeautifulSoup
from selenium import webdriver
import undetected_chromedriver as uc
import ast

import psycopg2
import time


options = webdriver.ChromeOptions() 
options.headless = True
dr = uc.Chrome(options=options)

conn = psycopg2.connect(database="postgres",
                        host="localhost",
                        user="postgres",
                        password="123rty789",
                        port="5432")

ProductList = conn.cursor()
ProductList.execute("SELECT * FROM ozon.products where deleted_flag = false")


def get_price_ozon(url):
  dr.get(url)
  soup = BeautifulSoup(dr.page_source, 'lxml')
  soup = soup.find(id="state-webOzonAccountPrice-1587460-default-1").get('data-state') # вытаскивание блока с ценой
  product_price = int(ast.literal_eval(soup)['priceText'].split('₽')[0].replace(" ", "")) # вытаскивание самой цены
  return product_price

def write_price_ozon(prod_id, price = None, availabile = False):
  sql = """INSERT INTO ozon.availability (product_id, price, availabile) VALUES (%s, %s, %s)"""
  cursor = conn.cursor()
  if price is not None:
    availabile = True
  cursor.execute(sql, [prod_id, price, availabile])
  conn.commit()   
  

for row in ProductList:
  print (row[1])
  try:
    price = get_price_ozon(row[2])
  except:
    price = None
  write_price_ozon(row[0],price)
  time.sleep(0.5)



# 1 - доставать цену из карточки (OK)
# 2 - складывать цену в таблицу (OK)
# 3 - настроить список любимых товаров и запустить батч для сверки цен
# 4 - подключить бота для оповещения о ценах
# 5 - настроить механизм алертинга цен - высчитывать среднюю, минимальную, цену по которой хочу брать
# 6 - оповещения о битых ссылках / пропаже товара
# 7 - прикрутить управление таблицей через телегу
# 8 - разместить все это на VPS





# cursor = conn.cursor()
# cursor.execute("INSERT INTO a_table (c1, c2, c3) VALUES(%s, %s, %s)", (v1, v2, v3))
# conn.commit() # <- We MUST commit to reflect the inserted data
# cursor.close()
# conn.close()

# conn = sqlite3.connect('/path/to/file.db')
# cursor = conn.cursor()
# sql = """INSERT INTO mytable (ID, Speed, Power) VALUES (?, ?, ?)"""
# values = [(1,7,3000),(1,8,3500),(1,9,3900)]
# cursor.executemany(stmt, values)