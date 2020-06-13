import multiprocessing


class ProcessPool:
    def __init__(self, min_workers, max_workers, mem_usage):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.mem_usage = self.mem_in_bits(mem_usage)
        self.workers = []

        self.in_queue = multiprocessing.Queue
        self.out_queue = multiprocessing.Queue

    def mem_in_bits(self, s):
        if 'Gb' in s:
            return int(s[:len(s)-2]) * 2 ** 33
        elif 'Mb' in s:
            return int(s[len(s)-2]) * 2 ** 23
        else:
            raise Exception('Invalid memory format')
