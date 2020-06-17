import numpy
import random

from pools import ProcessPool


def heavy_computation(data_chunk):
    kernel = numpy.ndarray(shape=(2000, 2000))
    kernel[:] = 10
    res = sum(sum(data_chunk * kernel)) ** 2
    s = 'Data:\n' + str(data_chunk) + '\n' + 'Result:\n' + str(res)
    print(s)


def get_big_data():
    big_data = []
    for _ in range(20):
        array = numpy.ndarray(shape=(2000, 2000))
        array[:] = random.randint(1, 100)
        big_data.append(array)
    return big_data


if __name__ == '__main__':
    big_data = get_big_data()
    pool = ProcessPool(min_workers=2, max_workers=10, mem_usage='0.5Gb')
    results = pool.map(heavy_computation, big_data)
