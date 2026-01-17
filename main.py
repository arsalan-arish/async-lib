from src.asynclib.core import Event_Loop

def test1():
    print("Starting coroutine test1() called by main()")
    print("Ending coroutine test1() called by main()")
    yield ("none", {})

def test2():
    print("Starting coroutine test2() called by main()")
    yield ("await_coroutine", {"target": test1()})
    print("Ending coroutine test2() called by main()")

def main():
    print("Starting coroutine main()")
    yield ("await_coroutine", {"target": test2()})
    print("Ending coroutine main() called by Event loop")



loop = Event_Loop()
loop.run(main())