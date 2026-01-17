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


#* Signal Command Handling functions
def await_time(**kwargs):
    #SPEC SIGNAL SPEC PARAMS --> {time: int}
    time = kwargs["time"]
    import time as t
    t.sleep(time)
    return None

def await_coroutine(**kwargs):
    #SPEC SIGNAL SPEC PARAMS --> {target: function_object, args : tuple, kwargs : dict}
    target = kwargs.get("target") # It must be a generator object
    if not target:
        raise ValueError("ERROR : No target specified")

    # Actual Action
    loop = Event_Loop()
    result = loop.run(target)
    return result

def create_task(**kwargs):
    pass
    return None

def await_all_tasks(**kwargs):
    pass

def await_task(**kwargs):
    pass

def none(**kwargs):
    return None

#* Protocol dictionary contains all signals reference
protocol = {
    "await_time" : await_time,
    "await_coroutine": await_coroutine,
    "none": none,
    "create_task": create_task,
    "await_all_tasks": await_all_tasks,
    "await_task": await_task,
}

#* Task_queue used by the event loop
class task_queue:
    def __init__(self):
        self.queue = []
    def enqueue(self, coro):
        self.queue.append(coro)
    def dequeue(self, coro):
        self.queue.pop()
    

#* Custom event loop
class Event_Loop:
    def __init__(self):
        self.__doc__ = f"""
        Signal SPEC --> tuple(<command>, dict(param1: arg1, param2, arg2, ...))
        Protocol SPEC --> 
        {list(protocol.keys())}
    """

    SIGNAL_SYNTAX_ERROR = "\nTHE EVENT LOOP CANNOT RECOGNIZE SUCH SYNTAX OF SIGNAL\n PLEASE OBEY THE 'SIGNAL SPEC'!"
    PROTOCOL_ERROR = "\nTHIS COMMAND IS NOT IN THE PROTOCOL\n PLEASE OBEY THE 'PROTOCOL'!"

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
                if command in protocol:
                    try:
                        returned_value = protocol[command](**kwargs) # Calling the handling function
                        generator_sending_value = deepcopy(returned_value) # An arbitrary check just in case any bugs come
                    except Exception as e:
                        if command == "await_coroutine":
                            print(f"======= ERROR : {kwargs['target'].__name__}() failed to run with the following exception")
                            traceback.print_exc()
                        else:
                            raise e
                else:
                    raise Exception(PROTOCOL_ERROR)
            # Until generator returns
            except StopIteration as e:
                return e.value

