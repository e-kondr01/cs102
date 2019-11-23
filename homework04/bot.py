import datetime
import config
import requests
import telebot

from bs4 import BeautifulSoup
from typing import List, Optional, Tuple


bot = telebot.TeleBot(config.access_token)
telebot.apihelper.proxy = config.proxy

days = {
        '/monday' : '1',
        '/tuesday' : '2',
        '/wednesday' : '3',
        '/thursday' : '4',
        '/friday' : '5',
        '/saturday' : '6',
        '/sunday' : '7',
    }

russian_days = {
        '/monday' : 'Понедельник',
        '/tuesday' : 'Вторник',
        '/wednesday' : 'Среда',
        '/thursday' : 'Четверг',
        '/friday' : 'Пятница',
        '/saturday' : 'Суббота',
        '/sunday' : 'Воскресенье',
    }


def get_day(day: int) -> str:
    #по номеру дня возвращает название
    for n in days.keys():
        if str(day) == days[n]:
            day = n
            break
    return day

def get_page(group: str, week: str='') -> str:
    if week:
        week = str(week) + '/'
    url = f'{config.domain}/{group}/{week}raspisanie_zanyatiy_{group}.htm'
    response = requests.get(url, verify = False)
    web_page = response.text
    return web_page


def parse_schedule(web_page: str, day: str) -> Tuple[List[str], List[str], List[str]]:
    soup = BeautifulSoup(web_page, "html5lib")
    
    num = days[day]
    day = '{}day'.format(num)

    # Получаем таблицу с расписанием
    schedule_table = soup.find("table", attrs={"id": day})

    # Время проведения занятий
    times_list = schedule_table.find_all("td", attrs={"class": "time"})
    times_list = [time.span.text for time in times_list]

    # Место проведения занятий
    locations_list = schedule_table.find_all("td", attrs={"class": "room"})
    locations_list = [room.span.text for room in locations_list]

    # Название дисциплин и имена преподавателей
    lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
    lessons_list = [lesson.text.split('\n\n') for lesson in lessons_list]
    lessons_list = [', '.join([info for info in lesson_info if info]) for lesson_info in lessons_list]

    return times_list, locations_list, lessons_list


@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
def get_schedule(message: str) -> None:
    """ Получить расписание на указанный день """
    day, week, group = message.text.split()
    web_page = get_page(group, week)
    resp = ''
    try:
        times_lst, locations_lst, lessons_lst = parse_schedule(web_page, day)
        for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
            resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)
    except AttributeError:
           resp += 'Занятий нет.'

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['near'])
def get_near_lesson(message):
    """ Получить ближайшее занятие, рассчитывая,
    что у группы есть хотя бы 1 занятие в неделю """
    _, group = message.text.split()
    today = datetime.datetime.today()
    curr_time = today.timetuple()
    curr_hour = curr_time[3]
    curr_minutes = curr_time[4]
    resp = ''
    weekchange = 0
    daycheck = today.isocalendar()[2]

    try:
        day = get_day(daycheck)
        week = str((today.isocalendar()[1] - 35 + weekchange) % 2 + 1)
        web_page = get_page(group, week)    
        times_lst, locations_lst, lessons_lst = parse_schedule(web_page, day)
        for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
            lesson_end_hour = int(time[6:8])
            lesson_end_minutes = int(time[9:])
            if curr_hour < lesson_end_hour:
                resp += '<b>{}</b>\n\n<b>{}</b>, {}, {}\n'.format(russian_days[day], time, location, lession)
                break
            elif curr_hour == lesson_end_hour and curr_minutes < lesson_end_minutes:
                resp += '<b>{}</b>\n\n<b>{}</b>, {}, {}\n'.format(russian_days[day], time, location, lession)
                break
        else:
            while True:
                try:
                    daycheck +=1
                    if daycheck > 7:
                        daycheck = 1
                        weekchange +=1
                    day = get_day(daycheck)
                    week = str((today.isocalendar()[1] - 35 + weekchange) % 2 + 1)
                    web_page = get_page(group, week)    
                    times_lst, locations_lst, lessons_lst = parse_schedule(web_page, day)
                    resp += '<b>{}</b>\n\n<b>{}</b>, {}, {}\n'.format(
                    russian_days[day], times_lst[0], locations_lst[0], lessons_lst[0])
                    break
                except AttributeError:
                    daycheck +=1
                    if daycheck > 7:
                        daycheck = 1
                        weekchange +=1
    except AttributeError:
        while True:
            try:
                daycheck +=1
                if daycheck > 7:
                    daycheck = 1
                    weekchange +=1
                day = get_day(daycheck)
                week = str((today.isocalendar()[1] - 35 + weekchange) % 2 + 1)
                web_page = get_page(group, week)    
                times_lst, locations_lst, lessons_lst = parse_schedule(web_page, day)
                resp += '<b>{}</b>\n\n<b>{}</b>, {}, {}\n'.format(
                russian_days[day], times_lst[0], locations_lst[0], lessons_lst[0])
                break
            except AttributeError:
                daycheck +=1
                if daycheck > 7:
                    daycheck = 1
                    weekchange +=1

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['tommorow'])
def get_tommorow(message):
    """ Получить расписание на следующий день """
    today = datetime.datetime.today().isocalendar()
    day = get_day(today[2] + 1)
    if day == '/sunday':
        day = '/monday'
    if day == '/monday':
        week = str((today[1] - 35 + 1) % 2 + 1)
    else:
        week = str((today[1] - 35) % 2 + 1)
    _, group = message.text.split()
    web_page = get_page(group, week)
    resp = ''
    try:
        times_lst, locations_lst, lessons_lst = parse_schedule(web_page, day)
        for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
            resp += '<b>{}</b>\n\n<b>{}</b>, {}, {}\n'.format(russian_days[day], time, location, lession)
    except AttributeError:
           resp += 'Занятий нет.'

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['all'])
def get_all_schedule(message):
    """ Получить расписание на всю неделю для указанной группы """
    _, week, group = message.text.split()
    resp = ''
    for day in days.keys():
        resp += '<b>{}</b>\n\n'.format(russian_days[day])
        web_page = get_page(group, week)
        try:
            times_lst, locations_lst, lessons_lst = parse_schedule(web_page, day)
        except AttributeError:
            resp += 'Занятий нет.\n\n'
            continue
        for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
            resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


if __name__ == '__main__':
    bot.polling()
