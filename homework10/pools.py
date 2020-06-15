import multiprocessing
import psutil
import time


class ProcessPool:
    def __init__(self, min_workers, max_workers, mem_usage):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.mem_usage = self.mem_in_bytes(mem_usage)

    def mem_in_bytes(self, s):
        if 'Gb' in s:
            return int(s[:len(s)-2]) * 2 ** 30
        elif 'Mb' in s:
            return int(s[:len(s)-2]) * 2 ** 20
        else:
            raise Exception('Invalid memory format')

    def map(self, func, data):
        self.guess_max_workers(func, data[0])
        if self.max_workers < self.min_workers:
            raise Exception('Not enough memory to have min workers')
        print(f'Looks like there should be {self.max_workers} workers')
        self.pool = multiprocessing.Pool(processes=self.max_workers)
        res = self.pool.map_async(func, data[1:])
        res.get()
        self.pool.close()

    def guess_max_workers(self, func, data):
        data = [data]  # check in another dataset
        p = multiprocessing.Process(target=func, args=data)
        p.start()
        memory_usage = []
        while p.is_alive():
            try:
                memory_usage.append(psutil.Process(p.pid).memory_info()[0])
                time.sleep(0.01)
            except psutil.NoSuchProcess:
                break
        peak_memory_usage = max(memory_usage)
        self.max_workers = min(self.mem_usage // peak_memory_usage,
                               self.max_workers)
