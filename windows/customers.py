import tkinter as tk
from db import execute_query
from tkinter import ttk, messagebox
from import_utils import import_excel_to_table


class CustomersWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Клиенты")
        self.top.geometry("800x500")

        # Таблица
        columns = ('ID', 'Фамилия', 'Имя', 'Телефон', 'Email', 'Скидка %')
        self.tree = ttk.Treeview(self.top, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопки
        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Добавить", command=self.add_customer).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Изменить", command=self.edit_customer).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_customer).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Показать заказы клиента", command=self.show_orders).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Импорт из Excel", command=self.import_from_excel).pack(side=tk.LEFT, padx=5)

        self.load_data()

    def import_from_excel(self):
        from tkinter import filedialog, messagebox
        file_path = filedialog.askopenfilename(
            title="Выберите файл Excel",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not file_path:
            return
        try:
            columns = ['last_name', 'first_name', 'phone', 'email', 'discount']
            import_excel_to_table(file_path, 'customers', columns)
            messagebox.showinfo("Успех", "Данные импортированы")
            self.load_data()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = execute_query(
            "SELECT customer_id, last_name, first_name, phone, email, discount FROM customers ORDER BY customer_id")
        print("Данные из БД:", rows)
        for r in rows:
            self.tree.insert('', tk.END, values=(
            r['customer_id'], r['last_name'], r['first_name'], r['phone'], r['email'], r['discount']))

    def add_customer(self):
        AddEditCustomerDialog(self.top, self, mode='add')

    def edit_customer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите клиента")
            return
        item = self.tree.item(selected[0])
        cust_id = item['values'][0]
        AddEditCustomerDialog(self.top, self, mode='edit', cust_id=cust_id)

    def delete_customer(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите клиента")
            return
        item = self.tree.item(selected[0])
        cust_id = item['values'][0]
        if messagebox.askyesno("Подтверждение", "Удалить клиента?"):
            execute_query("DELETE FROM customers WHERE customer_id = :id", {"id": cust_id})
            self.load_data()

    def show_orders(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите клиента")
            return
        item = self.tree.item(selected[0])
        cust_id = item['values'][0]
        from windows.orders import CustomerOrdersWindow
        CustomerOrdersWindow(self.top, cust_id)


class AddEditCustomerDialog:
    def __init__(self, parent, parent_window, mode='add', cust_id=None):
        self.parent_window = parent_window
        self.cust_id = cust_id
        self.mode = mode
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить клиента" if mode == 'add' else "Редактировать клиента")

        fields = ['Фамилия', 'Имя', 'Телефон', 'Email', 'Скидка %']
        self.entries = {}
        for i, field in enumerate(fields):
            tk.Label(self.dialog, text=field).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = tk.Entry(self.dialog)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[field] = entry

        if mode == 'edit' and cust_id:
            row = execute_query("SELECT * FROM customers WHERE customer_id = :id", {"id": cust_id})[0]
            self.entries['Фамилия'].insert(0, row['last_name'])
            self.entries['Имя'].insert(0, row['first_name'])
            self.entries['Телефон'].insert(0, row['phone'] or '')
            self.entries['Email'].insert(0, row['email'] or '')
            self.entries['Скидка %'].insert(0, row['discount'])

        btn_frame = tk.Frame(self.dialog)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save(self):
        data = {
            'last_name': self.entries['Фамилия'].get(),
            'first_name': self.entries['Имя'].get(),
            'phone': self.entries['Телефон'].get(),
            'email': self.entries['Email'].get(),
            'discount': float(self.entries['Скидка %'].get() or 0)
        }
        if self.mode == 'add':
            execute_query("""
                INSERT INTO customers (last_name, first_name, phone, email, discount)
                VALUES (:last_name, :first_name, :phone, :email, :discount)
            """, data)
        else:
            data['id'] = self.cust_id
            execute_query("""
                UPDATE customers SET last_name=:last_name, first_name=:first_name,
                    phone=:phone, email=:email, discount=:discount
                WHERE customer_id = :id
            """, data)
        self.parent_window.load_data()
        self.dialog.destroy()


def open_window(parent):
    CustomersWindow(parent)