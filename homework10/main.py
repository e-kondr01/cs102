from pools import ProcessPool


def heavy_computation(data_chunk):
    pass


if __name__ == '__main__':
    pool = ProcessPool(min_workers=2, max_workers=10, mem_usage='1Gb')
    #  results = pool.map(heavy_computation, big_data)
