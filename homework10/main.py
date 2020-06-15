from pools import ProcessPool


def heavy_computation(data_chunk):
    print(sum(data_chunk)**2)


def get_big_data():
    big_data = []
    big_data.append([i for i in range(1000)])
    big_data.append([i for i in range(1001)])
    big_data.append([i for i in range(1002)])
    big_data.append([i for i in range(1003)])
    return big_data


if __name__ == '__main__':
    big_data = get_big_data()
    pool = ProcessPool(min_workers=2, max_workers=10, mem_usage='1Gb')
    results = pool.map(heavy_computation, big_data)
