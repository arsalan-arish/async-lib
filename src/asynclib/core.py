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
    def __init__(self):
        self.queue = []
    def enqueue(self, generator):
        self.queue.append(generator)
    def dequeue(self, generator):
        self.queue.pop(0)
    

#* Signal Command Handling functions
class Handler:

    def __init__(self):
        self.queue = Task_Queue()
        self.protocol = {
        "await_time" : self.await_time,
        "await_coroutine": self.await_coroutine,
        "none": self.none,
        "create_task": self.create_task,
        "await_all_tasks": self.await_all_tasks,
        "await_task": self.await_task,
      }
    

    def await_time(self, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {time: int}
        time = kwargs["time"]
        import time as t
        t.sleep(time)
        return None

    def await_coroutine(self, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {target: generator_object}
        target = kwargs.get("target") # It must be a generator object
        if not target:
            raise ValueError("ERROR : No target specified")

        loop = Event_Loop()
        result = loop.run(target)
        return result

    def create_task(self, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {target: generator_object}

        return None

    def await_all_tasks(self, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {target: generator_object}
        pass

    def await_task(self, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {target: generator_object}
        pass

    def none(self, **kwargs):
        #SPEC SIGNAL SPEC PARAMS --> {target: generator_object}
        return None



#* Custom event loop
class Event_Loop:
    def __init__(self):
        self.handler = Handler()
        self.__doc__ = f"""
        Signal SPEC --> tuple(<command>, dict(param1: arg1, param2, arg2, ...))
        Protocol SPEC -->
        {list(self.handler.protocol.keys())}"""
        
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
                if command in self.handler.protocol:
                    try:
                        returned_value = self.handler.protocol[command](**kwargs) # Calling the handling function
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

