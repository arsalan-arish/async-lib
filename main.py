from src.asynclib.core import Event_Loop

def task1():
    print("Starting task1...")
    yield ("await_time", {"time": 3})
    print("Ending task1...")

def task2():
    print("Starting task2...")
    yield ("await_time", {"time": 3})
    print("Ending task2...")


def main():
    print("Starting coroutine main()")
    yield ("create_task", {"target": task1()})
    yield ("create_task", {"target": task2()})
    yield ("await_all_tasks", {})
    print("Ending coroutine main() called by Event loop")



loop = Event_Loop()
loop.run(main())