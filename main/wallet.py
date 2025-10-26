import tkinter as tk
from tkinter import messagebox
import json
import os
from tkinter import ttk
from datetime import datetime

class Transaction:
    def __init__(self, category, amount, transaction_type, description="No description"):
        self.category = category
        self.amount = float(amount)
        self.transaction_type = transaction_type
        self.description = description
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            'category': self.category,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'date': self.date
        }

class Wallet:
    def __init__(self, file_name="wallet_data.json"):
        self.file_name = file_name
        self.transactions = []
        self.balance = 0.0
        self.load_data()

    def add_transaction(self, category, amount, transaction_type, description):
        new_transaction = Transaction(category, amount, transaction_type, description)
        self.transactions.append(new_transaction)
        self.update_balance(transaction_type, amount)
        self.save_data()

    def update_balance(self, transaction_type, amount):
        if transaction_type == "Income":
            self.balance += amount
        else:
            self.balance -= amount

    def save_data(self):
        # Ensure the data is saved in the JSON file correctly
        data = {'transactions': [transaction.to_dict() for transaction in self.transactions], 'balance': self.balance}
        with open(self.file_name, "w") as file:
            json.dump(data, file, indent=4)

    def load_data(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r") as file:
                data = json.load(file)
                self.transactions = [Transaction(t['category'], t['amount'], t['transaction_type'], t['description']) for t in data['transactions']]
                self.balance = data['balance']

class WalletApp:
    def __init__(self, root, wallet):
        self.root = root
        self.wallet = wallet
        self.root.title("Personal Wallet - Basic Version")

        # Set the window size and position
        self.root.geometry("1200x600")

        # Set up the header with current balance (center aligned)
        self.header_label = tk.Label(root, text=f"Current Balance: ${self.wallet.balance:.2f}", font=("Helvetica", 18), bg="darkgreen", fg="white", height=2)
        self.header_label.pack(fill="x", pady=10)

        # Add Transaction section (center aligned)
        self.transaction_frame = tk.Frame(root)
        self.transaction_frame.pack(pady=20)

        self.amount_label = tk.Label(self.transaction_frame, text="Amount:", font=("Helvetica", 12))
        self.amount_label.grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(self.transaction_frame, font=("Helvetica", 12))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        self.type_label = tk.Label(self.transaction_frame, text="Type:", font=("Helvetica", 12))
        self.type_label.grid(row=1, column=0, padx=5, pady=5)
        self.type_var = tk.StringVar(value="Income")
        self.type_dropdown = ttk.Combobox(self.transaction_frame, textvariable=self.type_var, values=["Income", "Expense"], font=("Helvetica", 12))
        self.type_dropdown.grid(row=1, column=1, padx=5, pady=5)

        self.category_label = tk.Label(self.transaction_frame, text="Category:", font=("Helvetica", 12))
        self.category_label.grid(row=2, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar(value="Salary")
        self.category_dropdown = ttk.Combobox(self.transaction_frame, textvariable=self.category_var, values=["Salary", "Entertainment", "Food", "Utilities", "Other"], font=("Helvetica", 12))
        self.category_dropdown.grid(row=2, column=1, padx=5, pady=5)

        self.description_label = tk.Label(self.transaction_frame, text="Description:", font=("Helvetica", 12))
        self.description_label.grid(row=3, column=0, padx=5, pady=5)
        self.description_entry = tk.Entry(self.transaction_frame, font=("Helvetica", 12))
        self.description_entry.grid(row=3, column=1, padx=5, pady=5)

        self.add_income_button = tk.Button(self.transaction_frame, text="Add Income", bg="green", fg="white", command=self.add_income, font=("Helvetica", 12), width=15)
        self.add_income_button.grid(row=4, column=0, padx=5, pady=5)

        self.add_expense_button = tk.Button(self.transaction_frame, text="Add Expense", bg="red", fg="white", command=self.add_expense, font=("Helvetica", 12), width=15)
        self.add_expense_button.grid(row=4, column=1, padx=5, pady=5)

        self.clear_button = tk.Button(self.transaction_frame, text="Clear Form", command=self.clear_form, font=("Helvetica", 12), width=15)
        self.clear_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Transaction History section (center aligned)
        self.history_frame = tk.Frame(root)
        self.history_frame.pack(pady=10)

        self.history_label = tk.Label(self.history_frame, text="Transaction History", font=("Helvetica", 14))
        self.history_label.grid(row=0, column=0, padx=5, pady=5)

        self.history_tree = ttk.Treeview(self.history_frame, columns=("Index", "Amount", "Type", "Category", "Description", "Date"), show="headings", height=8)
        self.history_tree.grid(row=1, column=0, padx=5, pady=5)

        self.history_tree.heading("Index", text="#")
        self.history_tree.heading("Amount", text="Amount")
        self.history_tree.heading("Type", text="Type")
        self.history_tree.heading("Category", text="Category")
        self.history_tree.heading("Description", text="Description")
        self.history_tree.heading("Date", text="Date")

        self.update_history()

    def add_income(self):
        amount = self.amount_entry.get()
        category = self.category_var.get()
        description = self.description_entry.get()

        if not amount:
            messagebox.showerror("Error", "Please enter an amount")
            return

        try:
            # Check if the amount is a valid float
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the amount")
            return

        # Add transaction
        self.wallet.add_transaction(category, amount, "Income", description)
        self.update_balance_label()
        self.update_history()
        self.clear_form()

    def add_expense(self):
        amount = self.amount_entry.get()
        category = self.category_var.get()
        description = self.description_entry.get()

        if not amount:
            messagebox.showerror("Error", "Please enter an amount")
            return

        try:
            # Check if the amount is a valid float
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the amount")
            return

        # Add transaction
        self.wallet.add_transaction(category, amount, "Expense", description)
        self.update_balance_label()
        self.update_history()
        self.clear_form()

    def clear_form(self):
        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

    def update_balance_label(self):
        self.header_label.config(text=f"Current Balance: ${self.wallet.balance:.2f}")

    def update_history(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        for idx, transaction in enumerate(self.wallet.transactions):
            self.history_tree.insert("", "end", values=(idx + 1, f"${transaction.amount:.2f}", transaction.transaction_type, transaction.category, transaction.description, transaction.date))

if __name__ == "__main__":
    wallet = Wallet()  # Load the wallet data from the file when starting
    root = tk.Tk()
    app = WalletApp(root, wallet)
    root.mainloop()
