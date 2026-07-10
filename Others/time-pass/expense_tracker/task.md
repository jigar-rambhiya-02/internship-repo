# Task 2: Expense Tracker with Categories

## Goal
Track expenses grouped by category, generate simple reports (totals, sorted lists), and store data in a CSV file so it survives between runs.

## Files to create
- expense.py
- tracker.py
- reports.py
- storage.py
- main.py

---

## expense.py

Define a class `Expense` that just stores data and knows how to print itself.

```python
class Expense:
    def __init__(self, amount, category, description, date):
        # store all 4 values as self.amount, self.category, self.description, self.date
        pass

    def __str__(self):
        # return a string like:
        # "[2024-01-05] Food - Lunch: $12.50"
        pass
```

**Note:** `amount` should be stored as a `float`, even if the user types it as a string from `input()`.

---

## tracker.py

```python
class ExpenseTracker:
    def __init__(self):
        self.expenses = []

    def add_expense(self, expense):
        # add expense object to self.expenses
        pass

    def get_by_category(self, category):
        # return a list of expenses where expense.category matches (case-insensitive)
        pass

    def total_spent(self):
        # return sum of all expense.amount values
        # return 0 if list is empty
        pass

    def total_by_category(self):
        # return a dict like {"Food": 45.50, "Transport": 20.00}
        # loop through self.expenses, build dict manually:
        #   if category already a key, add to it
        #   else, create the key with that amount
        pass
```

---

## reports.py

```python
def generate_summary(tracker):
    # print total spent overall (use tracker.total_spent())
    # print total spent per category (use tracker.total_by_category())
    # Example output format:
    # Total Spent: $150.00
    # --- By Category ---
    # Food: $80.00
    # Transport: $70.00
    pass

def top_category(tracker):
    # find category with highest total spend
    # use max() on the dict from tracker.total_by_category(), with key=dict.get
    # print like: "Top spending category: Food ($80.00)"
    # handle case where there are no expenses at all
    pass
```

---

## storage.py

Use Python's built-in `csv` module (`import csv`).

```python
import csv
from expense import Expense

def save_expenses(expenses):
    # open "expenses.csv" in write mode, newline=""
    # use csv.writer
    # write one row per expense: [amount, category, description, date]
    pass

def load_expenses():
    # try to open "expenses.csv" in read mode
    # use csv.reader
    # for each row, create an Expense object (remember to convert amount back to float!)
    # return list of Expense objects
    # if file doesn't exist, catch FileNotFoundError and return []
    pass
```

---

## main.py

```python
from expense import Expense
from tracker import ExpenseTracker
from reports import generate_summary, top_category
from storage import save_expenses, load_expenses

def main():
    tracker = ExpenseTracker()
    # load existing expenses, add each to tracker

    while True:
        print("\n1. Add Expense")
        print("2. View All Expenses")
        print("3. View Summary Report")
        print("4. View Top Spending Category")
        print("5. Save & Exit")
        choice = input("Choose an option: ")

        # wire up choices 1-5
        # option 5 should call save_expenses(tracker.expenses) then break

if __name__ == "__main__":
    main()
```

---

## SAMPLE RUN (use this to compare your output)

**Input sequence (what you'd type when running `python main.py` for the first time, empty expenses.csv):**

```
Choose an option: 1
Enter amount: 12.50
Enter category: Food
Enter description: Lunch
Enter date (YYYY-MM-DD): 2024-01-05

Choose an option: 1
Enter amount: 30.00
Enter category: Transport
Enter description: Cab fare
Enter date (YYYY-MM-DD): 2024-01-06

Choose an option: 1
Enter amount: 67.50
Enter category: Food
Enter description: Groceries
Enter date (YYYY-MM-DD): 2024-01-07

Choose an option: 2
Choose an option: 3
Choose an option: 4
Choose an option: 5
```

**Expected output for option 2 (View All Expenses):**
```
[2024-01-05] Food - Lunch: $12.50
[2024-01-06] Transport - Cab fare: $30.00
[2024-01-07] Food - Groceries: $67.50
```

**Expected output for option 3 (View Summary Report):**
```
Total Spent: $110.00
--- By Category ---
Food: $80.00
Transport: $30.00
```

**Expected output for option 4 (View Top Spending Category):**
```
Top spending category: Food ($80.00)
```

**Expected contents of expenses.csv after saving:**
```
12.5,Food,Lunch,2024-01-05
30.0,Transport,Cab fare,2024-01-06
67.5,Food,Groceries,2024-01-07
```

**Second run (loading existing file):** if you run `python main.py` again and choose option 2 right away, you should see the same 3 expenses printed — proving load_expenses() works.

## New concept notes
- `csv.writer` and `csv.reader` handle commas/quoting for you — safer than manual string splitting.
- Building a running-total dictionary is a very common pattern: check `if key in dict` before adding to it, or use `dict.get(key, 0) + amount`.
- `max(dictionary, key=dictionary.get)` finds the key with the highest value — worth remembering, it comes up a lot.

## Bonus (optional)
- Add `filter_by_date_range(tracker, start_date, end_date)` — since dates are formatted YYYY-MM-DD, plain string comparison (`"2024-01-05" >= start_date`) works correctly without needing the `datetime` module.