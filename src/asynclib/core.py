""" ----- Implementation of asynchronous workflow using purely generators / iterator protocol -----

    The event loop 'run' takes a 'main' function (coroutine) as an entrypoint argument, and handles all 
    asynchronous operations. The asynchronous functions have to be generator objects, from which they
    inherit the functionality of temporarily returning (pausing) and saving their state crucial for 
    asynchronous operations. The functions can give signals (with 'yield' keyword) with specific commands 
    and arguments so that the event loop can understand what to do and handle accrodingly.
"""

# For tasks, add internal memory dict of completed tasks' returned results.
# Also instead of dequeueing(popping), store completed tasks in another list/dict with their results 

from copy import deepcopy
import traceback
from threading import Thread
from time import sleep
from func_timeout import func_timeout

__all__ = [
    "event_loop",
]


#* Task_queue used by the event loop
class Task_Queue:
    __slots__ = ('queue')

    def __init__(self):
        self.queue = list([]) # list() to avoid mutable object sharing 
    def enqueue(self, generator_obj):
        self.queue.append(generator_obj)
    def remove_task(self, generator_obj):
        self.queue.remove(generator_obj)
    

#* Signal Command Handling functions
class Handler:
    __slots__ = ('protocol', 'handling_error_msgs')
    queue = Task_Queue()

    @staticmethod
    def counter(time: int):
        sleep(time)

    def __init__(self):
        self.protocol = dict({ # dict() to avoid mutable object sharing
        "await_time" : self.await_time,
        "await_coroutine": self.await_coroutine,
        "none": self.none,
        "create_task": self.create_task,
        "await_all_tasks": self.await_all_tasks,
        "await_task": self.await_task,
        "remove_task": self.remove_task
       })
        self.handling_error_msgs = dict({ # dict() to avoid mutable object sharing
        "await_time" : "",
        "await_coroutine": f"\nThe awaited coroutine failed to run with the following exception",
        "none": "",
        "create_task": "",
        "await_all_tasks": "",
        "await_task": "",
        "remove_task": "",
       })
    
    def await_coroutine(self, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {target: generator_object}
        target = kwargs.get("target") # It must be a generator object
        if not target:
            raise ValueError("ERROR : No target specified")
        loop = Event_Loop()
        result = loop.run(target)
        return result

    @classmethod
    def create_task(cls,**kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {target: generator_object}
        generator_obj = kwargs["target"]
        cls.queue.enqueue(generator_obj)
        return None

    @classmethod
    def remove_task(cls, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {target: generator_object}
        generator_obj = kwargs["target"]
        cls.queue.remove_task(generator_obj)
        return None

    @classmethod
    def await_all_tasks(cls, time: int = None, tasks: list = None, **kwargs) -> list:
        #SPEC SIGNAL SPEC PARAMS --> {}
        if not time:
            if not tasks:
                tasks = cls.queue.queue
                if not tasks:
                    return list([])
            loop = Event_Loop()
            results: list = loop.run_tasks(tasks)
            return results
        elif time:
            if not tasks:
                tasks = cls.queue.queue
                if not tasks:
                    return list([])
            loop = Event_Loop()
            t = Thread(target=Handler.counter, args=(time,))
            t.start()
            try:
                results: list | None = func_timeout(time, loop.run_tasks(tasks))
            except FunctionTimedOut as e:
                pass
            t.join()
            return results


    def await_task(self, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> 
        pass

    @classmethod
    def await_time(cls, source: str = "run", **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {time: int}
        time: int = kwargs["time"]
        match source:
            case "run":
                Handler.await_all_tasks(time)
            case "run_tasks":
                tasks = list(cls.queue.queue).pop(0)
                Handler.await_all_tasks(time, tasks)

        return None

    def none(self, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {}
        return None



#* Custom event loop
class Event_Loop:
    __slots__ = ()

    """ Signal SPEC --> tuple(<command>, dict(param1: arg1, param2, arg2, ...))
        Protocol SPEC -->
        Available commands:
        - await_time: Sleep for specified duration
        - await_coroutine: Await another coroutine
        - await_task: Wait for a specific task
        - await_all_tasks: Wait for all tasks to complete
        - create_task: Create a new task
        - remove_task: Remove a task
        - none: No operation
    """

    SIGNAL_SYNTAX_ERROR = "\nTHE EVENT LOOP CANNOT RECOGNIZE SUCH SYNTAX OF SIGNAL\n PLEASE OBEY THE 'SIGNAL SPEC'!"
    PROTOCOL_ERROR = "\nTHIS COMMAND IS NOT IN THE PROTOCOL\n PLEASE OBEY THE 'PROTOCOL'!"
    handler = Handler()

    def run(self, generator_object):
        generator_sending_value = None # Initializing
        while True:
            # Drive the generator
            try:
                yielded = generator_object.send(generator_sending_value)
                try:
            # Read the signal
                    command = yielded[0]
                    kwargs = dict(yielded[1])
                except ValueError:
                    raise ValueError(SIGNAL_SYNTAX_ERROR)
            # Handle the signal
                if command in Event_Loop.handler.protocol:
                    try:
                        returned_value = Event_Loop.handler.protocol[command](**kwargs) # Calling the handling function
                        generator_sending_value = deepcopy(returned_value) # An arbitrary check just in case any bugs come
                    except Exception as e:
                        error_msg = Event_Loop.handler.handling_error_msgs.get(command)
                        print(f"======= ERROR - COMMAND: {command}; ARGS: {kwargs};  {error_msg}")
                        traceback.print_exc()
                else:
                    raise Exception(PROTOCOL_ERROR)
            # Until generator returns
            except StopIteration as e:
                return e.value

    def run_tasks(self, tasks: list) -> list:
        # tasks is a list of generator objects
        generator_sending_value = None # Initializing value
        results: list = list([])
        for task in tasks:
            while True:
                # Drive the generator
                try:
                    yielded = task.send(generator_sending_value)
                    try:
                # Read the signal
                        command: str = yielded[0]
                        kwargs: dict = dict(yielded[1])
                    except ValueError:
                        raise ValueError(SIGNAL_SYNTAX_ERROR)
                # Handle the signal
                    if command in Event_Loop.handler.protocol:
                        if command == "await_time":
                            try:
                                returned_value = Event_Loop.handler.protocol[command]("run_tasks",**kwargs)
                                results.append(returned_value)
                            except Exception as e:
                                error_msg = Event_Loop.handler.handling_error_msgs.get(command)
                                print(f"======= ERROR - COMMAND: {command}; ARGS: {kwargs};  {error_msg}")
                                traceback.print_exc()
                        else:
                            try:
                                returned_value = Event_Loop.handler.protocol[command](**kwargs) # Calling the handling function
                                generator_sending_value = deepcopy(returned_value) # An arbitrary check just in case any bugs come
                            except Exception as e:
                                error_msg = Event_Loop.handler.handling_error_msgs.get(command)
                                print(f"======= ERROR - COMMAND: {command}; ARGS: {kwargs};  {error_msg}")
                                traceback.print_exc()
                    else:
                        raise Exception(PROTOCOL_ERROR)
                # Until generator returns
                # TODO Fix the order problem of results
                except StopIteration as e:
                    results.append(e.value)
                    tasks.pop(0)

        return results
