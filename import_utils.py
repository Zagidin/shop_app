import pandas as pd
from sqlalchemy import text
from db import engine

def import_excel_to_table(file_path, table_name, columns):
    """
    Импортирует данные из Excel в таблицу.
    :param file_path: путь к .xlsx файлу
    :param table_name: имя таблицы
    :param columns: список полей для вставки (без ID)
    """
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise Exception(f"Ошибка чтения Excel-файла: {e}")

    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"В файле отсутствуют колонки: {missing}")

    cols_str = ', '.join(columns)
    placeholders = ', '.join([f':{col}' for col in columns])
    sql = text(f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})")

    with engine.connect() as conn:
        for _, row in df.iterrows():
            params = {col: row[col] for col in columns}
            conn.execute(sql, params)
        conn.commit()


import_csv_data_table = f"""
    COPY customers(last_name, first_name, phone, email, discount)
    FROM 'C:\Zagidin\Рабочий_стол\Кклиенты.csv'
    DELIMITER ';'
    CSV HEADER;
"""