import game_api, random, time, re

#If GAME_ID == -1 show all games
GAME_ID = 4
turns = 1
used_words = []

def main():
    total_time = 0
    time_init = time.time()
    
    selected_game = game_api.SelectGame(GAME_ID)

    time_interval = time.time() - time_init
    total_time += time_interval
    print('api request time: ' + str(time_interval))

    if selected_game != None:
        #game data
        time_init = time.time()

        word_length = selected_game['word_length']
        words_count = selected_game['words_count']
        game_dictionary = game_api.LoadDictionary(selected_game['language'])
        
        time_interval = time.time() - time_init
        total_time += time_interval
        print('api get dict time: ' + str(time_interval))

        #dict processing
        time_init = time.time()

        game_dictionary = basic_filter(game_dictionary, word_length)
        game_chars = character_analyzer(game_dictionary)
        
        first_word = SetFirstWord(game_dictionary, word_length, game_chars)
        print('first word guess: ' + first_word)
        used_words.append(first_word)
        
        time_interval = time.time() - time_init
        total_time += time_interval
        print('word pre procesing time: ' + str(time_interval))

        #play game
        time_init = time.time()
        
        response = FirstTurn(first_word)

        time_interval = time.time() - time_init
        total_time += time_interval
        print('first turn time: ' + str(time_interval))

        time_init = time.time()

        #Para multiples palabras usar dos dimensiones de letras usadas
        used_letters = []
        found_positions = []
        posible_letters = []
        
        for char in range(word_length):
            found_positions.append('.')

        response = Play(game_dictionary, response, first_word, used_letters, found_positions, posible_letters)

        time_interval = time.time() - time_init
        total_time += time_interval
        print('second turn time: ' + str(time_interval))
        print('total time: ' + str(total_time))

def basic_filter(game_dictionary, word_length):
    new_dict = []
    for word in game_dictionary:
        if len(word) == word_length:
            new_dict.append(word)
    print('word length filter: ' + str(len(new_dict)))
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
        elif result == '1':
            if letter not in posible_letters:
                posible_letters.append(letter)

def SetFirstWord(game_dictionary, word_length, characters):
    key_list = list(characters.keys())
    first_results = []
    aux_list = []
    first_letter = True

    for iterator in range(word_length):
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
    print('first best len: ' + str(len(first_results)))
    print('first best list: ' + str(first_results))

    return first_results[random.randint(0, len(first_results) - 1)]

def PickNewWord(game_dictionary, used_letters, found_positions, posible_letters):
    regex = ''.join(found_positions)
    posible_words = []
    aux_list = []

    #Regex con posiiciones encontradas
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

    print(len(posible_words))

    return(posible_words[random.randint(0, len(posible_words) - 1)])
    

def FirstTurn(first_word):
    global turns
    print('turn: ' + str(turns))
    response = game_api.SendWord(GAME_ID, first_word)

    finished = response['finished']
    if finished == True:
        print('game ended')
        print(used_words)
        game_api.ResetGame(GAME_ID)
        exit()
    else:
        turns += 1
        return response

def Play(game_dictionary, response, last_word, used_letters, found_positions, posible_letters):    
    global turns
    print('turn: ' + str(turns))
    result = response['result'][0]

    AnalizeResponseChars(list(result), list(last_word), used_letters, found_positions, posible_letters)

    print(found_positions)
    print(posible_letters)
    print(used_letters)

    new_selected_word = PickNewWord(game_dictionary, used_letters, found_positions, posible_letters)
    print(new_selected_word)
    used_words.append(new_selected_word)
    response = game_api.SendWord(GAME_ID, new_selected_word)

    print(response)

    if response['finished'] == True:
        print('game ended')
        print(used_words)
        game_api.ResetGame(GAME_ID)
        exit()
    else:
        turns += 1
        Play(game_dictionary, response, new_selected_word, used_letters, found_positions, posible_letters)
        print('Recursive turn')

if __name__ == '__main__':
    main()