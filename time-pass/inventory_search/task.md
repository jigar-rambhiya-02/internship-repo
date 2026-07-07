# Task 4: Inventory Search & Filter System

## Goal
Build an inventory system focused on searching and filtering — multiple filter criteria, combining filters, and text search. This is heavier on logic than file structure.

## Files to create
- product.py
- inventory.py
- search_filters.py
- storage.py
- main.py

---

## product.py

```python
class Product:
    def __init__(self, name, category, price, quantity, tags=None):
        # store name, category, price (float), quantity (int)
        # tags is a list of strings, e.g. ["electronics", "sale"]
        # if tags is None, default to an empty list - be careful not to share
        # one mutable list between all objects (don't use tags=[] as default!)
        pass

    def to_dict(self):
        # return dict of all attributes, tags as a list
        pass

    def __str__(self):
        # format like:
        # "Wireless Mouse | Electronics | $19.99 | Qty: 50 | Tags: sale, bestseller"
        pass
```

**Important gotcha to be aware of:** never write `def __init__(self, tags=[])` — mutable default arguments in Python are shared across every object that doesn't pass one in. Use `tags=None`, then inside the method do `self.tags = tags if tags is not None else []`.

---

## inventory.py

```python
class Inventory:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        pass

    def remove_product(self, name):
        # remove by exact name match (case-insensitive)
        pass

    def update_quantity(self, name, new_quantity):
        # find product by name, update its quantity
        pass

    def list_all(self):
        pass
```

---

## search_filters.py

This is the core of the task — practice writing several independent filter functions that all take `products` (a list) and return a filtered list.

```python
def search_by_name(products, keyword):
    # return products where keyword (case-insensitive) appears anywhere in product.name
    pass

def filter_by_category(products, category):
    # return products matching category exactly (case-insensitive)
    pass

def filter_by_price_range(products, min_price, max_price):
    # return products where min_price <= product.price <= max_price
    pass

def filter_by_tag(products, tag):
    # return products where tag (case-insensitive) is in product.tags
    pass

def filter_low_stock(products, threshold):
    # return products where quantity < threshold
    pass

def combined_filter(products, category=None, min_price=None, max_price=None, tag=None):
    # apply ONLY the filters that were actually provided (not None)
    # start with all products, then narrow down step by step
    # example: if category is given, filter by category first, then filter that
    # result further by price range if given, etc.
    pass
```

---

## storage.py

```python
import json
from product import Product

def save_inventory(products):
    # save list of product.to_dict() to inventory.json
    pass

def load_inventory():
    # load inventory.json, rebuild Product objects
    # catch FileNotFoundError -> return []
    pass
```

---

## main.py

```python
from product import Product
from inventory import Inventory
from search_filters import (
    search_by_name, filter_by_category, filter_by_price_range,
    filter_by_tag, filter_low_stock, combined_filter
)
from storage import save_inventory, load_inventory

def main():
    inv = Inventory()
    # load existing products into inv

    while True:
        print("\n1. Add Product")
        print("2. View All Products")
        print("3. Search by Name")
        print("4. Filter by Category")
        print("5. Filter by Price Range")
        print("6. Filter by Tag")
        print("7. Low Stock Report (below threshold)")
        print("8. Combined Filter (category + price range)")
        print("9. Save & Exit")
        choice = input("Choose an option: ")

        # wire up all 9 options
        # for tags input, split the user's comma-separated string:
        # tags = [t.strip() for t in input("Tags (comma separated): ").split(",")]

if __name__ == "__main__":
    main()
```

---

## SAMPLE RUN (compare your output against this)

**Setup — add these 4 products first (option 1, repeated 4 times):**
```
Name: Wireless Mouse | Category: Electronics | Price: 19.99 | Quantity: 50 | Tags: sale,bestseller
Name: Office Chair    | Category: Furniture   | Price: 89.50 | Quantity: 5  | Tags: sale
Name: USB Cable       | Category: Electronics | Price: 5.99  | Quantity: 3  | Tags: bestseller
Name: Desk Lamp       | Category: Furniture   | Price: 24.00 | Quantity: 15 | Tags: (leave blank)
```

**Option 3 - Search by Name, keyword "usb":**
```
USB Cable | Electronics | $5.99 | Qty: 3 | Tags: bestseller
```

**Option 4 - Filter by Category "Electronics":**
```
Wireless Mouse | Electronics | $19.99 | Qty: 50 | Tags: sale, bestseller
USB Cable | Electronics | $5.99 | Qty: 3 | Tags: bestseller
```

**Option 5 - Filter by Price Range, min=10, max=30:**
```
Wireless Mouse | Electronics | $19.99 | Qty: 50 | Tags: sale, bestseller
Desk Lamp | Furniture | $24.00 | Qty: 15 | Tags:
```

**Option 6 - Filter by Tag "sale":**
```
Wireless Mouse | Electronics | $19.99 | Qty: 50 | Tags: sale, bestseller
Office Chair | Furniture | $89.50 | Qty: 5 | Tags: sale
```

**Option 7 - Low Stock Report, threshold=10:**
```
Office Chair | Furniture | $89.50 | Qty: 5 | Tags: sale
USB Cable | Electronics | $5.99 | Qty: 3 | Tags: bestseller
```

**Option 8 - Combined Filter, category=Electronics, min_price=10, max_price=30:**
```
Wireless Mouse | Electronics | $19.99 | Qty: 50 | Tags: sale, bestseller
```
(USB Cable is excluded — it's Electronics but priced at $5.99, below min_price)

## New concept notes
- Writing several small, single-purpose filter functions (each doing ONE thing) is far easier to test and debug than one giant function with lots of if/else.
- `combined_filter` should REUSE your other filter functions rather than rewriting the logic — call `filter_by_category`, then feed its result into `filter_by_price_range`, etc.
- Mutable default arguments (`def f(x=[])`) are a classic Python trap — now you've seen why to avoid them.

## Bonus (optional)
- Add `sort_by_price(products, descending=False)` using `sorted()` with a lambda key.