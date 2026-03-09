import tkinter as tk
from windows import customers, products, orders, reports


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Магазин запчастей для тяжёлой техники")
        self.root.geometry("600x400")

        tk.Label(root, text="Информационная система магазина запчастей", font=("Arial", 16)).pack(pady=20)

        tk.Button(root, text="Клиенты", command=self.open_customers, width=30, height=2).pack(pady=5)
        tk.Button(root, text="Товары", command=self.open_products, width=30, height=2).pack(pady=5)
        tk.Button(root, text="Заказы", command=self.open_orders, width=30, height=2).pack(pady=5)
        tk.Button(root, text="Отчёты и процедуры", command=self.open_reports, width=30, height=2).pack(pady=5)
        tk.Button(root, text="Выход", command=root.quit, width=30, height=2).pack(pady=20)

    def open_customers(self):
        customers.open_window(self.root)

    def open_products(self):
        products.open_window(self.root)

    def open_orders(self):
        orders.open_window(self.root)

    def open_reports(self):
        reports.open_window(self.root)


if __name__ == "__main__":
    root = tk.Tk()
    from tkinter import font

    default_font = font.nametofont('TkDefaultFont')
    default_font.configure(family='Segoe UI', size=10)
    app = MainApp(root)
    root.mainloop()