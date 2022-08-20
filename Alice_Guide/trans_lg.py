import requests

API_KEY = 'trnsl.1.1.20190417T155546Z.bd929d1aedabb'\
          + '54b.ca20b327a7ccf88b6565b12eb1a144a04ac61bbb'


def detect_lg(text):
    api_server = "https://translate.yandex.net/api/v1.5/tr.json/detect"
    api_params = {"key": API_KEY,
                  "text": text}
    response = requests.get(api_server, params=api_params)
    return eval(response.content.decode())['lang']


def translate_lg(text, language):
    api_server = "https://translate.yandex.net/api/v1.5/tr.json/translate"
    api_params = {"key": API_KEY,
                  "text": text,
                  "lang": language}
    response = requests.get(api_server, params=api_params)
    return eval(response.content.decode())['text'][0]
