import os
from datetime import datetime

def save_result(num1, num2, expression, result):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = f'[{timestamp}] {num1} {expression} {num2} = {result}\n'
    with open('History.txt', 'a') as file:   # 'a' for append only
        file.write(log)

def show_history():
    if not os.path.exists('History.txt'):
        print("No history yet.")
        return
    with open('History.txt', 'r') as file:   # 'r' for reading only
        content = file.readlines()
        if not content:
            print("History is empty.")
        else:
            for line in content:
                print(line, end='')   # avoid extra blank lines