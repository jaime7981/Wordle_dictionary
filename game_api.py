import requests, numpy, os.path, json

BASE_URL = 'https://pds-wordie.herokuapp.com'
PLAYER_KEY = ''

with open('vars/secret_vars.json') as f:
    json_data = json.load(f)
    PLAYER_KEY = json_data['p_key']

#Get Active Games
def ShowGames():
    response = requests.get(f'{BASE_URL}/api/games/')
    games = response.json()['games']
    for g in games:
        print(g)

def GetGamesIds():
    response = requests.get(f'{BASE_URL}/api/games/')
    games = response.json()['games']
    ids_list = []
    for g in games:
        ids_list.append(g['id'])
    return ids_list

def GetOneWordGamesIds():
    response = requests.get(f'{BASE_URL}/api/games/')
    games = response.json()['games']
    ids_list = []
    for g in games:
        if g['words_count'] == 1:
            ids_list.append(g['id'])
    return ids_list

def SelectGame(game_id):
    response = requests.get(f'{BASE_URL}/api/games/')
    games = response.json()['games']
    for g in games:
        if game_id == g['id']:
            return g
        elif game_id == -1:
            print(g)
    return None

def LoadDictionary(language):
    lang_filename = 'static/' + language.split('/')[2]
    if os.path.isfile(lang_filename):
        print ("File exist")
        try:
            f = open(lang_filename)
        except IOError:
            print("File not accessible")
        finally:
            saved_file = list(f)
            counter = 0
            for word in saved_file:
                saved_file[counter] = word.strip('\n')
                counter += 1
            f.close()
            return saved_file
    else:
        print ("File does not exist")
        file_url = f'{BASE_URL}{language}'
        r = requests.get(file_url)
        requests.enconding = 'cp1252'
        text = r.content.decode('cp1252', errors='ignore')
        text_list = text.split('\n')
        words = [w.strip().upper() for w in text_list]
        print('dict length: ' + str(len(words)))
        SaveDisctionary(words, lang_filename)
        return words

def SaveDisctionary(dictionary, name):
    numpy.savetxt(f"{name}", dictionary, delimiter=",", fmt='%s')

def SendWord(game_id, word):
    data = {
        'game': game_id,
        'key': PLAYER_KEY,
        'word': word
    }
    r = requests.post(f'{BASE_URL}/api/play/', data=data)
    print(r.json())
    return r.json()

def ResetGame(game_id):
    data = {
        'game': game_id,
        'key': PLAYER_KEY
    }
    r = requests.post(f'{BASE_URL}/api/reset/', data=data)
    print(r.json())
    return r.json()
