DATES -- важно
 23 JUN 2020 -- отметить
/ -- что могут быть комментарии


TASK
-- title    priority due date       body
 "New task 1" 1        "24 JUN 2020"  "Task body -- а это нет" / -- это комментарий
 "New task 2" 2        "25 JUN 2020"  "" /
/

-- raise ValueError(f"Невозможно разобрать строку {line}")

TASK
-- title    priority due date       body
 "New task" 3* /
-- "New task" 1        "24 JUN 2020"  "" -- а тут закомментировали всю строку
/

DATES
  24 JUN 2020
/

TASK
-- title    priority due date       body
 "New task" 1*        "30 JUN 2020"  "" /
/

TASK
-- title    priority due date       body
 "New task" 2* "kek" /
/

-- attr/default values:
-- title: required[str]
-- created: required[str]
-- priority: float("inf")
-- due_date: None
-- body: ""

-- Output:
-- tasks["23.06.2020"][1].title -> New task 2 (str)
-- tasks["23.06.2020"][1].priority -> 2 (float)
-- tasks["23.06.2021"] -> []
