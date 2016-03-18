from tcutils.dice import roll
import sys


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


def special_add_to_wordlist(word_list, n_words):
    special = ("~!#$%^", "&*()-=", "+[]\\{}", ":;\"'<>", "?/0123", "456789")
    word_roll = special_get_word_roll(n_words) - 1
    digit_roll = special_get_digit_roll(n_words) - 1
    special_roll_1, special_roll_2 = roll(2)
    # print((word_roll, digit_roll, special_roll_1, special_roll_2))
    special_char = special[special_roll_2 - 1][special_roll_1 - 1]
    # print("\"{}\"[{}] = {}".format(word_list[word_roll], digit_roll, special_char))
    word_list[word_roll] = word_list[word_roll][:digit_roll] + special_char + word_list[word_roll][digit_roll+1:]


def gen_diceware_passphrase(n_words=4, with_special=True):
    word_list = get_words(n_words)
    if with_special:
        special_add_to_wordlist(word_list, n_words)
    passphrase = " ".join(word_list)
    return passphrase


if __name__ == '__main__':
    if len(sys.argv) == 2:
        print(gen_diceware_passphrase(int(sys.argv[1])))
    else:
        print(gen_diceware_passphrase(4, False))

