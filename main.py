import datetime
import json
import time
import os

import requests

with open('auth_data.json', 'r') as auth_file:
    auth_data = json.load(auth_file)

access_token = auth_data['access_token']


# Общее количество подписчиков в паблике(определить смещение)
def get_member_count(group_id):
    try:
        count = requests.get('https://api.vk.com/method/groups.getMembers', params={
            'access_token': access_token,
            'group_id': group_id,
            'sort': 'id_asc',
            'offset': 0,
            'v': 5.131
        }).json()['response']['count']
    except Exception as ex:
        print('[ERROR] Next try after 500ms!')
        time.sleep(0.5)
        get_member_count(group_id)
    else:
        return count


# Список id подписчиков группы
def get_all_members(group_id):
    member_count = get_member_count(group_id)
    members_list = {'count': member_count, 'male': {'count': 0, 'items': []},
                    'female': {'count': 0, 'items': []},
                    'false': {'count': 0, 'items': []}}
    offset, max_offset = 0, member_count // 1000
    while offset < max_offset + 1:
        try:  # Блок, чтобы отлавливать ошибки, когда ответ на запрос ошибочный
            r = requests.get('https://api.vk.com/method/groups.getMembers', params={
                'access_token': access_token,
                'group_id': group_id,
                'offset': offset * 1000,
                'fields': 'sex, photo_max_orig',  # Чтоб разделять аудиторию по полу
                'v': 5.131
            })
            data = r.json()['response']['items']
        except Exception as ex:
            print('[ERROR] Next try after 500ms!')
            time.sleep(0.5)
        else:
            for item in data:
                try:
                    if item['deactivated'] == 'deleted' or item['deactivated'] == 'banned':
                        members_list['false']['items'].append(item['id'])
                except KeyError:
                    try:
                        if item['sex'] == 2:
                            members_list['male']['items'].append(item['id'])
                        elif item['sex'] == 1:
                            members_list['female']['items'].append(item['id'])
                            if item['photo_max_orig'][-5:] == 'ava=1':
                                download_image(item['id'], item['photo_max_orig'])
                        else:
                            members_list['false']['items'].append(item['id'])
                    except KeyError:
                        members_list['false']['items'].append(item['id'])
            offset += 1
    members_list['male']['count'] = (len(members_list['male']['items']))
    members_list['female']['count'] = (len(members_list['female']['items']))
    members_list['false']['count'] = (len(members_list['false']['items']))
    return members_list


# Получение информации о пользователе по id
def get_users(user_ids, fields):
    offsets_list, data = [], []
    for i in range(0, len(user_ids), 10):
        offsets_list.append(user_ids[i: 10 + i])

    for offset in offsets_list:
        try:
            r = requests.get('https://api.vk.com/method/users.get', params={
                'access_token': access_token,
                'user_ids': offset,
                'fields': fields,
                'v': 5.131
            }, timeout=5)
            print(r.json())
            items = r.json()['response']
        except KeyError:
            print('[ERROR] Next try after 500ms!')
            print(len(data))
            t
            get_member_count(user_ids)
        else:
            for item in items:
                data.append(item)
    return data


def download_image(user_id, photo_url):
    try:
        r = requests.get(photo_url, stream=True)
        image_content = r.content
    except Exception as ex:
        print('[ERROR] Next try after 500ms!')
        time.sleep(0.5)
    else:
        if not os.path.exists('D:/images'):
            os.mkdir('D:/images')
        with open(f'D:/images/{user_id}.jpg', 'wb') as image:
            image.write(image_content)
    pass


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
    group_list = ['mirea_official', 'mirealab', 'sumirea']
    females = []
    for group in group_list:
        females.append(set(get_all_members(group)['female']['items']))
    data = list(auditory_union(females))
    # with open('females.txt', 'w') as file:
    #     for id in list(data):
    #         file.write(str(id) + '\n')
    # data = []
    # with open('females.txt', 'r') as file:
    #     for id in file:
    #         data.append(id[:-1])
    # print(len(data))
    # #get_users('levjke, 23123', 'bdate')
    # users_data = get_users(", ".join(data), 'photo_max_orig')
    # print(users_data)




if __name__ == '__main__':
    main()
