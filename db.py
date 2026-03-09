import psycopg2
from os import getenv
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()

conn = psycopg2.connect(
    host=getenv("host"),
    database=getenv("database"),
    user=getenv("user"),
    password=getenv("password")
)

conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

try:
    cur.execute("""
        CREATE DATABASE shop_parts
        ENCODING 'UTF8'
        LC_COLLATE 'Russian_Russia.1251'
        LC_CTYPE 'Russian_Russia.1251'
        TEMPLATE template0
    """)
except:
    pass
cur.close()
conn.close()

print("База данных shop_parts создана успешно.")


DATABASE_URL = f"postgresql://{getenv('user')}:{getenv('password')}@{getenv('host')}/shop_parts"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()

def execute_query(sql, params=None):
    with engine.connect() as conn:
        if params:
            result = conn.execute(text(sql), params)
        else:
            result = conn.execute(text(sql))
        if result.returns_rows:
            return [dict(row._mapping) for row in result]
        else:
            conn.commit()
            return None