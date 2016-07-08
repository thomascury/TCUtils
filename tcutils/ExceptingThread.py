import datetime
import queue as Queue
import traceback
import warnings
from time import sleep
import threading
import inspect
import ctypes

# Async raise recipe found on
# http://tomerfiliba.com/recipes/Thread2/


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class Thread(threading.Thread):
    def _get_my_tid(self):
        """determines this (self's) thread id"""
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        raise AssertionError("could not determine the thread's id")

    def raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        _async_raise(self._get_my_tid(), exctype)

    def interrupt(self):
        """raises KeyboardInterrupt in the context of the given thread, which should
        cause the thread to exit loudly (unless caught)"""
        self.raise_exc(KeyboardInterrupt)

    def terminate(self):
        """raises SystemExit in the context of the given thread, which should
        cause the thread to exit silently (unless caught)"""
        self.raise_exc(SystemExit)


class ExceptingThread(Thread):
    def __init__(self, pid, worker_function, queues, shutdown_event):
        self.tasks, self.results, self.errors = queues
        self._shutdown = shutdown_event
        self._worker = worker_function
        self._pid = pid
        super(ExceptingThread, self).__init__(name="thread-{}".format(pid),
                                              target=self._worker,
                                              args=(pid, queues, shutdown_event))
        self.setDaemon(True)

    def run(self):
        self.prepare_thread()
        try:
            super(ExceptingThread, self).run()
        except (KeyboardInterrupt, SystemExit) as exc:
            print("Interruption {} in thread_{}".format(type(exc).__name__, self._pid))
            self.error_treatment(exc)
            self.cancel_thread()
        except Exception as exc:
            self.error_treatment(exc)
        finally:
            self.cleanup_thread()

    def cancel_thread(self):
        # raise NotImplementedError
        pass

    def error_treatment(self, exc):
        self.errors.put_nowait(exc)

    def prepare_thread(self):
        print("{} started".format(self.name))

    def cleanup_thread(self):
        print("{} stopped.".format(self.name))


def worker_fn(pid, queues, shutdown_event):
    tasks, results, errors = queues
    while not shutdown_event.is_set():
        try:
            task = tasks.get_nowait()
        except Queue.Empty:
            break
        try:
            print("worker_{}: working on item #{}".format(pid, task))
            sleep(1)
            results.put_nowait(task)
        finally:
            print("worker_{}: finished working on item #{}".format(pid, task))
            tasks.task_done()


def main():
    task_queue = Queue.Queue()
    result_queue = Queue.Queue()
    error_queue = Queue.Queue()
    queues = (task_queue, result_queue, error_queue)

    for i in range(1, 11):
        task_queue.put_nowait(i)

    nb_of_threads = 3
    shutdown_event = threading.Event()
    threads = [ExceptingThread(pid, worker_fn, queues, shutdown_event) for pid in range(nb_of_threads)]

    print("Go !")
    starting_stamp = datetime.datetime.now()

    try:
        # Start threads
        for thread in threads:
            thread.start()

        while True in (thread.is_alive() for thread in threads):
            sleep(.5)
    except (KeyboardInterrupt, SystemExit):
        print("Interruption detected. Propagating to threads.")
        shutdown_event.set()
        for thread in threads:
            thread.interrupt()
        for thread in threads:
            thread.join()
        sleep(1)
    finally:
        extract_time = datetime.datetime.now() - starting_stamp
        print("Finished !")

    # Parse results
    results = []
    while result_queue.unfinished_tasks > 0:
        result = result_queue.get_nowait()
        results.append(result)
        result_queue.task_done()
    nb_match = len(results)

    # Parse and log errors
    with open("error.log", 'w') as error_log_d:
        errors = []
        while error_queue.unfinished_tasks > 0:
            exception = error_queue.get_nowait()
            try:
                raise exception
            except:
                traceback.print_exc(file=error_log_d)
            error_log_d.write("\n")
            errors.append(exception)
            error_queue.task_done()
    if len(errors) > 0:
        warnings.warn("Errors occured, check the error log.", RuntimeWarning)

    print(print("Extracted {} lines in {}.".format(nb_match, extract_time)))

if __name__ == '__main__':
    main()
