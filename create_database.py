"""
create_database.py
Creates a sample SQLite database (company.db) with a few related tables
and populates them with sample data. This is the DB that natural language
queries will be converted into SQL against.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "company.db")


def create_database():
    # Start fresh every time this script is run
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ---------- Schema ----------
    cursor.executescript(
        """
        CREATE TABLE departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT NOT NULL,
            location TEXT
        );

        CREATE TABLE employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            department_id INTEGER,
            salary REAL,
            hire_date TEXT,
            email TEXT,
            FOREIGN KEY (department_id) REFERENCES departments(department_id)
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT,
            price REAL
        );

        CREATE TABLE sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            sale_date TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
        """
    )

    # ---------- Sample data ----------
    departments = [
        ("Sales", "New York"),
        ("Engineering", "San Francisco"),
        ("Marketing", "Chicago"),
        ("Human Resources", "Austin"),
        ("Finance", "Boston"),
    ]
    cursor.executemany(
        "INSERT INTO departments (department_name, location) VALUES (?, ?)",
        departments,
    )

    employees = [
        ("Alice", "Johnson", 1, 65000, "2021-03-15", "alice.johnson@company.com"),
        ("Bob", "Smith", 2, 95000, "2019-07-01", "bob.smith@company.com"),
        ("Carol", "Williams", 2, 105000, "2018-01-10", "carol.williams@company.com"),
        ("David", "Brown", 3, 58000, "2022-05-20", "david.brown@company.com"),
        ("Eva", "Davis", 1, 72000, "2020-11-11", "eva.davis@company.com"),
        ("Frank", "Miller", 4, 61000, "2021-09-01", "frank.miller@company.com"),
        ("Grace", "Wilson", 5, 88000, "2017-02-25", "grace.wilson@company.com"),
        ("Henry", "Moore", 2, 99000, "2020-06-30", "henry.moore@company.com"),
        ("Ivy", "Taylor", 3, 54000, "2023-01-15", "ivy.taylor@company.com"),
        ("Jack", "Anderson", 1, 69000, "2019-12-05", "jack.anderson@company.com"),
    ]
    cursor.executemany(
        """INSERT INTO employees
           (first_name, last_name, department_id, salary, hire_date, email)
           VALUES (?, ?, ?, ?, ?, ?)""",
        employees,
    )

    products = [
        ("Laptop Pro 15", "Electronics", 1299.99),
        ("Wireless Mouse", "Electronics", 24.99),
        ("Office Chair", "Furniture", 189.50),
        ("Standing Desk", "Furniture", 349.00),
        ("Notebook Set", "Stationery", 9.99),
        ("4K Monitor", "Electronics", 399.00),
        ("Desk Lamp", "Furniture", 29.99),
        ("Mechanical Keyboard", "Electronics", 89.99),
    ]
    cursor.executemany(
        "INSERT INTO products (product_name, category, price) VALUES (?, ?, ?)",
        products,
    )

    sales = [
        (1, 1, 2, "2024-01-10"),
        (1, 2, 5, "2024-01-12"),
        (5, 3, 1, "2024-02-01"),
        (9, 5, 10, "2024-02-05"),
        (1, 6, 3, "2024-02-15"),
        (5, 4, 2, "2024-03-01"),
        (9, 8, 4, "2024-03-10"),
        (1, 7, 6, "2024-03-20"),
        (5, 1, 1, "2024-04-02"),
        (9, 2, 8, "2024-04-15"),
    ]
    cursor.executemany(
        """INSERT INTO sales (employee_id, product_id, quantity, sale_date)
           VALUES (?, ?, ?, ?)""",
        sales,
    )

    conn.commit()
    conn.close()
    print(f"Database created at: {DB_PATH}")


if __name__ == "__main__":
    create_database()
