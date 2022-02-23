#!/usr/bin/python3

import argparse
import argcomplete
import functions

parser = argparse.ArgumentParser(description="Encrypt or decrypt a vigenere cipher, or try to solve one without a key!")

input_type = parser.add_mutually_exclusive_group(required=True)
input_type.add_argument("-T", "--text", type=str, help="The text to either encrypt, decrypt, or solve.")
input_type.add_argument("-F", "--file", type=argparse.FileType("r"), help="Use a file instead of text.")

subparsers = parser.add_subparsers(dest="mode", required=True, help="Use -h after the 'encrypt', 'decrypt', or solve'")

encrypt = subparsers.add_parser("encrypt")
encrypt.add_argument("--key", type=str, required=True)

decrypt = subparsers.add_parser("decrypt")
decrypt.add_argument("--key", type=str, required=True)

solve = subparsers.add_parser("solve")

solve_with_length = solve.add_mutually_exclusive_group(required=False)
solve_with_length.add_argument("-l", "--key_length", type=int, help="Solve with an already-known key length.")
solve_with_length.add_argument("-n", "--num_lengths", type=int, help="Number of key lengths to look for. Default is 1.")
solve_with_length.add_argument("-m", "--max_length", type=int, help="Solve with a known maximum key length.")

solve.add_argument("-b", "--bigram", required=False, action="store_true", help="Potentially improves the key, but takes longer to complete.")
# solve.add_argument("-d", "--decrypt", required=False, action="store_true", help="Decrypt after finding the key. Not recommended on large ciphertexts and when [num_lengths] > 1.")

argcomplete.autocomplete(parser)
args = parser.parse_args()

# Gets the text
if args.text:
    text = args.text
elif args.file:
    text = args.file.read()

if args.mode == "encrypt":
    encryption_key = args.key
    plaintext = functions.vigenere(text, encryption_key, mode="encrypt")
    print(plaintext)

elif args.mode == "decrypt":
    decryption_key = args.key
    ciphertext = functions.vigenere(text, decryption_key, mode="decrypt")
    print(ciphertext)

elif args.mode == "solve":

    # Set defaults for each "solve" argument. Defaults will be edited if arg is used
    number_of_lengths = 1
    bigram_mode = False
    chosen_max_length = 0

    print(f"Using autosolve mode -")
    if args.key_length:
        key_length = args.key_length
        print(f"The known key length that will be used is {args.key_length}")
        number_of_lengths = 0

    elif args.num_lengths:
        number_of_lengths = args.num_lengths
        print(f"The {number_of_lengths} most likely key lengths will be presented along with best keys:")

    elif args.max_length:
        chosen_max_length = args.max_length
        print(f"Looking at all keys up to {chosen_max_length} characters long.")

    if args.bigram:
        bigram_mode = True
        print(f"Also running bigram analysis. This may take longer.")

    if number_of_lengths == 0:
        key = functions.create_key_from_length(text, key_length)
        plaintext = functions.vigenere(text, key, mode="decrypt")
        print(f"    INITIAL KEY: {key}")

    elif number_of_lengths > 0:
        best_lengths = functions.find_key_lengths(text, number_of_lengths, selected_length=chosen_max_length)
        for best_length in best_lengths:
            key = functions.create_key_from_length(text, best_length)
            print(f"Length: {best_length}")
            print(f"    INITIAL KEY: {key}")
            if bigram_mode:
                bigram_key = functions.bigram_analysis(key, text)
                print(f"    ~BIGRAM KEY: {bigram_key}")
            # else:
            # plaintext = functions.vigenere(text, key, mode="decrypt")
            # print(plaintext)
