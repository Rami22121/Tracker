import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import datetime

texts_en = {
    "title": "Personal Expense Tracker",
    "add_expense": "Add Expense",
    "amount": "Amount",
    "category": "Category",
    "date": "Date",
    "2penses": "View Expenses",
    "update_expense": "Update Expense",
    "delete_expense": "Delete Expense",
    "summary": "Summary",
    "submit": "Submit",
    "invalid_amount": "Invalid amount entered.",
    "invalid_category": "Category cannot be empty.",
    "view_expenses": "View Expenses",
    "invalid_date": "Invalid date format.",
    "enter_expense_id": "Enter Expense ID:",
    "edit_expense": "Edit Expense",
    "error": "Error",
    "expense_not_found": "Expense not found",
    "success": "Success",
    "expense_updated": "Expense updated successfully.",
    "expense_deleted": "Expense deleted successfully."

}

texts_es = {
    "title": "Controlador de Gastos Personales",
    "add_expense": "Agregar Gasto",
    "amount": "Cantidad",
    "category": "Categoría",
    "date": "Fecha",
    "view_expenses": "Ver Gastos",
    "update_expense": "Actualizar Gasto",
    "delete_expense": "Eliminar Gasto",
    "summary": "Resumen",
    "submit": "Enviar",
    "invalid_amount": "Cantidad ingresada inválida.",
    "invalid_category": "La categoría no puede estar vacía.",
    "view_expenses": "Ver Gastos",
    "invalid_date": "Formato de fecha inválido.",
    "enter_expense_id": "Ingrese el ID del gasto:",
    "edit_expense": "Editar Gasto",
    "error": "Error",
    "expense_not_found": "Gasto no encontrado",
    "success": "Éxito",
    "expense_updated": "Gasto actualizado con éxito.",
    "expense_deleted": "Gasto eliminado con éxito."
}
texts_en.update({
    "delete": "Delete",
    "total_expense": "Total Expense",
    "average_expense": "Average Expense",
    "expenses_by_category": "Expenses by Category"
})

texts_es.update({
    "delete": "Eliminar",
    "total_expense": "Gasto Total",
    "average_expense": "Gasto Promedio",
    "expenses_by_category": "Gastos por Categoría"
})


def is_valid_amount(amount):
    try:
        return float(amount) > 0
    except ValueError:
        return False

def is_valid_category(category):
    return len(category.strip()) > 0

def is_valid_date(date, language):
    date_format = '%Y-%m-%d' if language == 'English' else '%d/%m/%Y'
    try:
        datetime.datetime.strptime(date, date_format)
        return True
    except ValueError:
        return False


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
    except sqlite3.Error as e:
        print(e)

def add_expense_to_database(amount, category, date):
    conn = create_connection("expenses.db")
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)", (amount, category, date))
            conn.commit()
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()

def initialize_database():
    conn = create_connection("expenses.db")
    if conn:
        create_table(conn)
        conn.close()

initialize_database()


def fetch_expenses():
    conn = create_connection("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, category, date FROM expenses")
    rows = cursor.fetchall()
    conn.close()
    return rows

def view_expenses(texts):
    view_window = tk.Toplevel()
    view_window.title(texts["view_expenses"])

    tree = ttk.Treeview(view_window, columns=("ID", texts["amount"], texts["category"], texts["date"]), show="headings")
    for col in ("ID", texts["amount"], texts["category"], texts["date"]):
        tree.heading(col, text=col)
    tree.pack(fill='both', expand=True)

    for expense in fetch_expenses():
        tree.insert("", "end", values=expense)


def choose_expense_to_update(language, texts):
    update_window = tk.Toplevel()
    update_window.title(texts["update_expense"])

    ttk.Label(update_window, text=texts["enter_expense_id"]).pack()
    expense_id_entry = ttk.Entry(update_window)
    expense_id_entry.pack()

    def on_submit():
        expense_id = expense_id_entry.get()
        update_expense_details(expense_id, language, texts)

    submit_button = ttk.Button(update_window, text=texts["submit"], command=on_submit)
    submit_button.pack()

def update_expense_details(expense_id, language, texts):
    conn = create_connection("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    expense = cursor.fetchone()
    conn.close()

    if expense:
        edit_window = tk.Toplevel()
        edit_window.title(texts["edit_expense"])

        ttk.Label(edit_window, text=texts["amount"]).pack()
        amount_entry = ttk.Entry(edit_window)
        amount_entry.insert(0, expense[1])
        amount_entry.pack()

        ttk.Label(edit_window, text=texts["category"]).pack()
        category_entry = ttk.Entry(edit_window)
        category_entry.insert(0, expense[2])
        category_entry.pack()

        ttk.Label(edit_window, text=texts["date"]).pack()
        date_entry = ttk.Entry(edit_window)
        date_entry.insert(0, expense[3])
        date_entry.pack()

        def on_update():
            new_amount = amount_entry.get()
            new_category = category_entry.get()
            new_date = date_entry.get()

            if not is_valid_amount(new_amount):
                messagebox.showerror(texts["error"], texts["invalid_amount"])
                return
            if not is_valid_category(new_category):
                messagebox.showerror(texts["error"], texts["invalid_category"])
                return
            if not is_valid_date(new_date, language):
                messagebox.showerror(texts["error"], texts["invalid_date"])
                return

            conn = create_connection("expenses.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE expenses SET amount = ?, category = ?, date = ? WHERE id = ?",
                           (new_amount, new_category, new_date, expense_id))
            conn.commit()
            conn.close()
            messagebox.showinfo(texts["success"], texts["expense_updated"])
            edit_window.destroy()

        update_button = ttk.Button(edit_window, text=texts["submit"], command=on_update)
        update_button.pack()
    else:
        messagebox.showerror(texts["error"], texts["expense_not_found"])


def choose_expense_to_delete(language, texts):
    delete_window = tk.Toplevel()
    delete_window.title(texts["delete_expense"])

    ttk.Label(delete_window, text=texts["enter_expense_id"]).pack()
    expense_id_entry = ttk.Entry(delete_window)
    expense_id_entry.pack()

    def on_delete():
        expense_id = expense_id_entry.get()

        if not expense_id.isdigit():
            messagebox.showerror(texts["error"], texts["invalid_amount"])
            return

        conn = create_connection("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
        if not cursor.fetchone():
            conn.close()
            messagebox.showerror(texts["error"], texts["expense_not_found"])
            return
        conn.close()

        delete_expense(expense_id)
        messagebox.showinfo(texts["success"], texts["expense_deleted"])
        delete_window.destroy()

    delete_button = ttk.Button(delete_window, text=texts["delete"], command=on_delete)
    delete_button.pack()

def delete_expense(expense_id):
    conn = create_connection("expenses.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def calculate_expense_summary():
    conn = create_connection("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT amount, category FROM expenses")
    expenses = cursor.fetchall()
    conn.close()

    total_expense = sum([expense[0] for expense in expenses])
    average_expense = total_expense / len(expenses) if expenses else 0

    expenses_by_category = {}
    for amount, category in expenses:
        expenses_by_category[category] = expenses_by_category.get(category, 0) + amount

    return total_expense, average_expense, expenses_by_category

def show_summary(texts):
    total, average, by_category = calculate_expense_summary()
    summary_window = tk.Toplevel()
    summary_window.title(texts["summary"])

    ttk.Label(summary_window, text=f"{texts['total_expense']}: {total:.2f}").pack()
    ttk.Label(summary_window, text=f"{texts['average_expense']}: {average:.2f}").pack()

    ttk.Label(summary_window, text=texts["expenses_by_category"]).pack()
    for category, amount in by_category.items():
        ttk.Label(summary_window, text=f"{category}: {amount:.2f}").pack()


def open_add_expense_window(texts, language):
    window = tk.Toplevel()
    window.title(texts["add_expense"])

    ttk.Label(window, text=texts["amount"]).pack()
    amount_entry = ttk.Entry(window)
    amount_entry.pack()

    ttk.Label(window, text=texts["category"]).pack()
    category_entry = ttk.Entry(window)
    category_entry.pack()

    ttk.Label(window, text=texts["date"]).pack()
    date_entry = ttk.Entry(window)
    date_entry.pack()

    def on_submit():
        amount = amount_entry.get()
        category = category_entry.get()
        date = date_entry.get()

        if not is_valid_amount(amount):
            messagebox.showerror("Validation Error", texts["invalid_amount"])
            return
        if not is_valid_category(category):
            messagebox.showerror("Validation Error", texts["invalid_category"])
            return
        if not is_valid_date(date, language):
            messagebox.showerror("Validation Error", texts["invalid_date"])
            return

        add_expense_to_database(amount, category, date)
        window.destroy()
        messagebox.showinfo("Success", texts["submit"])

    submit_button = ttk.Button(window, text=texts["submit"], command=on_submit)
    submit_button.pack()

def create_main_window() -> object:
    language = simpledialog.askstring("Language", "Choose a language: English or Spanish")
    texts = texts_en if language == "English" else texts_es

    root = tk.Tk()
    root.title(texts["title"])
    root.geometry("300x400")

    ttk.Button(root, text=texts["add_expense"], command=lambda: open_add_expense_window(texts, language)).pack(expand=True)
    ttk.Button(root, text=texts["view_expenses"], command=lambda: view_expenses(texts)).pack(expand=True)
    ttk.Button(root, text=texts["update_expense"], command=lambda: choose_expense_to_update(language, texts)).pack(expand=True)
    ttk.Button(root, text=texts["delete_expense"], command=lambda: choose_expense_to_delete(language, texts)).pack(expand=True)
    ttk.Button(root, text=texts["summary"], command=lambda: show_summary(texts)).pack(expand=True)

    return root


root = create_main_window()
root.mainloop()

