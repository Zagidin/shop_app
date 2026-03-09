import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="shop_parts",
    user="postgres",
    password="0505"
)
cur = conn.cursor()

# ---------- 1. Создание таблиц ----------
cur.execute("""
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    position VARCHAR(50),
    hire_date DATE DEFAULT CURRENT_DATE,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(100) UNIQUE,
    salary DECIMAL(10,2) CHECK (salary > 0)
)
""")

cur.execute("""
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
)
""")

cur.execute("""
CREATE TABLE equipment_types (
    equip_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(100) NOT NULL UNIQUE
)
""")

cur.execute("""
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT
)
""")

cur.execute("""
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category_id INTEGER REFERENCES categories(category_id) ON DELETE SET NULL,
    equip_type_id INTEGER REFERENCES equipment_types(equip_type_id) ON DELETE SET NULL,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    supplier_id INTEGER REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
    description TEXT
)
""")

cur.execute("""
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    discount DECIMAL(5,2) DEFAULT 0 CHECK (discount BETWEEN 0 AND 100)
)
""")

cur.execute("""
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE SET NULL,
    employee_id INTEGER REFERENCES employees(employee_id) ON DELETE SET NULL,
    total_amount DECIMAL(12,2) DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_at_sale DECIMAL(10,2) NOT NULL
)
""")

# ---------- 2. Вставка тестовых данных ----------
cur.executemany("INSERT INTO categories (category_name, description) VALUES (%s, %s)", [
    ('Двигатель', 'Детали двигателя'),
    ('Трансмиссия', 'КПП, сцепление, кардан'),
    ('Подвеска', 'Рессоры, амортизаторы'),
    ('Электрика', 'Генераторы, стартеры, проводка')
])

cur.executemany("INSERT INTO equipment_types (type_name) VALUES (%s)", [
    ('КАМАЗ',), ('МТЗ-80/82',), ('Кировец К-700',), ('Т-150',)
])

cur.executemany("INSERT INTO suppliers (supplier_name, contact_person, phone, email, address) VALUES (%s,%s,%s,%s,%s)",
                [
                    ('ООО "Автодеталь"', 'Иванов И.И.', '+7(999)123-45-67', 'info@avtodetal.ru',
                     'г. Москва, ул. Строителей, д.1'),
                    ('ЗАО "Трактороснаб"', 'Петров П.П.', '+7(999)234-56-78', 'sale@tractor.ru',
                     'г. Челябинск, пр. Ленина, д.10'),
                    ('ИП "Запчасть-Сервис"', 'Сидоров С.С.', '+7(999)345-67-89', 'sidorov@zapchas.ru',
                     'г. Новосибирск, ул. Промышленная, д.5')
                ])

cur.executemany("INSERT INTO customers (last_name, first_name, phone, email, discount) VALUES (%s,%s,%s,%s,%s)", [
    ('Сидоров', 'Алексей', '+7(900)111-22-33', 'sidorov@mail.ru', 0),
    ('Петрова', 'Мария', '+7(900)222-33-44', 'maria@yandex.ru', 5),
    ('Иванов', 'Дмитрий', '+7(900)333-44-55', 'dima@mail.ru', 0),
    ('Кузнецова', 'Елена', '+7(900)444-55-66', 'elena@bk.ru', 10)
])

cur.executemany(
    "INSERT INTO employees (last_name, first_name, position, phone, email, salary) VALUES (%s,%s,%s,%s,%s,%s)", [
        ('Смирнов', 'Иван', 'Продавец', '+7(911)111-11-11', 'ivan@shop.ru', 35000),
        ('Кузнецова', 'Ольга', 'Менеджер', '+7(911)222-22-22', 'olga@shop.ru', 45000),
        ('Попов', 'Андрей', 'Продавец', '+7(911)333-33-33', 'andrey@shop.ru', 35000)
    ])

cur.executemany("""
    INSERT INTO products (product_name, category_id, equip_type_id, price, stock_quantity, supplier_id, description)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
""", [
    ('Фильтр масляный', 1, 1, 350.00, 100, 1, 'Для КАМАЗ'),
    ('Стартер', 4, 2, 4500.00, 20, 2, 'Для МТЗ'),
    ('Рессора передняя', 3, 3, 5500.00, 15, 3, 'Для Кировец'),
    ('Тормозные колодки', 2, 1, 1200.00, 200, 1, 'Комплект для КАМАЗ'),
    ('Генератор', 4, 2, 3800.00, 10, 2, 'Для МТЗ'),
    ('Сцепление', 2, 3, 7200.00, 8, 3, 'Для Кировец'),
    ('Поршневая группа', 1, 1, 9500.00, 5, 1, 'Для КАМАЗ'),
    ('Аккумулятор', 4, 2, 6200.00, 12, 2, 'Для МТЗ'),
    ('Амортизатор', 3, 3, 2800.00, 25, 3, 'Для Кировец'),
    ('Фильтр воздушный', 1, 1, 450.00, 80, 1, 'Для КАМАЗ')
])

# Вставляем несколько заказов (чтобы были данные для тестов)
cur.execute("INSERT INTO orders (order_date, customer_id, employee_id) VALUES (NOW(), 1, 1) RETURNING order_id")
order1 = cur.fetchone()[0]
cur.execute("INSERT INTO orders (order_date, customer_id, employee_id) VALUES (NOW(), 2, 2) RETURNING order_id")
order2 = cur.fetchone()[0]
cur.execute("INSERT INTO orders (order_date, customer_id, employee_id) VALUES (NOW(), 3, 1) RETURNING order_id")
order3 = cur.fetchone()[0]

# Позиции для заказов
cur.executemany("INSERT INTO order_items (order_id, product_id, quantity, price_at_sale) VALUES (%s,%s,%s,%s)", [
    (order1, 1, 2, 350.00),
    (order1, 4, 1, 1200.00),
    (order2, 2, 1, 4500.00),
    (order2, 5, 2, 3800.00),
    (order3, 3, 1, 5500.00),
    (order3, 6, 1, 7200.00)
])

# ---------- 3. Хранимые процедуры (10 штук) ----------
# 1. add_order
cur.execute("""
CREATE OR REPLACE FUNCTION add_order(
    p_customer_id INTEGER,
    p_employee_id INTEGER,
    p_items JSONB
) RETURNS INTEGER AS $$
DECLARE
    new_order_id INTEGER;
    item RECORD;
    total DECIMAL(12,2) := 0;
    cur_price DECIMAL(10,2);
BEGIN
    INSERT INTO orders (customer_id, employee_id, order_date)
    VALUES (p_customer_id, p_employee_id, NOW())
    RETURNING order_id INTO new_order_id;

    FOR item IN SELECT * FROM jsonb_to_recordset(p_items) AS x(product_id INTEGER, quantity INTEGER)
    LOOP
        SELECT price INTO cur_price FROM products WHERE product_id = item.product_id;
        INSERT INTO order_items (order_id, product_id, quantity, price_at_sale)
        VALUES (new_order_id, item.product_id, item.quantity, cur_price);
        total := total + cur_price * item.quantity;
    END LOOP;

    UPDATE orders SET total_amount = total WHERE order_id = new_order_id;
    RETURN new_order_id;
END;
$$ LANGUAGE plpgsql;
""")

# 2. sales_report
cur.execute("""
CREATE OR REPLACE FUNCTION sales_report(start_date DATE, end_date DATE)
RETURNS TABLE(order_date DATE, total_orders BIGINT, total_sum NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT DATE(o.order_date)::DATE, COUNT(*), SUM(o.total_amount)
    FROM orders o
    WHERE DATE(o.order_date) BETWEEN start_date AND end_date
    GROUP BY DATE(o.order_date)
    ORDER BY DATE(o.order_date);
END;
$$ LANGUAGE plpgsql;
""")

# 3. top_products
cur.execute("""
CREATE OR REPLACE FUNCTION top_products(lim INTEGER DEFAULT 10)
RETURNS TABLE(product_name VARCHAR, total_quantity BIGINT, total_revenue NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT p.product_name, SUM(oi.quantity), SUM(oi.quantity * oi.price_at_sale)
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.product_id, p.product_name
    ORDER BY total_revenue DESC
    LIMIT lim;
END;
$$ LANGUAGE plpgsql;
""")

# 4. update_price (создадим таблицу логов, если нет)
cur.execute("""
CREATE TABLE IF NOT EXISTS price_log (
    log_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    change_date TIMESTAMP DEFAULT NOW(),
    changed_by VARCHAR(50)
);
""")
cur.execute("""
CREATE OR REPLACE FUNCTION update_price(
    p_product_id INTEGER,
    p_new_price DECIMAL(10,2),
    p_user VARCHAR
) RETURNS VOID AS $$
DECLARE
    old_price DECIMAL(10,2);
BEGIN
    SELECT price INTO old_price FROM products WHERE product_id = p_product_id;
    UPDATE products SET price = p_new_price WHERE product_id = p_product_id;
    INSERT INTO price_log (product_id, old_price, new_price, changed_by)
    VALUES (p_product_id, old_price, p_new_price, p_user);
END;
$$ LANGUAGE plpgsql;
""")

# 5. stock_by_category
cur.execute("""
CREATE OR REPLACE FUNCTION stock_by_category(p_cat_id INTEGER DEFAULT NULL)
RETURNS TABLE(category_name VARCHAR, product_name VARCHAR, stock INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT c.category_name, p.product_name, p.stock_quantity
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.category_id
    WHERE (p_cat_id IS NULL OR p.category_id = p_cat_id)
    ORDER BY c.category_name, p.product_name;
END;
$$ LANGUAGE plpgsql;
""")

# 6. customer_orders
cur.execute("""
CREATE OR REPLACE FUNCTION customer_orders(p_customer_id INTEGER)
RETURNS TABLE(order_id INTEGER, order_date TIMESTAMP, employee_name VARCHAR, total_amount NUMERIC, items TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT o.order_id, o.order_date,
           e.last_name || ' ' || e.first_name,
           o.total_amount,
           (SELECT string_agg(p.product_name || ' x' || oi.quantity, '; ')
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = o.order_id) as items
    FROM orders o
    LEFT JOIN employees e ON o.employee_id = e.employee_id
    WHERE o.customer_id = p_customer_id
    ORDER BY o.order_date DESC;
END;
$$ LANGUAGE plpgsql;
""")

# 7. avg_check_by_month
cur.execute("""
CREATE OR REPLACE FUNCTION avg_check_by_month()
RETURNS TABLE(year INTEGER, month INTEGER, avg_check NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT EXTRACT(YEAR FROM order_date)::INTEGER,
           EXTRACT(MONTH FROM order_date)::INTEGER,
           AVG(total_amount)
    FROM orders
    GROUP BY 1, 2
    ORDER BY 1, 2;
END;
$$ LANGUAGE plpgsql;
""")

# 8. low_stock
cur.execute("""
CREATE OR REPLACE FUNCTION low_stock(threshold INTEGER DEFAULT 10)
RETURNS TABLE(product_name VARCHAR, stock_quantity INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT p.product_name, p.stock_quantity
    FROM products p
    WHERE p.stock_quantity < threshold
    ORDER BY p.stock_quantity;
END;
$$ LANGUAGE plpgsql;
""")

# 9. supplier_revenue
cur.execute("""
CREATE OR REPLACE FUNCTION supplier_revenue(start_date DATE, end_date DATE)
RETURNS TABLE(supplier_name VARCHAR, total_revenue NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT s.supplier_name, COALESCE(SUM(oi.quantity * oi.price_at_sale), 0)
    FROM suppliers s
    LEFT JOIN products p ON s.supplier_id = p.supplier_id
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id
        AND DATE(o.order_date) BETWEEN start_date AND end_date
    GROUP BY s.supplier_name
    ORDER BY total_revenue DESC;
END;
$$ LANGUAGE plpgsql;
""")

# 10. search_parts
cur.execute("""
CREATE OR REPLACE FUNCTION search_parts(search_text VARCHAR)
RETURNS TABLE(product_name VARCHAR, category_name VARCHAR, equip_type VARCHAR, price DECIMAL, supplier_name VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT p.product_name, c.category_name, et.type_name,
           p.price, s.supplier_name
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.category_id
    LEFT JOIN equipment_types et ON p.equip_type_id = et.equip_type_id
    LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
    WHERE p.product_name ILIKE '%' || search_text || '%'
       OR p.description ILIKE '%' || search_text || '%';
END;
$$ LANGUAGE plpgsql;
""")

# ---------- 4. Триггеры (7 штук) ----------
# 1. decrease_stock
cur.execute("""
CREATE OR REPLACE FUNCTION decrease_stock()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""")
cur.execute("""
CREATE TRIGGER trg_decrease_stock
AFTER INSERT ON order_items
FOR EACH ROW
EXECUTE FUNCTION decrease_stock();
""")

# 2. increase_stock
cur.execute("""
CREATE OR REPLACE FUNCTION increase_stock()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products SET stock_quantity = stock_quantity + OLD.quantity
    WHERE product_id = OLD.product_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
""")
cur.execute("""
CREATE TRIGGER trg_increase_stock
AFTER DELETE ON order_items
FOR EACH ROW
EXECUTE FUNCTION increase_stock();
""")

# 3. adjust_stock_on_update
cur.execute("""
CREATE OR REPLACE FUNCTION adjust_stock_on_update()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products SET stock_quantity = stock_quantity + OLD.quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""")
cur.execute("""
CREATE TRIGGER trg_adjust_stock
AFTER UPDATE OF quantity ON order_items
FOR EACH ROW
EXECUTE FUNCTION adjust_stock_on_update();
""")

# 4. update_order_total (триггер на вставку, обновление, удаление)
cur.execute("""
CREATE OR REPLACE FUNCTION update_order_total()
RETURNS TRIGGER AS $$
DECLARE
    order_total DECIMAL(12,2);
BEGIN
    SELECT SUM(quantity * price_at_sale) INTO order_total
    FROM order_items
    WHERE order_id = COALESCE(NEW.order_id, OLD.order_id);

    UPDATE orders SET total_amount = order_total
    WHERE order_id = COALESCE(NEW.order_id, OLD.order_id);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
""")
cur.execute("""
CREATE TRIGGER trg_update_total_after_insert
AFTER INSERT ON order_items
FOR EACH ROW
EXECUTE FUNCTION update_order_total();
""")
cur.execute("""
CREATE TRIGGER trg_update_total_after_update
AFTER UPDATE ON order_items
FOR EACH ROW
EXECUTE FUNCTION update_order_total();
""")
cur.execute("""
CREATE TRIGGER trg_update_total_after_delete
AFTER DELETE ON order_items
FOR EACH ROW
EXECUTE FUNCTION update_order_total();
""")

# 5. check_price (BEFORE INSERT OR UPDATE)
cur.execute("""
CREATE OR REPLACE FUNCTION check_price()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.price < 0 THEN
        RAISE EXCEPTION 'Цена не может быть отрицательной';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""")
cur.execute("""
CREATE TRIGGER trg_check_price
BEFORE INSERT OR UPDATE ON products
FOR EACH ROW
EXECUTE FUNCTION check_price();
""")

# 6. log_price_change
cur.execute("""
CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.price != NEW.price THEN
        INSERT INTO price_log (product_id, old_price, new_price, changed_by)
        VALUES (NEW.product_id, OLD.price, NEW.price, CURRENT_USER);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""")
cur.execute("""
CREATE TRIGGER trg_log_price
AFTER UPDATE OF price ON products
FOR EACH ROW
EXECUTE FUNCTION log_price_change();
""")

# 7. set_order_date
cur.execute("""
CREATE OR REPLACE FUNCTION set_order_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.order_date IS NULL THEN
        NEW.order_date = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""")
cur.execute("""
CREATE TRIGGER trg_set_order_date
BEFORE INSERT ON orders
FOR EACH ROW
EXECUTE FUNCTION set_order_date();
""")

# ---------- 5. Генераторы (последовательности) ----------
cur.execute("CREATE SEQUENCE IF NOT EXISTS seq_employees START 1000")
cur.execute("CREATE SEQUENCE IF NOT EXISTS seq_products START 5000")
cur.execute("CREATE SEQUENCE IF NOT EXISTS seq_customers START 10000")
cur.execute("CREATE SEQUENCE IF NOT EXISTS seq_orders START 20000")
cur.execute("CREATE SEQUENCE IF NOT EXISTS seq_order_items START 50000")

# ---------- 6. Оконные функции (для отчёта, необязательно выполнять) ----------
# Но можно просто оставить как запросы, которые потом покажем в отчёте

conn.commit()
cur.close()
conn.close()

print("База данных полностью инициализирована: таблицы, данные, процедуры, триггеры, последовательности.")