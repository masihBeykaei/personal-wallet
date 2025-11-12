import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from datetime import datetime, timedelta
import json
from pathlib import Path

# ---------- Helpers: per-user data folder ----------
def app_data_dir() -> Path:
    # e.g., C:\Users\<you>\AdvancedWallet  (Windows)
    base = Path.home() / "AdvancedWallet"
    base.mkdir(parents=True, exist_ok=True)
    return base

def data_path(name: str) -> Path:
    return app_data_dir() / name

# ---------- App ----------
class AdvancedWallet:
        

    def on_close(self):
        # Stop Tk timers/events first
        try:
            # Destroy the canvas widget if it exists
            if hasattr(self, "canvas"):
                self.canvas.get_tk_widget().destroy()
        except Exception:
            pass

        # Close matplotlib figures so no timer threads linger
        try:
            if hasattr(self, "fig"):
                plt.close(self.fig)
            plt.close('all')
        except Exception:
            pass

        # Properly end Tk
        try:
            self.window.quit()
        except Exception:
            pass
        try:
            self.window.destroy()
        except Exception:
            pass

        # As a last resort, ensure the interpreter exits
        sys.exit(0)

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Personal Wallet - Advanced Version")
        self.window.geometry("800x600")

        self.transactions = []
        self.monthly_budget = 0.0
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Load persisted state BEFORE building UI so values show up immediately
        self.load_data()
        self.load_budget()

        self.setup_ui()

    def setup_ui(self):
        # Balance Display
        self.balance_frame = tk.Frame(self.window, bg="#2c3e50")
        self.balance_frame.pack(fill="x")
        tk.Label(self.balance_frame, text="Current Balance: $", fg="white", bg="#2c3e50").pack(side="left")
        self.balance_var = tk.StringVar(value="$0.00")
        tk.Label(
            self.balance_frame,
            textvariable=self.balance_var,
            fg="#27ae60",
            bg="#2c3e50",
            font=("Arial", 12, "bold")
        ).pack(side="left")
        tk.Button(self.balance_frame, text="Export CSV", command=self.export_to_csv).pack(side="right", padx=5)

        # Tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(expand=True, fill="both", pady=10)

        # Transactions Tab
        self.transactions_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.setup_transactions_tab()

        # Analytics Tab
        self.analytics_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_tab, text="Analytics")
        self.setup_analytics_tab()

        # Budget Tab
        self.budget_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.budget_tab, text="Budget")
        self.setup_budget_tab()

        # Search Tab
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Search")
        self.setup_search_tab()

        self.update_display()

    def setup_transactions_tab(self):
        form_frame = tk.Frame(self.transactions_tab)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Amount:").grid(row=0, column=0, sticky="e")
        self.amount_entry = tk.Entry(form_frame)
        self.amount_entry.grid(row=0, column=1, padx=4, pady=2)

        tk.Label(form_frame, text="Type:").grid(row=1, column=0, sticky="e")
        self.type_var = tk.StringVar(value="expense")
        tk.OptionMenu(form_frame, self.type_var, "income", "expense").grid(row=1, column=1, padx=4, pady=2, sticky="we")

        tk.Label(form_frame, text="Category:").grid(row=2, column=0, sticky="e")
        self.category_var = tk.StringVar(value="Food")
        tk.OptionMenu(
            form_frame, self.category_var, "Food", "Entertainment", "Healthcare", "Shopping", "Bills", "Salary"
        ).grid(row=2, column=1, padx=4, pady=2, sticky="we")

        tk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky="e")
        self.desc_entry = tk.Entry(form_frame)
        self.desc_entry.grid(row=3, column=1, padx=4, pady=2)

        btns = tk.Frame(form_frame)
        btns.grid(row=4, column=0, columnspan=2, pady=6)
        tk.Button(btns, text="+ Add Income", command=lambda: self.add_transaction("income"), bg="#2ecc71").pack(side="left", padx=3)
        tk.Button(btns, text="- Add Expense", command=lambda: self.add_transaction("expense"), bg="#e74c3c").pack(side="left", padx=3)
        tk.Button(btns, text="Clear Form", command=self.clear_form).pack(side="left", padx=3)

        self.tree = ttk.Treeview(
            self.transactions_tab,
            columns=("Amount", "Type", "Category", "Description", "Date"),
            show="headings"
        )
        for col, text in zip(("Amount", "Type", "Category", "Description", "Date"),
                             ("Amount", "Type", "Category", "Description", "Date")):
            self.tree.heading(col, text=text)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def setup_analytics_tab(self):
        tk.Label(self.analytics_tab, text="Financial Statistics").pack(pady=5)
        self.stats_frame = tk.Frame(self.analytics_tab)
        self.stats_frame.pack()
        self.stats_text = tk.Text(self.stats_frame, height=6, width=60)
        self.stats_text.pack()

        self.chart_frame = tk.Frame(self.analytics_tab)
        self.chart_frame.pack(pady=10)
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, self.chart_frame)
        self.canvas.get_tk_widget().pack()

    def setup_budget_tab(self):
        tk.Label(self.budget_tab, text="Monthly Budget Setup").pack(pady=5)
        tk.Label(self.budget_tab, text="Monthly Budget Amount:").pack()
        self.budget_entry = tk.Entry(self.budget_tab)
        self.budget_entry.pack()
        tk.Button(self.budget_tab, text="Set Budget", command=self.set_budget, bg="#9b59b6").pack(pady=5)

        self.budget_progress = tk.Label(self.budget_tab, text="Budget Progress")
        self.budget_progress.pack()
        self.budget_alert = tk.Text(self.budget_tab, height=3, width=50)
        self.budget_alert.pack()

    def setup_search_tab(self):
        tk.Label(self.search_tab, text="Search Filters").pack(pady=5)
        self.search_entry = tk.Entry(self.search_tab)
        self.search_entry.pack()
        tk.Button(self.search_tab, text="Search", command=self.perform_search).pack(pady=5)
        self.search_results = tk.Text(self.search_tab, height=10, width=50)
        self.search_results.pack()

    # ---------- Core logic ----------
    def add_transaction(self, trans_type):
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid amount", "Please enter a valid number.")
            return

        category = self.category_var.get()
        description = self.desc_entry.get().strip()
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        transaction = {
            "amount": amount if trans_type == "income" else -amount,
            "type": trans_type,
            "category": category,
            "description": description,
            "date": date
        }
        self.transactions.append(transaction)
        self.update_display()
        self.save_data()
        self.clear_form()

    def update_display(self):
        balance = sum(t["amount"] for t in self.transactions)
        self.balance_var.set(f"${balance:.2f}")

        # Rebuild table
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, trans in enumerate(self.transactions, 1):
            self.tree.insert(
                "", "end",
                values=(
                    f"${abs(trans['amount']):.2f}",
                    trans["type"],
                    trans["category"],
                    trans["description"],
                    trans["date"]
                )
            )

        self.update_analytics()
        self.update_budget_display()

    def clear_form(self):
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    # ---------- Persistence ----------
    def save_data(self):
        try:
            with open(data_path("wallet_data.json"), "w", encoding="utf-8") as f:
                json.dump(self.transactions, f)
        except OSError as e:
            messagebox.showerror("Save error", f"Could not save data:\n{e}")

    def load_data(self):
        try:
            with open(data_path("wallet_data.json"), "r", encoding="utf-8") as f:
                self.transactions = json.load(f)
        except FileNotFoundError:
            self.transactions = []
        except json.JSONDecodeError:
            # Corrupted file: reset gracefully
            self.transactions = []

    def set_budget(self):
        try:
            self.monthly_budget = float(self.budget_entry.get())
        except ValueError:
            messagebox.showerror("Invalid budget", "Please enter a valid number.")
            return
        self.save_budget()
        self.update_budget_display()

    def save_budget(self):
        try:
            with open(data_path("budget_data.json"), "w", encoding="utf-8") as f:
                json.dump({"monthly_budget": self.monthly_budget}, f)
        except OSError as e:
            messagebox.showerror("Save error", f"Could not save budget:\n{e}")

    def load_budget(self):
        try:
            with open(data_path("budget_data.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
                self.monthly_budget = float(data.get("monthly_budget", 0))
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            self.monthly_budget = 0.0

    def export_to_csv(self):
        try:
            with open(data_path("transactions.csv"), "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Amount", "Type", "Category", "Description", "Date"])
                for trans in self.transactions:
                    writer.writerow([
                        f"${abs(trans['amount']):.2f}",
                        trans["type"],
                        trans["category"],
                        trans["description"],
                        trans["date"]
                    ])
            messagebox.showinfo("Success", f"Data exported to {data_path('transactions.csv')!s}")
        except OSError as e:
            messagebox.showerror("Export error", f"Could not export CSV:\n{e}")

    # ---------- Budget display (the missing method) ----------
    def update_budget_display(self):
        """Refresh the budget progress/alerts based on current transactions."""
        # Sum expenses only (negative amounts)
        total_expenses = abs(sum(t["amount"] for t in self.transactions if t["amount"] < 0))
        spent = total_expenses
        if self.monthly_budget > 0:
            remaining = self.monthly_budget - spent
            progress = (spent / self.monthly_budget) * 100
            # Clamp to 0..999 to avoid weird text if heavily over budget
            progress = max(0.0, min(progress, 999.9))
            self.budget_progress.config(
                text=f"Budget: ${self.monthly_budget:.2f} | Spent: ${spent:.2f} | "
                     f"Remaining: ${remaining:.2f}\n{progress:.1f}%"
            )
            self.budget_alert.delete(1.0, tk.END)
            if progress >= 100:
                self.budget_alert.insert(tk.END, "⚠️ You have exceeded your monthly budget.")
            elif progress >= 75:
                self.budget_alert.insert(tk.END, "NOTICE: You have used 75% of your budget.")
            elif progress >= 50:
                self.budget_alert.insert(tk.END, "NOTICE: You have used 50% of your budget.")
        else:
            self.budget_progress.config(text="Budget Progress")
            self.budget_alert.delete(1.0, tk.END)

    # ---------- Analytics ----------
    def update_analytics(self):
        # Financial Statistics
        total_income = sum(t["amount"] for t in self.transactions if t["amount"] > 0)
        total_expenses = abs(sum(t["amount"] for t in self.transactions if t["amount"] < 0))
        net_savings = total_income - total_expenses
        transactions_count = len(self.transactions)

        # Simple average monthly expense estimate (avoid div-by-zero)
        months_considered = max(1, len({datetime.strptime(t["date"], "%Y-%m-%d %H:%M").strftime("%Y-%m")
                                        for t in self.transactions})) if self.transactions else 1
        avg_monthly_expense = total_expenses / months_considered

        largest_expense = max((abs(t["amount"]) for t in self.transactions if t["amount"] < 0), default=0)

        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, f"Total Income: ${total_income:.2f}\n")
        self.stats_text.insert(tk.END, f"Total Expenses: ${total_expenses:.2f}\n")
        self.stats_text.insert(tk.END, f"Net Savings: ${net_savings:.2f}\n")
        self.stats_text.insert(tk.END, f"Transactions: {transactions_count}\n")
        self.stats_text.insert(tk.END, f"Avg Monthly Expense: ${avg_monthly_expense:.2f}\n")
        self.stats_text.insert(tk.END, f"Largest Expense: ${largest_expense:.2f}")

        # Expense Distribution by Category
        categories = {}
        for t in self.transactions:
            if t["amount"] < 0:
                categories[t["category"]] = categories.get(t["category"], 0) + abs(t["amount"])
        total_expense = sum(categories.values())
        sizes = [v / total_expense * 100 for v in categories.values()] if total_expense > 0 else []
        labels = list(categories.keys())
        colors = ['#2ecc71', '#e74c3c', '#3498db', '#9b59b6', '#f1c40f', '#1abc9c']

        self.ax1.clear()
        if sizes:
            self.ax1.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%', startangle=90)
            self.ax1.axis('equal')
        self.ax1.set_title("Expense Distribution by Category")

        # Income vs Expense (Last 6 Months)
        months = [(datetime.now() - timedelta(days=30 * i)).strftime("%Y-%m") for i in range(5, -1, -1)]  # oldest -> newest
        income_data = {m: 0.0 for m in months}
        expense_data = {m: 0.0 for m in months}
        for t in self.transactions:
            try:
                d = datetime.strptime(t["date"], "%Y-%m-%d %H:%M")
            except (ValueError, KeyError):
                continue
            month = d.strftime("%Y-%m")
            if month in income_data:
                if t["amount"] > 0:
                    income_data[month] += t["amount"]
                else:
                    expense_data[month] += abs(t["amount"])

        self.ax2.clear()
        in_vals = [income_data[m] for m in months]
        ex_vals = [expense_data[m] for m in months]
        self.ax2.bar(months, in_vals, label='Income', color='#2ecc71')
        self.ax2.bar(months, ex_vals, bottom=in_vals, label='Expense', color='#e74c3c')
        self.ax2.set_title("Income vs Expense (Last 6 Months)")
        self.ax2.legend()
        self.ax2.tick_params(axis='x', rotation=45)

        self.canvas.draw()

    # ---------- Search ----------
    def perform_search(self):
        query = self.search_entry.get().lower()
        self.search_results.delete(1.0, tk.END)
        for i, trans in enumerate(self.transactions, 1):
            if query in trans.get("description", "").lower() or query in trans.get("category", "").lower():
                self.search_results.insert(
                    tk.END,
                    f"{i}: ${abs(trans['amount']):.2f} - {trans['type']} - "
                    f"{trans['category']} - {trans['description']} - {trans['date']}\n"
                )

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = AdvancedWallet()
    app.run()
