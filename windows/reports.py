import tkinter as tk
from tkinter import ttk, messagebox
from db import execute_query
from datetime import datetime


class ReportsWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Отчёты и аналитика")
        self.top.geometry("800x600")

        buttons = [
            ("Отчёт по продажам за период", self.sales_report),
            ("Топ-10 товаров", self.top_products),
            ("Остатки по категориям", self.stock_by_category),
            ("Заказы клиента (ввод ID)", self.customer_orders),
            ("Средний чек по месяцам", self.avg_check),
            ("Товары с низким остатком", self.low_stock),
            ("Выручка по поставщикам за период", self.supplier_revenue),
            ("Поиск запчастей", self.search_parts),
        ]

        for i, (text, cmd) in enumerate(buttons):
            tk.Button(self.top, text=text, command=cmd, width=30).grid(row=i, column=0, padx=10, pady=5, sticky='w')

        self.result_text = tk.Text(self.top, wrap=tk.WORD, height=25)
        self.result_text.grid(row=0, column=1, rowspan=len(buttons), padx=10, pady=5, sticky='nsew')
        scroll = tk.Scrollbar(self.top, orient=tk.VERTICAL, command=self.result_text.yview)
        scroll.grid(row=0, column=2, rowspan=len(buttons), sticky='ns')
        self.result_text.config(yscrollcommand=scroll.set)

        self.top.grid_columnconfigure(1, weight=1)
        self.top.grid_rowconfigure(0, weight=1)

    def clear_result(self):
        self.result_text.delete(1.0, tk.END)

    def display_result(self, data, columns=None):
        self.clear_result()
        if not data:
            self.result_text.insert(tk.END, "Нет данных\n")
            return
        if columns:
            header = "\t".join(columns) + "\n"
            self.result_text.insert(tk.END, header)
            self.result_text.insert(tk.END, "-" * 80 + "\n")
        for row in data:
            line = "\t".join(str(v) for v in row.values()) + "\n"
            self.result_text.insert(tk.END, line)

    def sales_report(self):
        dialog = tk.Toplevel(self.top)
        dialog.title("Период отчёта")
        tk.Label(dialog, text="Начало (ГГГГ-ММ-ДД):").grid(row=0, column=0)
        start_entry = tk.Entry(dialog)
        start_entry.grid(row=0, column=1)
        tk.Label(dialog, text="Конец (ГГГГ-ММ-ДД):").grid(row=1, column=0)
        end_entry = tk.Entry(dialog)
        end_entry.grid(row=1, column=1)

        def do_report():
            start = start_entry.get()
            end = end_entry.get()
            try:
                datetime.strptime(start, "%Y-%m-%d")
                datetime.strptime(end, "%Y-%m-%d")
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
                return
            result = execute_query("SELECT * FROM sales_report(:start, :end)", {"start": start, "end": end})
            self.display_result(result, ["Дата", "Кол-во заказов", "Сумма"])
            dialog.destroy()

        tk.Button(dialog, text="Выполнить", command=do_report).grid(row=2, column=0, columnspan=2, pady=10)

    def top_products(self):
        result = execute_query("SELECT * FROM top_products()")
        self.display_result(result, ["Товар", "Кол-во продаж", "Выручка"])

    def stock_by_category(self):
        result = execute_query("SELECT * FROM stock_by_category()")
        self.display_result(result, ["Категория", "Товар", "Остаток"])

    def customer_orders(self):
        dialog = tk.Toplevel(self.top)
        dialog.title("ID клиента")
        tk.Label(dialog, text="Введите ID клиента:").pack(pady=5)
        entry = tk.Entry(dialog)
        entry.pack(pady=5)

        def do_search():
            cust_id = entry.get()
            if not cust_id.isdigit():
                messagebox.showerror("Ошибка", "ID должен быть числом")
                return
            result = execute_query("SELECT * FROM customer_orders(:cid)", {"cid": int(cust_id)})
            self.display_result(result, ["ID заказа", "Дата", "Сотрудник", "Сумма", "Товары"])
            dialog.destroy()

        tk.Button(dialog, text="Показать", command=do_search).pack(pady=5)

    def avg_check(self):
        result = execute_query("SELECT * FROM avg_check_by_month()")
        self.display_result(result, ["Год", "Месяц", "Средний чек"])

    def low_stock(self):
        result = execute_query("SELECT * FROM low_stock()")
        self.display_result(result, ["Товар", "Остаток"])

    def supplier_revenue(self):
        dialog = tk.Toplevel(self.top)
        dialog.title("Период")
        tk.Label(dialog, text="Начало (ГГГГ-ММ-ДД):").grid(row=0, column=0)
        start_entry = tk.Entry(dialog)
        start_entry.grid(row=0, column=1)
        tk.Label(dialog, text="Конец (ГГГГ-ММ-ДД):").grid(row=1, column=0)
        end_entry = tk.Entry(dialog)
        end_entry.grid(row=1, column=1)

        def do_report():
            start = start_entry.get()
            end = end_entry.get()
            try:
                datetime.strptime(start, "%Y-%m-%d")
                datetime.strptime(end, "%Y-%m-%d")
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты")
                return
            result = execute_query("SELECT * FROM supplier_revenue(:start, :end)", {"start": start, "end": end})
            self.display_result(result, ["Поставщик", "Выручка"])
            dialog.destroy()

        tk.Button(dialog, text="Выполнить", command=do_report).grid(row=2, column=0, columnspan=2, pady=10)

    def search_parts(self):
        dialog = tk.Toplevel(self.top)
        dialog.title("Поиск")
        tk.Label(dialog, text="Введите текст для поиска:").pack(pady=5)
        entry = tk.Entry(dialog, width=40)
        entry.pack(pady=5)

        def do_search():
            text = entry.get()
            result = execute_query("SELECT * FROM search_parts(:txt)", {"txt": text})
            self.display_result(result, ["Товар", "Категория", "Тип техники", "Цена", "Поставщик"])
            dialog.destroy()

        tk.Button(dialog, text="Найти", command=do_search).pack(pady=5)


def open_window(parent):
    ReportsWindow(parent)