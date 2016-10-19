from time import sleep
from tcutils.dice import roll
import sys
from docopt import docopt


diceware_list_file = r"C:\beale.wordlist.asc"


def parse_list(file=diceware_list_file):
    word_dict = {}
    with open(file) as file_content:
        for line in file_content.readlines():
            try:
                word_id, word_string = line[:-1].split("\t")
            except ValueError:
                continue
            word_dict[word_id] = word_string
    return word_dict


def get_word(word_dict):
    word_id = "".join(map(str, roll(5)))
    word = word_dict[word_id]
    return word


def get_words(n):
    word_dict = parse_list()
    word_list = []
    while len(word_list) < n:
        try:
            word = get_word(word_dict)
            word_list.append(word)
        except KeyError:
            pass
    return word_list


def special_get_word_roll(n_words):
    word_roll = None
    while True:
        nb_word_rolls = int(n_words / 6) + 1
        word_rolls = roll(nb_word_rolls)
        word_roll = sum(word_rolls)
        if word_roll <= n_words:
            break
    return word_roll


def special_get_digit_roll(n_digits):
    digit_roll = None
    while True:
        nb_digit_rolls = int(n_digits / 6) + 1
        digit_rolls = roll(nb_digit_rolls)
        digit_roll = sum(digit_rolls)
        if digit_roll < n_digits:
            break
    return digit_roll


def special_add_to_wordlist(word_list):
    special = ("~!#$%^", "&*()-=", "+[]\\{}", ":;\"'<>", "?/0123", "456789")
    n_words = len(word_list)
    word_roll = special_get_word_roll(n_words) - 1
    digit_roll = special_get_digit_roll(n_words) - 1
    special_roll_1, special_roll_2 = roll(2)
    # print((word_roll, digit_roll, special_roll_1, special_roll_2))
    special_char = special[special_roll_2 - 1][special_roll_1 - 1]
    # print("\"{}\"[{}] = {}".format(word_list[word_roll], digit_roll, special_char))
    word_list[word_roll] = word_list[word_roll][:digit_roll] + special_char + word_list[word_roll][digit_roll+1:]


def capitalize_add_to_wordlist(word_list):
    n_words = len(word_list)
    word_roll = special_get_word_roll(n_words) - 1
    digit_roll = special_get_digit_roll(len(word_list[word_roll])) - 1
    while word_list[word_roll][digit_roll] not in 'abcdefghijklmnopqrstuvwxyz':
        word_roll = special_get_word_roll(n_words) - 1
        digit_roll = special_get_digit_roll(len(word_list[word_roll])) - 1
    word_list[word_roll] = word_list[word_roll][:digit_roll]\
                         + word_list[word_roll][digit_roll].upper()\
                         + word_list[word_roll][digit_roll+1:]


def gen_diceware_passphrase(n_words=4, specials=0, capitalized=0):
    word_list = get_words(n_words)
    for i in range(specials):
        special_add_to_wordlist(word_list)
    for i in range(capitalized):
        capitalize_add_to_wordlist(word_list)
    passphrase = " ".join(word_list)
    return passphrase


def passphrase_check(passphrase, length, upper, special, number):
    LOWER = 'abcdefghijklmnopqrstuvwxyz'  # By default is lower
    UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    NUMBER = '0123456789'
    SPECIAL = "~!#$%^&*()-=+[]\\{}:;\"'<>?/"
    l = u = n = s = 0
    w = 1
    for char in passphrase:
        if char == ' ':
            w += 1
        elif char in LOWER:
            l += 1
        elif char in UPPER:
            u += 1
        elif char in NUMBER:
            n += 1
        elif char in SPECIAL:
            s += 1
        else:
            raise ValueError('Unknown character type')

    # print("Passphrase: '{pf}'\n"
    #       " > Word count: {wcf}/{wca}\n"
    #       " > Upper: {uf}/{ua}\n"
    #       " > Number: {nf}/{na}\n"
    #       " > Special: {sf}/{sa}"
    #       "".format(pf=passphrase,
    #                 wcf=w, wca=length,
    #                 uf=u, ua=upper,
    #                 nf=n, na=number and '>0' or '=0',
    #                 sf=s, sa=special
    #                 ))

    return w == length and u == upper and s == special and n == number


def enforced_passphrase(length, specials=0, capitalized=0, number=1):
    t = 1
    passphrase = gen_diceware_passphrase(length, specials, capitalized)
    print("Try {}".format(t))
    while not passphrase_check(passphrase, length, capitalized, specials, number):
        # print(passphrase + " did not pass !")
        # sleep(1)
        t += 1
        passphrase = gen_diceware_passphrase(length, specials, capitalized)
        print("Try {}".format(t))
    return passphrase


__ver__ = "Diceware Passphrase Generator v2"
__doc__ = """Diceware Passphrase Generator.

Usage:
    diceware_passphrase.py [<nb_of_words> <nb_special> <nb_capitalized> <nb_number>]
    diceware_passphrase.py (-h | --help)
    diceware_passphrase.py --version

Options:
    -h --help                   Show this screen.
    --version                   Show version.
    <nb_of_words>               Number of words in the passphrase [default: 4].
    <nb_special>                Number of special characters in the passphrase [default: 1].
    <nb_capitalized>            Number of capitalized characters in the passphrase [default: 1].
    <nb_number>                 Number of number characters in the passphrase [default: 1].
"""

if __name__ == '__main__':
    arguments = docopt(__doc__, version=__ver__)
    word_count = arguments["<nb_of_words>"] is not None and int(arguments["<nb_of_words>"]) or 4
    special = arguments["<nb_special>"] is not None and int(arguments["<nb_special>"]) or 1
    capitalized = arguments["<nb_capitalized>"] is not None and int(arguments["<nb_capitalized>"]) or 1
    number = arguments["<nb_number>"] is not None and int(arguments["<nb_number>"]) or 1
    print(arguments)
    print(enforced_passphrase(word_count, special, capitalized, number))
    # if len(sys.argv) == 2:
    #     print(gen_diceware_passphrase(int(sys.argv[1])))
    # else:
    #     print(gen_diceware_passphrase(4, True))

