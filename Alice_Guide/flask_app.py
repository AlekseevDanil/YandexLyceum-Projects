from flask import Flask, request
import logging
import json
import random
import db_cities
from geo import get_country, get_distance, get_coordinates
from trans_lg import detect_lg, translate_lg
import count_lg

app = Flask(__name__)
logging.basicConfig(level=logging.INFO,
                    filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

# создаём словарь, где для каждого пользователя мы будем хранить его имя
sessionStorage = {}

# список ответов на вопрос как дела
happ = ['Просто чудесно',
        'Всё нормально, спасибо, что интересуетесь',
        'Очень хорошо!',
        'Мои дела - ваши дела',
        'Для меня личные дела это роскошь, я занимаюсь только вашими',
        'Как никогда хорошо. Спасибо!',
        'Всё в порядке.',
        'Дело у меня одно - помогать вам. И как оно, решать тоже вам.',
        'Порядок!',
        'Голова пока цела! Имею в виду процессор.',
        'В порядке... В случайном',
        'Как в сказке - чем дальше, тем интереснее!']

# список ответов на привет
hello = ['Привет!',
         'Здравствуйте',
         'Чем я могу помочь?',
         'И вам здравствуйте',
         'Здоровались!',
         'Да?',
         'Я вас слушаю...',
         'Добрый день!',
         'Приветствую тебя землянин!',
         'Nani?',
         'Привет! Вы меня искали?',
         'Здравствуйте! Вы меня звали и вот я здесь!',
         'Приветики',
         'Хай']

# словарь всех используемых фото
photos = {'alica': '997614/4cacde76baaf6db69245',
          'alica_city_game': '1030494/864cf1dd75f2b04999fd',
          'alica_distance_city_game': '213044/0472791be4c29ad3d526',
          'alica_country_game': '1652229/4ed9926117d97e5db304',
          'alica_trans_lg': '1540737/b9b01650cbbf5b89fcca',
          'alica_search_lg': '997614/6e3104d429a2560278c3',
          'alica_ya_serch': '937455/bf53cda6186ec05fbd1e'}

# переменные
cities = db_cities.CITIES
random.shuffle(cities)
used_cities = []

# все навыки
city_game = [False, '']
distance_city_game = False
country_game = False
trans_lg = False
search_lg = False
ya_serch = False


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    global photos
    user_id = req['session']['user_id']

    # если пользователь новый, то просим его представиться.
    if req['session']['new']:
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = 'Привет! Я Алиса.Гид,'\
                                           + ' а тебя как зовут?'
        res['response']['card']['image_id'] = photos['alica']
        # текст если нету экрана
        res['response']['text'] = 'Привет! Я Алиса-Гид,'\
                                  + ' а тебя как зовут?'
        # создаём словарь в который в будущем положим имя пользователя
        sessionStorage[user_id] = {
            'first_name': None
        }
        return

    # если пользователь не новый, то попадаем сюда.
    # если поле имени пустое, то это говорит о том,
    # что пользователь ещё не представился.
    if sessionStorage[user_id]['first_name'] is None:
        # в последнем его сообщение ищем имя.
        first_name = get_first_name(req)
        # если не нашли, то сообщаем пользователю что не расслышали.
        if first_name is None:
            res['response']['text'] = \
                'Не расслышала имя. Повтори, пожалуйста!'
        # если нашли, то приветствуем пользователя
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response'][
                'text'] = 'Приятно познакомиться, ' + first_name.title()\
                          + '.\nВот что я умею:\n1. Играть в горо'\
                          + 'да (Просто скажите: "Давай сыграем в города")\n'\
                          + '2. Найти точное расстаяние между городами '\
                          + '(Просто скажите: "Отмерь расстояние")\n'\
                          + '3. Найти в какой стране город '\
                          + '(Просто скажите: "В какой стране город?")\n'\
                          + '4. Перевести на любой язык '\
                          + '(Просто скажите: "Перевод")\n'\
                          + '5. Определить язык '\
                          + '(Просто скажите: "Определи язык")\n'\
                          + '6. Произвести поиск '\
                          + '(Просто скажите: "Поиск")'

    else:
        # преобразовываем все нужные переменные в глобальные
        global city_game
        global used_cities
        global cities
        global distance_city_game
        global country_game
        global trans_lg
        global language
        global translate_lg
        global search_lg
        global detect_lg
        global ya_serch
        global happ
        global hello

        # ИГРА В ГОРОДА
        if 'давай сыграем в города' in req['request']['command'].lower():
            city_game = [True, 'а']
            # фотография Алисы с тайтлами
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = '*Чтобы прекратить игру напиш'\
                                               + 'ите Хватит* Я начну, Москв'\
                                               + 'а - тебе на "а"'
            res['response']['card']['image_id'] = photos['alica_city_game']
            # текст если нету экрана
            res['response']['text'] = '*Чтобы прекратить игру напишите Хвати'\
                                      + 'т* Я начну, Москва - тебе на "а"'
            res['response']['buttons'] = [{'title': 'Хватит',
                                           'hide': True}]
        elif city_game[0] is True:
            if 'где это' in req['request']['command'].lower():
                res['response']['text'] = 'Это замечательное место. Ваш ход...'
                res['response']['buttons'] = [{'title': 'Хватит',
                                               'hide': True}]
            elif 'хватит' in req['request']['command'].lower():
                res['response']['text'] = 'С тобой было приятно играть!\n'\
                                          + '-Если хочешь узнать, что я могу,'\
                                          + ' напиши: "Что ты можешь?" '
                city_game = [False, '']
                used_cities = []
            elif sorted(cities) == sorted(used_cities):
                res['response']['text'] = 'С тобой приятно играть, но я устал'\
                                          + 'а!\n-Если хочешь узнать, что '\
                                          + 'я могу, напиши: "Что ты можешь?"'
                city_game = [False, '']
                used_cities = []
            elif city_game[1] == req['request']['command'].lower()[0]:
                if req['request']['command'].lower().title() in used_cities:
                    res['response']['text'] = 'Повторяться нельзя!\nТы проиг'\
                                          + 'рал. Но ничего в следующий раз '\
                                          + 'обязательно всё получится!\n'\
                                          + '-Если хочешь узнать, что я могу,'\
                                          + ' напиши: "Что ты можешь?" '
                    city_game = [False, '']
                    used_cities = []
                elif req['request']['command'].lower().title() not in cities:
                    res['response']['text'] = 'Такого города я не знаю!\nКа'\
                                          + 'жется ты проиграл. Но ничего в с'\
                                          + 'ледующий раз обязательно всё пол'\
                                          + 'учится!\n-Если хочешь узнать, чт'\
                                          + 'о я могу, напиши:"Что ты можешь?"'
                    city_game = [False, '']
                    used_cities = []
                else:
                    word = req['request']['command'].lower().title()
                    used_cities.append(word)
                    if req['request']['command'].lower()[-1] != 'ь'\
                       and req['request']['command'].lower()[-1] != 'ъ'\
                       and req['request']['command'].lower()[-1] != 'ы':
                        city_game[1] = req['request']['command'].lower()[-1]
                    else:
                        city_game[1] = req['request']['command'].lower()[-2]
                    for i in cities:
                        if i[0].lower() == city_game[1].lower()\
                           and i not in used_cities:
                            used_cities.append(i)
                            res['response']['text'] = str(i)
                            city_n = str(i)
                            if i[-1] != 'ь'\
                               and i[-1] != 'ъ'\
                               and i[-1] != 'ы':
                                city_game[1] = i[-1]
                            else:
                                city_game[1] = i[-2]
                            break
                    url = 'https://yandex.ru/maps/?ll=86.026101%2C46.958498&m'\
                          + 'ode=search&sll=52.395874%2C55.743583&sspn=0.3137'\
                          + '97%2C0.105549&text={}&z=2.7'.format(city_n)
                    res['response']['buttons'] = [{'title': 'Где это?',
                                                   'hide': True,
                                                   'url': url},
                                                  {'title': 'Хватит',
                                                   'hide': True}]
            else:
                res['response']['text'] = 'Упс... Кажется ты проиграл\n'\
                                          + 'Но ничего в следующий раз '\
                                          + 'обязательно всё получится!\n'\
                                          + '-Если хочешь узнать, что я могу,'\
                                          + ' напиши: "Что ты можешь?" '
                city_game = [False, '']
                used_cities = []

        # НАХОЖДЕНИЕ РАССТОЯНИЯ ГОРОДОВ
        elif 'отмерь расстояние' in req['request']['command'].lower():
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = '*Чтобы прекратить напишите '\
                                               + 'Хватит* Каких двух городо'\
                                               + 'в нужно узнать расстояние'\
                                               + '? (Пример: Москва Питер)'
            name_photo = 'alica_distance_city_game'
            res['response']['card']['image_id'] = photos[name_photo]
            distance_city_game = True
            # текст если нету экрана
            res['response']['text'] = '*Чтобы прекратить напишите Хватит*'\
                                      + '\nКаких двух городов нужно узнать'\
                                      + ' расстояние?\n (Пример: Москва Питер)'
            res['response']['buttons'] = [{'title': 'Хватит',
                                           'hide': True}]
        elif distance_city_game is True:
            cities_d = get_cities(req)
            if 'хватит' in req['request']['command'].lower():
                res['response']['text'] = 'Закончили!\n'\
                                          + '-Если хочешь узнать, что я могу,'\
                                          + ' напиши: "Что ты можешь?" '
                distance_city_game = False
            elif len(cities_d) == 0:
                res['response']['text'] = 'Ты не написал название'\
                                          + ' не одного города!'
                res['response']['buttons'] = [{'title': 'Хватит',
                                               'hide': True}]
            elif len(cities_d) == 2:
                distance = get_distance(get_coordinates(cities_d[0]),
                                        get_coordinates(cities_d[1]))
                res['response']['text'] = 'Расстояние между этими городами: '\
                                          + str(round(distance)) + ' км.\n'\
                                          + '-Если хочешь узнать, что я могу,'\
                                          + ' напиши: "Что ты можешь?" '
                distance_city_game = False
            else:
                res['response']['text'] = 'Не то количество городов!\n'\
                                          + 'Попробуй ещё раз.'
                res['response']['buttons'] = [{'title': 'Хватит',
                                               'hide': True}]

        # В КАКОЙ СТРАНЕ ГОРОД
        elif 'в какой стране город' in req['request']['command'].lower():
            country_game = True
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = '*Чтобы прекратить напишите '\
                                               + 'Хватит* Какого города нуж'\
                                               + 'но узнать страну?'
            res['response']['card']['image_id'] = photos['alica_country_game']
            # текст если нету экрана
            res['response']['text'] = '*Чтобы прекратить напишите Хватит*'\
                                      + '\nКакого города нужно узнать страну?'
            res['response']['buttons'] = [{'title': 'Хватит',
                                           'hide': True}]
        elif country_game is True:
            cities_d = get_cities(req)
            if 'хватит' in req['request']['command'].lower():
                res['response']['text'] = 'Закончили!\n'\
                                          + '-Если хочешь узнать, что я могу,'\
                                          + ' напиши: "Что ты можешь?" '
                country_game = False
            elif len(cities_d) == 0:
                res['response']['text'] = 'Ты не написал название города!'
                res['response']['buttons'] = [{'title': 'Хватит',
                                               'hide': True}]
            elif len(cities_d) == 1:
                res['response']['text'] = 'Этот город в стране - '\
                                          + get_country(cities_d[0])\
                                          + '\n-Если хочешь узнать, что я '\
                                          + 'могу, напиши: "Что ты можешь?" '
                country_game = False
            else:
                res['response']['text'] = 'Слишком много городов!\n'\
                                          + 'Попробуй ещё раз.'
                res['response']['buttons'] = [{'title': 'Хватит',
                                               'hide': True}]

        # ПЕРЕВОДЧИК
        elif 'перевод' == req['request']['command'].lower():
            trans_lg = True
            language = ''
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = '*Чтобы прекратить напишите '\
                                               + 'Хватит* На какой язык пер'\
                                               + 'евести? Если вы не знаете'\
                                               + ' язык в какой-то стране, '\
                                               + 'напиши страну, я помогу!'
            res['response']['card']['image_id'] = photos['alica_trans_lg']
            # текст если нету экрана
            res['response']['text'] = '*Чтобы прекратить напишите Хватит*'\
                                      + '\nНа какой язык вы хотите перевести?'\
                                      + '\nЕсли вы не знаете язык в какой-то '\
                                      + 'стране, напиши страну, я тебе помогу!'
            res['response']['buttons'] = [{'title': 'Хватит',
                                           'hide': True}]
        elif trans_lg is True:
            word = req['request']['command'].lower().strip().title()
            if 'хватит' in req['request']['command'].lower():
                res['response']['text'] = 'Закончили!\n'\
                                          + '-Если хочешь узнать, что я могу,'\
                                          + ' напиши: "Что ты можешь?" '
                trans_lg = False
            elif word in count_lg.COUNTRY_LG:
                ans = req['request']['command'].lower().strip().title()
                ans = count_lg.COUNTRY_LG[ans]
                ans = count_lg.SIM_LG[ans]
                language = count_lg.LG_SIM[ans]
                res['response']['text'] = 'Я определила язык, это - ' + ans\
                                          + '\nЧто вы хотите перевести?'
                res['response']['buttons'] = [{'title': 'Хватит',
                                               'hide': True}]
            elif req['request']['command'].lower().strip() in count_lg.LG_SIM:
                res['response']['text'] = 'Что вы хотите перевести?'
                ans = req['request']['command'].lower().strip()
                language = count_lg.LG_SIM[ans]
                res['response']['buttons'] = [{'title': 'Хватит',
                                               'hide': True}]
            elif language == '':
                res['response']['text'] = 'Не понимаю! Попробуйте ещё раз...'
                res['response']['buttons'] = [{'title': 'Хватит',
                                               'hide': True}]
            else:
                text = str(req['request']['command'])
                res['response']['text'] = 'Перевод: ' + str(
                    translate_lg(text, language))
                res['response']['buttons'] = [{'title': 'Хватит',
                                               'hide': True}]

        # ОПРЕДЕЛЕНИЕ ЯЗЫКА
        elif 'определи язык' == req['request']['command'].lower():
            search_lg = True
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = '*Чтобы прекратить напишите '\
                                               + 'Хватит* Напишите что-нибу'\
                                               + 'дь, а я определю, что за'\
                                               + ' язык!'
            res['response']['card']['image_id'] = photos['alica_search_lg']
            # текст если нету экрана
            res['response']['text'] = '*Чтобы прекратить напишите Хватит*'\
                                      + '\nНапишите что-нибудь, '\
                                      + 'а я определю, что за язык!'
            res['response']['buttons'] = [{'title': 'Хватит',
                                           'hide': True}]
        elif search_lg:
            if 'хватит' in req['request']['command'].lower():
                res['response']['text'] = 'Закончили!\n'\
                                          + '-Если хочешь узнать, что я могу,'\
                                          + ' напиши: "Что ты можешь?" '
                search_lg = False
            else:
                text = str(req['request']['command'])
                ans = detect_lg(text)
                ans = count_lg.SIM_LG[ans]
                res['response']['text'] = 'Я знаю! Это -' + ans\
                                          + '\nНапиши что-нибудь ещё!'
                res['response']['buttons'] = [{'title': 'Хватит',
                                               'hide': True}]

        # ПОИСК
        elif 'поиск' == req['request']['command'].lower():
            ya_serch = True
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = '*Чтобы прекратить напишите'\
                                               + ' Хватит* Напишите что ну'\
                                               + 'жно найти, после нажмите'\
                                               + ' кнопку "Искать"!'
            res['response']['card']['image_id'] = photos['alica_ya_serch']
            # текст если нету экрана
            res['response']['text'] = '*Чтобы прекратить напишите Хватит*'\
                                      + '\nНапишите что нужно найти, '\
                                      + 'после нажмите кнопку "Искать"!'
            res['response']['buttons'] = [{'title': 'Хватит',
                                           'hide': True}]
        elif ya_serch:
            if 'хватит' in req['request']['command'].lower():
                res['response']['text'] = 'Закончили искать!\n'\
                                          + '-Если хочешь узнать, что я могу,'\
                                          + ' напиши: "Что ты можешь?" '
                ya_serch = False
            elif 'нет' == req['request']['command'].lower():
                res['response']['text'] = 'Попробуйте искать по другому'\
                                          + ' запросу...'
                res['response']['buttons'] = [{'title': 'Хватит',
                                               'hide': True}]
            elif 'да' == req['request']['command'].lower():
                res['response']['text'] = 'Отлично!\n'\
                                          + '-Если хочешь узнать, что я могу,'\
                                          + ' напиши: "Что ты можешь?" '
                ya_serch = False
            elif 'искать' == req['request']['command'].lower():
                res['response']['text'] = 'Нашли что хотели?'
                res['response']['buttons'] = [{'title': 'Да',
                                               'hide': True},
                                              {'title': 'Нет',
                                               'hide': True},
                                              {'title': 'Хватит',
                                               'hide': True}]
            else:
                ans = '%20'.join(req['request']['command'].split())
                url = 'https://yandex.ru/search/?text={}&lr=236'.format(ans)
                res['response']['buttons'] = [{'title': 'Искать',
                                               'hide': True,
                                               'url': url},
                                              {'title': 'Хватит',
                                               'hide': True}]
                res['response']['text'] = 'Произвожу поиск...'

        # СПОНТАННОЕ ПРИВЕТСТВИЕ
        elif 'привет' == req['request']['command'].lower()\
             or 'здравствуй' == req['request']['command'].lower()\
             or 'здравствуйте' == req['request']['command'].lower()\
             or 'хай' == req['request']['command'].lower()\
             or 'хеллоу' == req['request']['command'].lower():
            answer = str(random.choice(hello))
            res['response']['text'] = answer

        # СПОНТАННО СТРОСИЛИ КАК ДЕЛА
        elif 'как дела?' in req['request']['command'].lower()\
             or 'как дела' in req['request']['command'].lower()\
             or 'как у тебя дела?' in req['request']['command'].lower()\
             or 'как у тебя дела' in req['request']['command'].lower():
            answer = str(random.choice(happ))
            res['response']['text'] = answer

        # ЕСЛИ НЕТ ПОДХОДЯЩЕГО НАВЫКА ИЛИ ОТВЕТА НА ЗАПРОС
        else:
            res['response']['text'] = 'Я могу:\n1. Играть в города (Просто'\
                                      + ' скажите: "Давай сыграем в города'\
                                      + '")\n2. Найти точное расстаяние ме'\
                                      + 'жду городами (Просто скажите: "От'\
                                      + 'мерь расстояние")\n3. Найти в как'\
                                      + 'ой стране город (Просто скажите: '\
                                      + '"В какой стране город?")\n4. Пере'\
                                      + 'вести на любой язык (Просто скажи'\
                                      + 'те: "Перевод")\n5. Определить язы'\
                                      + 'к (Просто скажите: "Определи язык'\
                                      + '")\n6. Произвести поиск (Просто с'\
                                      + 'кажите: "Поиск")'


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


def get_cities(req):
    cities = []
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value'].keys():
                cities.append(entity['value']['city'])
    return cities


if __name__ == '__main__':
    app.run()
