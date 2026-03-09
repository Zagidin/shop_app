import tkinter as tk
from tkinter import ttk, messagebox
from db import execute_query
import json


class OrdersWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Все заказы")
        self.top.geometry("900x500")

        # Таблица заказов
        columns = ('ID', 'Дата', 'Клиент', 'Сотрудник', 'Сумма')
        self.tree = ttk.Treeview(self.top, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind('<<TreeviewSelect>>', self.on_order_select)

        # Таблица товаров в заказе
        tk.Label(self.top, text="Товары в заказе:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10)
        columns_items = ('Товар', 'Количество', 'Цена', 'Сумма')
        self.tree_items = ttk.Treeview(self.top, columns=columns_items, show='headings', height=8)
        for col in columns_items:
            self.tree_items.heading(col, text=col)
            self.tree_items.column(col, width=150)
        self.tree_items.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Кнопки
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Новый заказ", command=self.new_order).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить заказ", command=self.delete_order).pack(side=tk.LEFT, padx=5)

        self.load_orders()

    def load_orders(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = execute_query("""
            SELECT o.order_id, o.order_date, 
                   c.last_name || ' ' || c.first_name as customer,
                   e.last_name || ' ' || e.first_name as employee,
                   o.total_amount
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            LEFT JOIN employees e ON o.employee_id = e.employee_id
            ORDER BY o.order_date DESC
        """)
        for r in rows:
            self.tree.insert('', tk.END,
                             values=(r['order_id'], r['order_date'], r['customer'], r['employee'], r['total_amount']))

    def on_order_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        order_id = item['values'][0]
        self.load_order_items(order_id)

    def load_order_items(self, order_id):
        for row in self.tree_items.get_children():
            self.tree_items.delete(row)
        rows = execute_query("""
            SELECT p.product_name, oi.quantity, oi.price_at_sale,
                   (oi.quantity * oi.price_at_sale) as total
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = :order_id
        """, {"order_id": order_id})
        for r in rows:
            self.tree_items.insert('', tk.END,
                                   values=(r['product_name'], r['quantity'], r['price_at_sale'], r['total']))

    def new_order(self):
        NewOrderDialog(self.top, self)

    def delete_order(self):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        order_id = item['values'][0]
        if messagebox.askyesno("Подтверждение", "Удалить заказ? Все связанные позиции также будут удалены."):
            execute_query("DELETE FROM orders WHERE order_id = :id", {"id": order_id})
            self.load_orders()
            self.tree_items.delete(*self.tree_items.get_children())


class CustomerOrdersWindow:
    def __init__(self, parent, customer_id):
        self.top = tk.Toplevel(parent)
        self.top.title("Заказы клиента")
        self.top.geometry("800x500")
        self.customer_id = customer_id

        cust = \
        execute_query("SELECT last_name, first_name FROM customers WHERE customer_id = :id", {"id": customer_id})[0]
        cust_name = f"{cust['last_name']} {cust['first_name']}"
        tk.Label(self.top, text=f"Заказы клиента: {cust_name}", font=('Arial', 12, 'bold')).pack(pady=5)

        columns = ('ID заказа', 'Дата', 'Сотрудник', 'Сумма', 'Товары')
        self.tree = ttk.Treeview(self.top, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.load_orders()

    def load_orders(self):
        rows = execute_query("""
            SELECT o.order_id, o.order_date, 
                   e.last_name || ' ' || e.first_name as employee,
                   o.total_amount,
                   (SELECT string_agg(p.product_name || ' x' || oi.quantity, ', ')
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.product_id
                    WHERE oi.order_id = o.order_id) as items
            FROM orders o
            LEFT JOIN employees e ON o.employee_id = e.employee_id
            WHERE o.customer_id = :cust_id
            ORDER BY o.order_date DESC
        """, {"cust_id": self.customer_id})
        for r in rows:
            self.tree.insert('', tk.END,
                             values=(r['order_id'], r['order_date'], r['employee'], r['total_amount'], r['items']))


class NewOrderDialog:
    def __init__(self, parent, parent_window):
        self.parent_window = parent_window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Новый заказ")
        self.dialog.geometry("600x500")

        # Выбор клиента
        tk.Label(self.dialog, text="Клиент:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.customer_combo = ttk.Combobox(self.dialog, state='readonly')
        self.customer_combo.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.load_customers()

        # Выбор сотрудника
        tk.Label(self.dialog, text="Сотрудник:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.employee_combo = ttk.Combobox(self.dialog, state='readonly')
        self.employee_combo.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.load_employees()

        # Таблица для выбора товаров
        tk.Label(self.dialog, text="Товары:").grid(row=2, column=0, padx=5, pady=5, sticky='ne')

        frame_items = tk.Frame(self.dialog)
        frame_items.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky='nsew')

        self.product_listbox = tk.Listbox(frame_items, height=8, exportselection=False)
        self.product_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = tk.Scrollbar(frame_items, orient=tk.VERTICAL, command=self.product_listbox.yview)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.product_listbox.config(yscrollcommand=scroll.set)
        self.load_products()

        frame_qty = tk.Frame(self.dialog)
        frame_qty.grid(row=3, column=1, pady=5, sticky='w')
        tk.Label(frame_qty, text="Кол-во:").pack(side=tk.LEFT)
        self.qty_entry = tk.Entry(frame_qty, width=10)
        self.qty_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_qty, text="Добавить товар", command=self.add_item).pack(side=tk.LEFT)

        columns = ('Товар', 'Цена', 'Количество', 'Сумма')
        self.tree_items = ttk.Treeview(self.dialog, columns=columns, show='headings', height=5)
        for col in columns:
            self.tree_items.heading(col, text=col)
            self.tree_items.column(col, width=100)
        self.tree_items.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        tk.Button(self.dialog, text="Сохранить заказ", command=self.save_order).grid(row=5, column=0, columnspan=2,
                                                                                     pady=10)

        self.items = []  # список словарей {product_id, name, price, quantity}

    def load_customers(self):
        rows = execute_query("SELECT customer_id, last_name, first_name FROM customers ORDER BY last_name")
        self.customers = {f"{r['last_name']} {r['first_name']}": r['customer_id'] for r in rows}
        self.customer_combo['values'] = list(self.customers.keys())

    def load_employees(self):
        rows = execute_query("SELECT employee_id, last_name, first_name FROM employees ORDER BY last_name")
        self.employees = {f"{r['last_name']} {r['first_name']}": r['employee_id'] for r in rows}
        self.employee_combo['values'] = list(self.employees.keys())

    def load_products(self):
        rows = execute_query("SELECT product_id, product_name, price FROM products ORDER BY product_name")
        self.products = {f"{r['product_name']} ({r['price']} руб.)": {'id': r['product_id'], 'price': r['price']} for r
                         in rows}
        for name in self.products.keys():
            self.product_listbox.insert(tk.END, name)

    def add_item(self):
        selection = self.product_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар")
            return
        prod_name = self.product_listbox.get(selection[0])
        prod_data = self.products[prod_name]
        qty = self.qty_entry.get()
        if not qty.isdigit() or int(qty) <= 0:
            messagebox.showwarning("Предупреждение", "Введите корректное количество")
            return
        qty = int(qty)
        total = prod_data['price'] * qty
        self.tree_items.insert('', tk.END, values=(prod_name, prod_data['price'], qty, total))
        self.items.append({
            'product_id': prod_data['id'],
            'product_name': prod_name.split(' (')[0],
            'price': prod_data['price'],
            'quantity': qty
        })

    def save_order(self):
        if not self.customer_combo.get() or not self.employee_combo.get():
            messagebox.showwarning("Предупреждение", "Выберите клиента и сотрудника")
            return
        if not self.items:
            messagebox.showwarning("Предупреждение", "Добавьте хотя бы один товар")
            return

        cust_id = self.customers[self.customer_combo.get()]
        emp_id = self.employees[self.employee_combo.get()]

        items_json = [{"product_id": item['product_id'], "quantity": item['quantity']} for item in self.items]
        items_str = json.dumps(items_json)

        try:
            result = execute_query("SELECT add_order(:cust_id, :emp_id, :items::jsonb)",
                                   {"cust_id": cust_id, "emp_id": emp_id, "items": items_str})
            if result:
                messagebox.showinfo("Успех", f"Заказ №{result[0]['add_order']} создан")
                self.parent_window.load_orders()
                self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать заказ: {e}")


def open_window(parent):
    OrdersWindow(parent)