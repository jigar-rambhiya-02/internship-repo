class Expense:
    def __init__(self, amount: float, category, description, date):
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date
        pass

    def __str__(self):
        log = '[{date}] {category} - {description}: ${amount}'
        return log
    