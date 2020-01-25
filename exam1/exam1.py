import os
import csv

from collections import defaultdict
from itertools import groupby
from operator import itemgetter
from tabulate import tabulate

d1 = {'number': 0,
      'district': 1,
      'address': 2,
      'amount': 3}


class DataFrame:

    def __init__(self, headers, rows):
        self._headers = headers
        self._rows = rows

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, new_headers):
        assert len(self._headers) == len(new_headers)
        self._headers = new_headers

    @property
    def rows(self):
        return self._rows

    def group_by(self, by):
        d = {}
        for row in self.rows:
            k = row[d1[by]].strip()
            if k not in d.keys():
                d[k] = []
                d[k].append(row)
            else:
                d[k].append(row)
        groupped_headers = [f'{by}', 'data']
        groupped = GrouppedDataFrame(groupped_headers, d)
        return groupped

    def merge(self, df, by):
        n = df.headers.index(by)
        new_rows = []
        for row1 in self.rows:
            for row2 in df.rows:
                if row1[n] == row2[n]:
                    del row2[n]
                    new_row = row1 + row2
                    new_rows.append(new_row)
                    break
        del df.headers[n]
        new_headers = self.headers + df.headers
        new_df = DataFrame(new_headers, new_rows)
        return new_df

    def __str__(self):
        return tabulate(self.rows, headers=self.headers)

    @staticmethod
    def from_file(path):
        data = []
        with open(f'{path}', 'r', encoding='UTF-8') as f:
            headers = f.readline().rstrip('\n').split(',')
            # while True:
            for i in range(2000):
                line = f.readline().rstrip('\n')
                if not line:
                    break
                split_line = line.split(',')
                stop = len(split_line) - 1
                for i in range(3, stop):
                    split_line[2] += split_line[3]
                    del split_line[3]
                data.append(split_line)
        rows = data
        dataframe = DataFrame(headers, rows)
        return dataframe

    def to_csv(self, path):
        data = [self._headers] + self._rows
        with open(path, "w", newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            for line in data:
                writer.writerow(line)


class GrouppedDataFrame:

    def __init__(self, headers, groups):
        self._headers = headers
        self._groups = groups

    def sum_by(self, by):
        new_data = []
        for key in self._groups.keys():
            L = []
            L.append(key)
            sum = 0
            for item in self._groups[key]:
                sum += int(item[d1[by]])
            L.append(sum)
            new_data.append(L)
        new_dataframe = DataFrame(self._headers, new_data)
        return new_dataframe


BASE_PATH = r'C:\cs102\exam1'
PATH = os.path.join(BASE_PATH, 'spb_cameras.csv')
POPULATION_PATH = os.path.join(BASE_PATH, 'spb_population_by_district.csv')
CAMERAS_PATH = os.path.join(BASE_PATH, 'cameras_per_district.csv')

df = DataFrame.from_file(PATH)
amount_df = df.group_by('district').sum_by('amount')
amount_df.headers = ['Район', 'Число Камер']
amount_df.to_csv(CAMERAS_PATH)
print(amount_df)
# Район                Число Камер
# -----------------  -------------
# Адмиралтейский               396
# Василеостровский             588
# Выборгский                  3299
# Калининский                 3369
# Кировский                    732
# ...

# ===================================================

amount_df = DataFrame.from_file(CAMERAS_PATH)
pop_df = DataFrame.from_file(POPULATION_PATH)
full_df = amount_df.merge(pop_df, by='Район')
print(full_df)
# Район                Число Камер    Население    Площадь
# -----------------  -------------  -----------  ---------
# Калининский                 3369       538258      40.18
# Выборгский                  3299       509592     115.52
# Фрунзенский                 2787       401410      37.52
# Красногвардейский           2379       357906      56.35
# ...

full_df.headers.append('Плотность')
for row in full_df.rows:
    row.append(float(row[2]) / float(row[3]))

full_df.to_csv('exam_done.csv')
print(full_df)
# Район                Число Камер    Население    Площадь    Плотность
# -----------------  -------------  -----------  ---------  -----------
# Калининский                 3369       538258      40.18      13396.2
# Выборгский                  3299       509592     115.52      4411.29
# ...
