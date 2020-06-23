import pathlib
import datetime
import math


class Task:
    def __init__(self, title, priority, due_date, body):
        self.title = title
        self.priority = priority
        self.due_date = due_date
        self.body = body
        self.info = [self.title, self.priority, self.due_date, self.body]


class TasksParser:
    def __init__(self, path):
        self.path = path
        self.tasks = {}

    def parse(self):
        with self.path.open(mode='r') as f:
            self.lines = f.readlines()
        while self.lines:
            self.parse_date()

    def delete_comments_in_line(self, line, looking_for_comments_start=0):
        while True:
            index = line.find('--', looking_for_comments_start)
            if index == -1:
                break
            check = line[:index].count('"')
            if check % 2 == 0:
                line = line[:index]
                break
            looking_for_comments_start = index + 1
        return line

    def find_skips_in_line(self, line, looking_for_skip_start):
        skip_priority = False
        skip_date = False
        skip_body = False

        while True:
            index = line.find('*', looking_for_skip_start)
            if index == -1:
                break
            check = line[:index].count('"')
            skip_number = int(line[index-1])
            if check == 2:
                if skip_number == 1:
                    skip_priority = True
                if skip_number == 2:
                    skip_priority = True
                    skip_date = True
                if skip_number == 3:
                    skip_priority = True
                    skip_date = True
                    skip_body = True
            if check == 4:
                if skip_number == 1:
                    skip_date = True
                if skip_number == 2:
                    skip_date = True
                    skip_body = True
            if check == 6:
                skip_body = True
            looking_for_skip_start = index + 1
        return skip_priority, skip_date, skip_body

    def parse_date(self):
        date_keyword = False
        task_keyword = False
        tasks = []

        while True:
            '''Parsing date '''
            try:
                line = self.lines.pop(0)
            except IndexError:
                return
            line = line.strip()
            if line == '':
                continue
            if line[0:2] == '--':
                continue
            if line[0:5] == 'DATES':
                date_keyword = True
                continue
            if line[0] == '/':
                if not date_keyword:
                    raise Exception('Wrong date format')
                break
            date = line[:11]
            date = datetime.datetime.strptime(date, '%d %b %Y')
            date = date.strftime('%d.%m.%Y')

        while True:
            '''Parsing tasks '''
            try:
                line = self.lines.pop(0)
            except IndexError:
                break
            line = line.strip()
            if line == '':
                continue
            if line[0:2] == '--':
                continue
            if line[0:4] == 'TASK':
                task_keyword = True
                continue
            if line[0] == '/':
                if not task_keyword:
                    raise Exception('Wrong task format')
                continue

            if line[0:5] == 'DATES':
                self.lines.insert(0, line)
                break

            priority = math.inf
            due_date = None
            body = ''

            block_start = line.find('"')
            block_end = line.find('"', block_start+1)
            title = line[block_start+1:block_end]

            line = self.delete_comments_in_line(line, block_end)

            skip_priority, skip_date, skip_body = self.find_skips_in_line(line, block_end)

            if not skip_priority:
                priority_end = line.find('"', block_end+1)
                if priority_end == -1:
                    priority_end = line.find('/', block_end+1)
                priority = line[block_end+1: priority_end]
                priority = int(priority.replace(' ', ''))

            if not skip_date:
                block_start = line.find('"', block_end+1)
                block_end = line.find('"', block_start+1)
                due_date = line[block_start+1:block_end]
                due_date = datetime.datetime.strptime(due_date, '%d %b %Y')
                due_date = due_date.strftime('%d.%m.%Y')

            if not skip_body:
                block_start = line.find('"', block_end+1)
                block_end = line.find('"', block_start+1)
                body = line[block_start+1:block_end]

            if '/' in line[block_end+1:]:
                task = Task(title=title, priority=priority,
                            due_date=due_date, body=body)
                tasks.append(task)
            else:
                raise Exception('Wrong task format')

        self.tasks[date] = tasks


def main():
    path = pathlib.Path('.') / "exam41.sch"
    parser = TasksParser(path)
    parser.parse()
    tasks = parser.tasks
    print(tasks)
    for task in tasks['23.06.2020']:
        print('date:  23.06.2020')
        print(task.info)
    for task in tasks['24.06.2020']:
        print('date:  24.06.2020')
        print(task.info)
    assert len(tasks["23.06.2020"]) == 3
    assert tasks["23.06.2020"][1].title == "New task 2"
    assert tasks["23.06.2020"][1].priority == 2
    assert tasks["23.06.2020"][1].due_date == "25.06.2020"
    assert tasks["23.06.2020"][1].body == ""
    #assert tasks["23.06.2021"] == []


if __name__ == '__main__':
    main()
