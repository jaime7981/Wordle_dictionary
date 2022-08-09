import game_api, random, re

#GAME_ID = 33
turns = 1
used_words = []

def ResetGlobalVars():
    global turns, used_words
    turns = 1
    used_words = []

def main_game(game_id):
    global turns
    selected_game = game_api.SelectGame(game_id)

    if selected_game != None:
        #game data
        word_length = selected_game['word_length']
        words_count = selected_game['words_count']
        game_dictionary = game_api.LoadDictionary(selected_game['language'])

        #dict processing
        game_dictionary = basic_filter(game_dictionary, word_length)
        game_chars = character_analyzer(game_dictionary)
        
        first_word = SetFirstWord(game_dictionary, word_length, game_chars)
        first_word = first_word[random.randint(0, len(first_word) - 1)]
        used_words.append(first_word)
        
        #play game
        response = FirstTurn(first_word, id)

        #Para multiples palabras usar dos dimensiones de letras usadas
        used_letters = []
        found_positions = []
        posible_letters = []
        
        for char in range(word_length):
            found_positions.append('.')

        Play(game_dictionary, response, first_word, used_letters, found_positions, posible_letters, id)
        return turns


def basic_filter(game_dictionary, word_length):
    new_dict = []
    for word in game_dictionary:
        if len(word) == word_length:
            new_dict.append(word)
    return new_dict

def character_analyzer(game_dictionary):
    char_analyzer = {}
    for word in game_dictionary:
        for letter in word:
            if letter not in char_analyzer:
                char_analyzer[letter] = 1
            else:
                char_analyzer[letter] += 1
    char_analyzer = dict(sorted(char_analyzer.items(), key=lambda x: x[1], reverse=True))
    print(char_analyzer)
    return char_analyzer

#Depending on the api response, clasify diferent results for each letter
def AnalizeResponseChars(result_list, last_word_list, used_letters, found_positions, posible_letters):
    for position in range(len(result_list)):
        letter = last_word_list[position]
        result = result_list[position]

        if result == '0':
            if letter not in used_letters:
                used_letters.append(letter)
        elif result == '2':
            found_positions[position] = letter
            if letter not in posible_letters:
                posible_letters.append(letter)
        elif result == '1':
            if letter not in posible_letters:
                posible_letters.append(letter)

def SetFirstWord(game_dictionary, word_length, characters):
    key_list = list(characters.keys())
    first_results = []
    aux_list = []
    first_letter = True

    for iterator in range(len(key_list)):
        if iterator <= len(key_list):
            if first_letter == True:
                for words in game_dictionary:
                    if key_list[iterator] in words:
                        first_results.append(words)
                first_letter = False
            else:
                for words in first_results:
                    if key_list[iterator] in words:
                        aux_list.append(words)
                if len(aux_list) > 1:
                    first_results = aux_list
                else:
                    break
                aux_list = []
        else:
            break
    
    print('Best List: ' + str(first_results))

    return first_results

def PickNewWord(game_dictionary, used_letters, found_positions, posible_letters, word_length):
    regex = ''.join(found_positions)
    posible_words = []
    aux_list = []

    #Regex con posiciones encontradas
    for words in game_dictionary:
        x = re.findall(regex, words)
        if len(x) > 0:
            posible_words.append(x[0])

    #Letras que estan en la palabra
    for letters in posible_letters:
        for words in posible_words:
            if letters in words:
                if words not in aux_list:
                    aux_list.append(words)
        if len(aux_list) > 0:
            posible_words = aux_list
        aux_list = []

    #letras que no pueden estar en las palabras
    for letters in used_letters:
        for words in posible_words:
            if letters not in words:
                if words not in aux_list:
                    aux_list.append(words)
        if len(aux_list) > 0:
            posible_words = aux_list
        aux_list = []

    #eliminar palabras usadas
    for used_word in used_words:
        if used_word in posible_words:
            posible_words.remove(used_word)

    #Agregar analizis de diccionario
    new_game_dict = character_analyzer(posible_words)

    #Agregar escoger palabra mas probable de que salga
    posible_next_word = SetFirstWord(posible_words, word_length, new_game_dict)

    return posible_next_word

def FirstTurn(first_word, game_id):
    global turns
    print('\nturn: ' + str(turns))
    print(first_word)
    response = game_api.SendWord(game_id, first_word)

    finished = response['finished']
    if finished == True:
        print('game ended')
        print(used_words)
        game_api.ResetGame(game_id)
        exit()
    else:
        turns += 1
        return response

def Play(game_dictionary, response, last_word, used_letters, found_positions, posible_letters, game_id):    
    global turns
    result = response['result'][0]

    AnalizeResponseChars(list(result), list(last_word), used_letters, found_positions, posible_letters)

    new_selected_word = PickNewWord(game_dictionary, used_letters, found_positions, posible_letters, len(last_word))
    new_selected_word = new_selected_word[random.randint(0, len(new_selected_word) - 1)]
    used_words.append(new_selected_word)

    response = game_api.SendWord(game_id, new_selected_word)

    for info in [('\nturn: ' + str(turns)), found_positions, posible_letters, used_letters, new_selected_word, response]:
        print(info)

    if response['finished'] == True:
        print('game ended')
        print(used_words)
        game_api.ResetGame(game_id)
    else:
        turns += 1
        Play(game_dictionary, response, new_selected_word, used_letters, found_positions, posible_letters, id)

if __name__ == '__main__':
    ids_list = game_api.GetOneWordGamesIds()
    game_count = 1

    for id in ids_list:
        print('game count: ', game_count)
        print('game id: ', id)
        turns_result = main_game(id)

        print('Total game turns:', turns_result, '\n')
        game_count += 1
        ResetGlobalVars()

    exit()