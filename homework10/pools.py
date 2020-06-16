import multiprocessing
import psutil
import time
from threading import Thread

class ProcessPool:
    def __init__(self, min_workers, max_workers, mem_usage):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.mem_usage = self.mem_in_bytes(mem_usage)
        self.processes = []
        self.in_queue = multiprocessing.Queue()
        self.running = False

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

        for item in data[1:]:
            self.in_queue.put(item)
        for _ in range(self.max_workers):
            p = multiprocessing.Process(target=self.run_p, args=(func,))
            self.processes.append(p)
        for p in self.processes:
            p.start()
            if not self.running:
                self.running = True
                self.start_monitoring()

    def run_p(self, func):
        while True:
            if self.in_queue.empty():
                break
            data = self.in_queue.get()
            func(data)

    def guess_max_workers(self, func, data):
        p = multiprocessing.Process(target=func, args=(data,))
        p.start()
        memory_usage = []
        while p.is_alive():
            try:
                mem = psutil.Process(p.pid).memory_info()[0]
                if mem >= self.mem_usage:
                    raise Exception("Cannot run the proccess with given memory")
                memory_usage.append(mem)
                time.sleep(0.01)
            except psutil.NoSuchProcess:
                break
        print(f'Bytes used by first process: {memory_usage}')
        peak_memory_usage = max(memory_usage)
        print(f'First process used {peak_memory_usage} bytes at max')
        self.max_workers = min(self.mem_usage // peak_memory_usage,
                               self.max_workers)

    def monitor_memory(self):
        while self.running:
            max_memory_usage = 0
            memory_usage = []
            print(self.processes)
            for p in self.processes:
                if p.is_alive():
                    try:
                        mem = psutil.Process(p.pid).memory_info()[0]
                    except psutil.NoSuchProcess:
                        mem = 0
                        memory_usage.append(mem)
                        continue
                    print(p)
                    print(mem)
                    memory_usage.append(mem)
                    if mem > max_memory_usage:
                        max_memory_usage = mem
                        process_with_most_memory = p
            print(sum(memory_usage))
            if not sum(memory_usage) and self.running:
                self.running = False
                print('seems like the programm ended...')
            if sum(memory_usage) >= self.mem_usage:
                print(process_with_most_memory)
                process_with_most_memory.terminate()
                print(f'{process_with_most_memory} had to be terminated')
            time.sleep(0.05)

    def start_monitoring(self):
        # Process here gave an error
        p = Thread(target=self.monitor_memory)
        p.start()
