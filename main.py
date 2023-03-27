import os
import json

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv

from models import create_tables, Publisher, Shop, Book, Stock, Sale


load_dotenv(find_dotenv())

driver = os.getenv('driver')
login = os.getenv('login')
password = os.getenv('password')
server_name = os.getenv('server_name')
server_port = os.getenv('server_port')
db_name = os.getenv('db_name')

DSN = driver+'://'+login+':'+password+'@'+server_name+':'+server_port+'/'+db_name
engine = sqlalchemy.create_engine(DSN)

create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    for record in data:
        model = {
            'publisher': Publisher,
            'shop': Shop,
            'book': Book,
            'stock': Stock,
            'sale': Sale
        }[record.get('model')]
        session.add(model(id=record.get('pk'), **record.get('fields')))
    session.commit()

publisher = input('Введите имя или идентификатор издателя: ').strip()

try:
    publisher = int(publisher)
    s = session.query(
        Book.title,
        Shop.name,
        Sale.price,
        Sale.date_sale
    ).join(Publisher).join(Stock).join(Shop).join(Sale).filter(
        Publisher.id == publisher
    ).all()
except ValueError:
    s = session.query(
        Book.title,
        Shop.name,
        Sale.price,
        Sale.date_sale
    ).join(Publisher).join(Stock).join(Shop).join(Sale).filter(
        Publisher.name.ilike(publisher)
    ).all()

session.close()

for c in s:
    print(f'{c.title:<40} | {c.name:<9} | {c.price:^7} | {c.date_sale:%d.%m.%Y %H:%M}')
