import tkinter as tk
from tkinter import ttk
from db import execute_query


class ProductsWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Товары")
        self.top.geometry("900x500")

        columns = ('ID', 'Название', 'Категория', 'Тип техники', 'Цена', 'Остаток', 'Поставщик')
        self.tree = ttk.Treeview(self.top, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.load_data()

    def load_data(self):
        rows = execute_query("""
            SELECT p.product_id, p.product_name, c.category_name, et.type_name,
                   p.price, p.stock_quantity, s.supplier_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN equipment_types et ON p.equip_type_id = et.equip_type_id
            LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
            ORDER BY p.product_id
        """)
        for r in rows:
            self.tree.insert('', tk.END, values=(r['product_id'], r['product_name'], r['category_name'],
                                                 r['type_name'], r['price'], r['stock_quantity'], r['supplier_name']))


def open_window(parent):
    ProductsWindow(parent)