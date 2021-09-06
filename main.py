import datetime
import json
import time

import requests

with open('auth_data.json', 'r') as auth_file:
    auth_data = json.load(auth_file)

access_token = auth_data['access_token']


# Общее количество подписчиков в паблике(определить смещение)
def get_member_count(group_id):
    count = requests.get('https://api.vk.com/method/groups.getMembers', params={
        'access_token': access_token,
        'group_id': group_id,
        'sort': 'id_asc',
        'offset': 0,
        'v': 5.131
    }).json()['response']['count']
    return count


# Список id подписчиков группы
def get_all_members(group_id):
    male_count, female_count, false_count = 0, 0, 0
    member_count = get_member_count(group_id)
    members_list = {'count': member_count, 'male': {'count': male_count, 'items': []},
                    'female': {'count': female_count, 'items': []},
                    'false': {'count': false_count, 'items': []}}
    max_offset = member_count // 1000
    for offset in range(0, max_offset + 1):
        try:  # Блок, чтобы отлавливать ошибки, когда ответ на запрос ошибочный
            r = requests.get('https://api.vk.com/method/groups.getMembers', params={
                'access_token': access_token,
                'group_id': group_id,
                'offset': offset * 1000,
                'fields': 'sex',  # Чтоб разделять аудиторию по полу
                'v': 5.131
            })
            data = r.json()['response']['items']
        except KeyError:
            time.sleep(1)
            offset -= 1
        else:
            for item in data:
                try:  # Мега тупое решение, НО РАБОЧЕЕЕ
                    if item['deactivated']:
                        members_list['false']['items'].append(item['id'])
                except KeyError:
                    try:
                        if item['sex'] == 2:
                            members_list['male']['items'].append(item['id'])
                        else:
                            members_list['female']['items'].append(item['id'])
                    except KeyError:
                        members_list['false']['items'].append(item['id'])
    members_list['male']['count'] = (len(members_list['male']['items']))
    members_list['female']['count'] = (len(members_list['female']['items']))
    members_list['false']['count'] = (len(members_list['false']['items']))
    return members_list


# Получение возраста по id
def get_user_age(user_ids):
    age = 0
    r = requests.get('https://api.vk.com/method/users.get', params={
        'access_token': access_token,
        'user_ids': user_ids,
        'fields': 'bdate',
        'v': 5.131
    })
    try:
        bdate = r.json()['response'][0]['bdate']
    except KeyError:
        pass
    else:
        if len(bdate) > 6:
            age = calculate_age(bdate)
    return age


# Пересечение аудитории
def auditory_intersection(list_of_sets):
    sets_intersection = set.intersection(*list_of_sets)
    return sets_intersection


# Объединение аудитории
def auditory_union(list_of_sets):
    sets_union = set.union(*list_of_sets)
    return sets_union


# Расчет полного возраста
def calculate_age(bdate):
    today = datetime.date.today()
    bdate = datetime.datetime.strptime(bdate, '%d.%m.%Y').date()
    try:
        birthday = bdate.replace(year=today.year)
    except ValueError:
        birthday = bdate.replace(year=today.year, day=bdate.day - 1)
    if birthday > today:
        return today.year - bdate.year - 1
    else:
        return today.year - bdate.year


# Файловый поток в json
def read_from_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data


# Запись json в файл одной строкой
def write_to_file(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)


def main():
    groups_list = ['twchnews', 'streaminside']

    for group in groups_list:
        data_list = get_all_members(group)
        write_to_file(f'{group}.json', data_list)


if __name__ == '__main__':
    main()
