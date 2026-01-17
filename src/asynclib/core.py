""" ----- Implementation of asynchronous workflow using purely generators / iterator protocol -----

    The event loop 'run' takes a 'main' function (coroutine) as an entrypoint argument, and handles all 
    asynchronous operations. The asynchronous functions have to be generator objects, from which they
    inherit the functionality of temporarily returning (pausing) and saving their state crucial for 
    asynchronous operations. The functions can give signals (with 'yield' keyword) with specific commands 
    and arguments so that the event loop can understand what to do and handle accrodingly.
"""

from copy import deepcopy
import traceback

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
    def dequeue(self):
        self.queue.pop(0)
    def remove_task(self, generator_obj):
        self.queue.remove(generator_obj)
    

#* Signal Command Handling functions
class Handler:
    __slots__ = ('protocol', 'handling_error_msgs')
    queue = Task_Queue()

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
    def await_all_tasks(cls, **kwargs):
        #SPEC SIGNAL SPEC PARAMS -->
        cls.

    def await_task(self, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> 
        pass

    def await_time(self, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {time: int}
        time = kwargs["time"]
        import time as t
        t.sleep(time)
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
