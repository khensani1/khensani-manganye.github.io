import argparse
import json
import os

TASKS_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def get_next_id(tasks):
    if not tasks:
        return 1
    return max(task["id"] for task in tasks) + 1

def add_task(args):
    tasks = load_tasks()
    task = {
        "id": get_next_id(tasks),
        "description": args.description,
        "status": "todo",
        "due": args.due if args.due else None,
        "priority": args.priority if args.priority else "medium"
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task {task['id']}: {task['description']}")

def list_tasks(args):
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return
    grouped = {"todo": [], "in_progress": [], "done": []}
    for task in tasks:
        grouped[task["status"]].append(task)
    statuses = [("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done")]
    if args.status:
        statuses = [(args.status, args.status.replace('_', ' ').title())]
    for status, label in statuses:
        print(f"\n{label}:")
        for task in grouped[status]:
            due = f" (Due: {task['due']})" if task.get('due') else ""
            priority = f" [Priority: {task.get('priority', 'medium')}]"
            print(f"  [{task['id']}] {task['description']}{due}{priority}")

def update_task_status(task_id, new_status):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = new_status
            save_tasks(tasks)
            print(f"Task {task_id} marked as {new_status.replace('_', ' ')}.")
            return
    print(f"Task {task_id} not found.")

def start_task(args):
    update_task_status(args.id, "in_progress")

def done_task(args):
    update_task_status(args.id, "done")

def delete_task(args):
    tasks = load_tasks()
    new_tasks = [task for task in tasks if task["id"] != args.id]
    if len(new_tasks) == len(tasks):
        print(f"Task {args.id} not found.")
    else:
        save_tasks(new_tasks)
        print(f"Task {args.id} deleted.")

def edit_task(args):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == args.id:
            old_desc = task["description"]
            task["description"] = args.description
            save_tasks(tasks)
            print(f"Task {args.id} description updated from '{old_desc}' to '{args.description}'.")
            return
    print(f"Task {args.id} not found.")

def search_tasks(args):
    tasks = load_tasks()
    keyword = args.keyword.lower()
    found = False
    for task in tasks:
        if keyword in task["description"].lower():
            due = f" (Due: {task['due']})" if task.get('due') else ""
            priority = f" [Priority: {task.get('priority', 'medium')}]"
            print(f"[{task['id']}] {task['description']}{due}{priority} (Status: {task['status']})")
            found = True
    if not found:
        print(f"No tasks found containing '{args.keyword}'.")

def set_due_date(args):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == args.id:
            old_due = task.get("due")
            task["due"] = args.due
            save_tasks(tasks)
            print(f"Task {args.id} due date updated from '{old_due}' to '{args.due}'.")
            return
    print(f"Task {args.id} not found.")

def set_priority(args):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == args.id:
            old_priority = task.get("priority", "medium")
            task["priority"] = args.priority
            save_tasks(tasks)
            print(f"Task {args.id} priority updated from '{old_priority}' to '{args.priority}'.")
            return
    print(f"Task {args.id} not found.")

def clear_completed(args):
    tasks = load_tasks()
    new_tasks = [task for task in tasks if task["status"] != "done"]
    removed = len(tasks) - len(new_tasks)
    save_tasks(new_tasks)
    print(f"Cleared {removed} completed task(s).")

def show_task(args):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == args.id:
            print(f"Task ID: {task['id']}")
            print(f"Description: {task['description']}")
            print(f"Status: {task['status']}")
            print(f"Due: {task.get('due', 'None')}")
            print(f"Priority: {task.get('priority', 'medium')}")
            return
    print(f"Task {args.id} not found.")

def main():
    parser = argparse.ArgumentParser(description="Task Tracker CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add command
    parser_add = subparsers.add_parser("add", help="Add a new task")
    parser_add.add_argument("description", type=str, help="Task description")
    parser_add.add_argument("--due", type=str, help="Due date (e.g. 2024-12-31)")
    parser_add.add_argument("--priority", type=str, choices=["low", "medium", "high"], help="Priority level")
    parser_add.set_defaults(func=add_task)

    # List command
    parser_list = subparsers.add_parser("list", help="List all tasks")
    parser_list.add_argument("--status", type=str, choices=["todo", "in_progress", "done"], help="Filter by status")
    parser_list.set_defaults(func=list_tasks)

    # Start command
    parser_start = subparsers.add_parser("start", help="Mark a task as in progress")
    parser_start.add_argument("id", type=int, help="Task ID")
    parser_start.set_defaults(func=start_task)

    # Done command
    parser_done = subparsers.add_parser("done", help="Mark a task as done")
    parser_done.add_argument("id", type=int, help="Task ID")
    parser_done.set_defaults(func=done_task)

    # Delete command
    parser_delete = subparsers.add_parser("delete", help="Delete a task")
    parser_delete.add_argument("id", type=int, help="Task ID")
    parser_delete.set_defaults(func=delete_task)

    # Edit command
    parser_edit = subparsers.add_parser("edit", help="Edit a task's description")
    parser_edit.add_argument("id", type=int, help="Task ID")
    parser_edit.add_argument("description", type=str, help="New description")
    parser_edit.set_defaults(func=edit_task)

    # Search command
    parser_search = subparsers.add_parser("search", help="Search tasks by keyword")
    parser_search.add_argument("keyword", type=str, help="Keyword to search for")
    parser_search.set_defaults(func=search_tasks)

    # Set-due command
    parser_due = subparsers.add_parser("set-due", help="Set or update a task's due date")
    parser_due.add_argument("id", type=int, help="Task ID")
    parser_due.add_argument("due", type=str, help="Due date (e.g. 2024-12-31)")
    parser_due.set_defaults(func=set_due_date)

    # Set-priority command
    parser_priority = subparsers.add_parser("set-priority", help="Set or update a task's priority")
    parser_priority.add_argument("id", type=int, help="Task ID")
    parser_priority.add_argument("priority", type=str, choices=["low", "medium", "high"], help="Priority level")
    parser_priority.set_defaults(func=set_priority)

    # Clear-completed command
    parser_clear = subparsers.add_parser("clear-completed", help="Delete all completed (done) tasks")
    parser_clear.set_defaults(func=clear_completed)

    # Show command
    parser_show = subparsers.add_parser("show", help="Show all details for a specific task")
    parser_show.add_argument("id", type=int, help="Task ID")
    parser_show.set_defaults(func=show_task)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main() 
