# Task 3: Simple Task Scheduler with Priorities

## Goal
Manage tasks with priorities and due dates, including a special "UrgentTask" subclass (inheritance), and sort/filter tasks.

## Files to create
- task_item.py
- urgent_task.py
- scheduler.py
- storage.py
- utils.py
- main.py

---

## task_item.py

```python
class Task:
    def __init__(self, title, due_date, priority="Normal", completed=False):
        # store title, due_date, priority, completed
        pass

    def mark_complete(self):
        # set self.completed = True
        pass

    def to_dict(self):
        # return a dict of all attributes PLUS a "type" key set to "Task"
        # example: {"title": "...", "due_date": "...", "priority": "...", "completed": False, "type": "Task"}
        pass

    def __str__(self):
        # format like: "[ ] Buy groceries | Due: 2024-01-10 | Priority: Normal"
        # if completed is True, use "[x]" instead of "[ ]"
        pass
```

---

## urgent_task.py

```python
from task_item import Task

class UrgentTask(Task):
    def __init__(self, title, due_date, contact_person, completed=False):
        # call super().__init__(title, due_date, priority="Urgent", completed=completed)
        # then store self.contact_person
        pass

    def to_dict(self):
        # call super().to_dict() first, store result in a variable
        # then add "contact_person" key and overwrite "type" to "UrgentTask"
        # return the updated dict
        pass

    def __str__(self):
        # call super().__str__(), append " | Contact: <name>"
        pass
```

---

## scheduler.py

```python
class TaskScheduler:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        pass

    def complete_task(self, title):
        # find task by title (case-insensitive), call mark_complete()
        # print "Task not found" if no match
        pass

    def list_all(self):
        # print every task using its __str__ (just print(task) works)
        pass

    def list_pending(self):
        # print only tasks where completed is False
        pass

    def sort_by_due_date(self):
        # return self.tasks sorted by due_date ascending
        # use: sorted(self.tasks, key=lambda t: t.due_date)
        pass

    def sort_by_priority(self):
        # return tasks sorted so "Urgent" comes before "Normal"
        # use: sorted(self.tasks, key=lambda t: 0 if t.priority == "Urgent" else 1)
        pass
```

---

## utils.py

```python
def is_overdue(task, today_str):
    # return True if task.due_date < today_str
    # only works correctly if dates are formatted YYYY-MM-DD
    pass

def count_by_priority(tasks):
    # return a dict like {"Urgent": 2, "Normal": 5}
    pass
```

---

## storage.py

```python
import json
from task_item import Task
from urgent_task import UrgentTask

def save_tasks(tasks):
    # convert each task using task.to_dict()
    # write the resulting list of dicts to tasks.json using json.dump()
    pass

def load_tasks():
    # try to open tasks.json, use json.load()
    # for each dict in the loaded list:
    #   check dict["type"]
    #   if "UrgentTask": create UrgentTask(title, due_date, contact_person, completed)
    #   if "Task": create Task(title, due_date, priority, completed)
    # return the list of reconstructed objects
    # catch FileNotFoundError -> return []
    pass
```

---

## main.py

```python
from task_item import Task
from urgent_task import UrgentTask
from scheduler import TaskScheduler
from storage import save_tasks, load_tasks

def main():
    scheduler = TaskScheduler()
    # load tasks, add each to scheduler

    while True:
        print("\n1. Add Task")
        print("2. Add Urgent Task")
        print("3. Mark Task Complete")
        print("4. View All Tasks")
        print("5. View Pending Tasks Only")
        print("6. View Tasks Sorted by Due Date")
        print("7. View Tasks Sorted by Priority")
        print("8. Save & Exit")
        choice = input("Choose an option: ")

        # wire up 1-8
        # for 6 and 7, remember these return NEW lists - loop through and print them,
        # don't call scheduler.list_all() for those options

if __name__ == "__main__":
    main()
```

---

## SAMPLE RUN (compare your output against this)

**Input sequence:**
```
Choose an option: 1
Enter title: Buy groceries
Enter due date (YYYY-MM-DD): 2024-01-10
Enter priority (Normal/Urgent, default Normal): 

Choose an option: 2
Enter title: Submit report
Enter due date (YYYY-MM-DD): 2024-01-08
Enter contact person: Manager Sam

Choose an option: 1
Enter title: Clean house
Enter due date (YYYY-MM-DD): 2024-01-12
Enter priority (Normal/Urgent, default Normal): 

Choose an option: 3
Enter title to complete: Buy groceries

Choose an option: 4
Choose an option: 5
Choose an option: 6
Choose an option: 7
Choose an option: 8
```

**Expected output for option 4 (View All Tasks):**
```
[x] Buy groceries | Due: 2024-01-10 | Priority: Normal
[ ] Submit report | Due: 2024-01-08 | Priority: Urgent | Contact: Manager Sam
[ ] Clean house | Due: 2024-01-12 | Priority: Normal
```

**Expected output for option 5 (View Pending Tasks Only):**
```
[ ] Submit report | Due: 2024-01-08 | Priority: Urgent | Contact: Manager Sam
[ ] Clean house | Due: 2024-01-12 | Priority: Normal
```

**Expected output for option 6 (Sorted by Due Date):**
```
[ ] Submit report | Due: 2024-01-08 | Priority: Urgent | Contact: Manager Sam
[x] Buy groceries | Due: 2024-01-10 | Priority: Normal
[ ] Clean house | Due: 2024-01-12 | Priority: Normal
```

**Expected output for option 7 (Sorted by Priority):**
```
[ ] Submit report | Due: 2024-01-08 | Priority: Urgent | Contact: Manager Sam
[x] Buy groceries | Due: 2024-01-10 | Priority: Normal
[ ] Clean house | Due: 2024-01-12 | Priority: Normal
```

**Expected contents of tasks.json after saving:**
```json
[
  {"title": "Buy groceries", "due_date": "2024-01-10", "priority": "Normal", "completed": true, "type": "Task"},
  {"title": "Submit report", "due_date": "2024-01-08", "priority": "Urgent", "completed": false, "type": "UrgentTask", "contact_person": "Manager Sam"},
  {"title": "Clean house", "due_date": "2024-01-12", "priority": "Normal", "completed": false, "type": "Task"}
]
```

**Second run:** running `python main.py` again and choosing option 4 immediately should print the same 3 tasks — proving load_tasks() correctly rebuilds both Task and UrgentTask objects.

## New concept notes
- Inheritance: `UrgentTask(Task)` means UrgentTask automatically gets everything Task has, and you only write the NEW or DIFFERENT behavior.
- `super().__init__(...)` calls the parent class's constructor so you don't repeat code.
- When loading mixed object types from JSON, a `"type"` field is the standard trick to know which class to rebuild.

## Bonus (optional)
- Add `search_by_keyword(tasks, keyword)` in utils.py — return tasks whose title contains the keyword, case-insensitive (`keyword.lower() in task.title.lower()`).