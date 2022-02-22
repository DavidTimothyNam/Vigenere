
# Rename this to something like "vignere_functions.py" and 
# change the import statement in __main__ 

from frequencies import letter_frequencies, all_bigram_freq

alphabet = "abcdefghijklmnopqrstuvwxyz"

def caesar_decrypt(ciphertext, key):
    temp_ciphertext = ciphertext.lower()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    key = int(key)
    # Shifts the ciphertext, excluding characters that aren't in the alphabet
    plaintext = ""
    for x in range(0, len(temp_ciphertext)):
        c = ciphertext[x]
        if temp_ciphertext[x] in alphabet:
            shifted = alphabet[(alphabet.index(temp_ciphertext[x]) - key) % len(alphabet)]
            if ciphertext[x].isupper():
                plaintext += shifted.upper()
            else:
                plaintext += shifted
        elif temp_ciphertext[x] not in alphabet:
            plaintext += ciphertext[x]
    # Return ciphertext
    return plaintext

def vigenere(text, key, mode="encrypt"):
    """Encrypt or decrypt vigenere-encoded text
    given a key"""
    temp_text = text.lower()
    key = key.lower()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    key_pair = ""
    str_all_special_char = ""    
    for x in range(0, len(text)):
        num_special_char = len(str_all_special_char)
        if temp_text[x] not in alphabet:
            str_all_special_char += temp_text[x]
            key_pair += temp_text[x]
        if temp_text[x] in alphabet:
            key_pair += key[(x - num_special_char) % len(key)]
    encoded_text = ""
    for x in range(0, len(text)):
        original = temp_text[x]
        encoded_chr = key_pair[x]
        if original not in alphabet:
            encoded_text += original
        else:
            if mode == "encrypt":
                shift_amount = alphabet.index(encoded_chr)
            elif mode == "decrypt":
                shift_amount = -1 * alphabet.index(encoded_chr)
            else:
                print("Invalid mode selected.")
            new = alphabet.index(original) + shift_amount
            final = alphabet[new % 26]
            # Matches casing of original text
            if text[x].isupper():
                encoded_text += final.upper()
            else:
                encoded_text += final
    return encoded_text

def solve_caesar(ciphertext):
    """Takes a caesar-encoded ciphertext and uses math to find 
    the most likely key. Returns the numeric value of the key."""
    # Maps each key to it's fitness (calculates fitness using chi-sq)
    # and then finds the best key (having the lowest chi-sq value)
    key_fitness = {}
    all_decrypted = []
    for i in range(0, 26):
        decrypted = caesar_decrypt(ciphertext, i)
        all_decrypted.append(decrypted)
        letters = {}
        for c in decrypted:
            if c not in letters:
                letters[c] = ""
        for x in letters:
            occurence = 0
            for c in decrypted:
                if x == c:
                    occurence += 1
            letters.update({x : str(occurence)})
        # Uses chi sq to solve caesar
        all_values = []
        for letter in letters.keys(): 
            actual = letters[letter]
            expected = letter_frequencies[letter] * len(ciphertext)
            squared = (int(actual) - float(expected)) ** 2
            value = squared / expected
            all_values.append(value)
        statistic = sum(all_values)
        key_fitness[str(i)] = str(statistic)
    best_key = min(key_fitness, key=lambda x:float(key_fitness[x]))
    return best_key

def find_key_lengths(ciphertext, number_of_lengths, selected_length=0):
    """Finds the best possible key lengths for a 
    vigenere-encrypted ciphertext"""
    # Cleans up the input so that it is usable in the program
    raw_ciphertext = ciphertext.lower()
    for character in raw_ciphertext:
        if character not in alphabet:
            raw_ciphertext = raw_ciphertext.replace(character, "")
    # Option to pick a max key length
    if selected_length == 0:
        max_key_length = len(raw_ciphertext) // 5
    else:
        max_key_length = selected_length
    
    #
    all_average_ICs = {}
    for key_period in range(2, max_key_length):
        all_sequences = []
        for x in range(0, key_period):
            new_sequence = ""
            y = x
            while y <= (len(raw_ciphertext) - 1):
                new_sequence += raw_ciphertext[y]
                y = y + key_period
            all_sequences.append(new_sequence)
        # 
        list_of_occurences = []
        for cut_ciphertext in all_sequences:
            letters = {}
            for c in cut_ciphertext:
                if c not in letters:
                    letters[c] = ""
            # occurences = []
            for x in letters:
                occurence = 0
                for c in cut_ciphertext:
                    if x == c:
                        occurence += 1
                letters.update({x : str(occurence)})
            list_of_occurences.append(letters.values())
        # 
        pre_average_prob = []
        for cut_ciphertext in all_sequences:
            for value in list_of_occurences:
                all_prob = []
                for single in value:
                    single = int(single)
                    ni = single / len(cut_ciphertext)
                    Ni = (single - 1) / (len(cut_ciphertext) - 1)
                    prob = ni * Ni
                    all_prob.append(prob)
                prob_sum = sum(all_prob)
                pre_average_prob.append(prob_sum)
        average_IC = sum(pre_average_prob) / len(pre_average_prob)
        all_average_ICs.update({str(key_period) : average_IC})
    best_key_lengths = sorted(all_average_ICs, key=all_average_ICs.get, reverse=True)[:number_of_lengths]
    best_key_lengths = [int(a) for a in best_key_lengths]
    # if len(best_key_lengths) == 1:
    #     return int(best_key_lengths[0])
    # else:
    return best_key_lengths

def create_key_from_length(original_ciphertext, key_length):
    raw_ciphertext = original_ciphertext.lower()
    for character in raw_ciphertext:
        if character not in alphabet:
            raw_ciphertext = raw_ciphertext.replace(character, "")
    
    # Uses key length to split the string into multiple caesar ciphers!
    all_sequences = []
    for new_sequence_starter in range(0, key_length):
        new_sequence = ""
        next_character_position = new_sequence_starter
        while next_character_position <= (len(raw_ciphertext) - 1):
            new_sequence += raw_ciphertext[next_character_position]
            next_character_position = next_character_position + key_length
        all_sequences.append(new_sequence)
    
    # Then the solve_casear() function solves each of those caesar ciphers 
    list_of_indices = []
    for string in all_sequences:
        chi_sq = solve_caesar(string)
        list_of_indices.append(chi_sq)
    
    # Turns each of the caesar solutions into corresponding letters
    letters = []
    for value in list_of_indices:
        letters.append(alphabet[int(value)])
    
    # Joins all the letters to create the key!
    key = ''.join(letters)
    return key

## BIGRAM ANALYSIS ##
# This function calculates the bigram fitness of a text
def bigram_fitness(text):
    text = text.lower()
    text = text.split()
    for x in range(0, len(text)):
        word = text[x]
        for character in word:
            if character not in alphabet:
                word = word.replace(character, "")
                text.pop(x)
                text.insert(x, word)
    every_bigram = []
    for x in range(0, (len(text))):
        word = text[x]
        for y in range(0, (len(word) - 1)):
            first = word[y]
            second = word[y + 1]
            bigram = first + second
            every_bigram.append(bigram)
    fitness = 0
    for bigram in every_bigram:
        key = bigram
        value = all_bigram_freq.get(key)
        fitness += float(value)
    return(fitness)

# Creates a key based on bigram analysis
def bigram_analysis(parent_key, original_ciphertext):

    # cleans up the parent_key
    parent_key = parent_key.lower()
    best_fitness_key = parent_key
    key_listed = list(best_fitness_key)
    # empty lists to hold all the parent keys
    # (the lists are used to determine when the fitness cannot be improved anymore)
    key_one = []
    key_two = []
    # lists can't be empty, so the key is added to list one,
    # and a place holder is added to list two
    key_one.append(best_fitness_key)
    key_two.append("A" * len(best_fitness_key))

    while key_one[-1] != key_two[-1]:
        key_two.append(best_fitness_key)
        for x in range(0, len(key_listed)):
            key_listed = list(best_fitness_key)
            character_position = alphabet.index(key_listed[x])
            for y in range(0, 27):
                new_character = alphabet[(character_position + (y)) % 26]
                key_listed[x] = new_character
                trial_key = "".join(key_listed)
                # print(trial_key)
                best_result = vigenere(original_ciphertext, best_fitness_key, mode="decrypt")
                best_fitness = bigram_fitness(best_result)
                plaintext_result = vigenere(original_ciphertext, trial_key, mode="decrypt")
                fitness = bigram_fitness(plaintext_result)
                # print(fitness)
                if fitness > best_fitness:
                    best_fitness_key = trial_key
                    key_one.append(best_fitness_key)
                    if len(key_one) > 5:
                        for x in range(0, 3):
                            key_one.pop(x)
                    if len(key_two) > 5:
                        for x in range(0, 3):
                            key_two.pop(x)
    return best_fitness_key
