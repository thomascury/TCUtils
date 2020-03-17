import datetime
import traceback
from concurrent import futures
from time import sleep
from functools import total_ordering
from tabulate import tabulate
from queue import Queue, PriorityQueue
from threading import Event

import warnings
def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return ' %s:%s: %s:%s' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line


@total_ordering
class Sorted:
    def __init__(self, priority):
        self.priority = priority

    def __eq__(self, other):
        return self.priority == other.priority

    def __lt__(self, other):
        return self.priority < other.priority  # Less is top


class Result(Sorted):
    def __init__(self, ces, headers, result):
        super(Result, self).__init__(ces)
        self.headers = headers
        self.result = result

    def __repr__(self):
        return tabulate(self.result, self.result)


class Results:
    def __init__(self):
        self.list = []

        self.headers = None
        self.results = None

    def add(self, result):
        self.list.append(result)
        if self.headers is None:
            self.headers = result.headers
        elif self.headers != result.headers:
            raise ValueError("Headers does not match")
        if self.results is None:
            self.results = result.result
        else:
            self.results.append(result.result)

    def sort(self):
        self.results = list(map(lambda r: r.result, sorted(self.list)))

    def __repr__(self):
        if self.results is None:
            return None
        if self.headers is None:
            return tabulate(self.results)
        return tabulate(self.results, self.headers)


def worker_fn(worker_id, task_queue, result_queue, error_queue, shutdown_event):
    print("Worker #{} started at {}.".format(worker_id, datetime.datetime.now()))
    try:
        while True:
            if task_queue.empty() or shutdown_event.isSet():
                break
            task = task_queue.get_nowait()
            try:
                result = 10/task
                sleep(1)
            except (KeyboardInterrupt, SystemExit) as exc:
                print("Worker #{}: Caught Interruption {}: {}".format(worker_id, type(exc).__name__, exc))
                raise
            except Exception as exc:
                print("Worker #{}: Caught exception {}: {}".format(worker_id, type(exc).__name__, exc))
                error_queue.put_nowait(exc)
            else:
                print("Worker #{}: found {}".format(worker_id, result))
                result_queue.put_nowait(result)
            finally:
                task_queue.task_done()
    finally:
        print("Worker #{} stopped at {}.".format(worker_id, datetime.datetime.now()))


def main():
    with futures.ThreadPoolExecutor(max_workers=3) as pool:
        task_queue = Queue()
        result_queue = PriorityQueue()
        error_queue = Queue()

        for x in range(20, -1, -1):
            task_queue.put_nowait(x)
        task_queue.put_nowait(0)

        shutdown_event = Event()

        try:
            workers = [pool.submit(worker_fn, worker_id, task_queue, result_queue, error_queue, shutdown_event)
                       for worker_id in range(1, pool._max_workers+1)]
            print("Done spawning workers.")
            while task_queue.unfinished_tasks > 0 and False in [f.done() for f in workers]:
                futures.wait(workers, 1)
        except Exception as exc:
            print("Caught exception in main thread, cancelling threads")
            shutdown_event.set()
            for index, future in enumerate(workers):
                future.cancel_thread()
                "Worker #{} : cancelling sent.".format(index)
            while False in [f.done() for f in workers]:
                futures.wait(workers, .5)
            sleep(1)
            raise exc

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

        print(results)


if __name__ == '__main__':
    main()
