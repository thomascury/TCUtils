from os import urandom as random
from docopt import docopt
from sys import argv
from os.path import basename


def generate_password(length, authorized_chars):
    return ''.join(authorized_chars[r % len(authorized_chars)] for r in random(length))


lowercase_letters = "abcdefghijklmnopqrstuvwxyz"
uppercase_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
number_digits = "0123456789"
special_characters = "~!#$%^&*()-=+[]\\{}:;\"'<>?/@"

filename = basename(argv[0])

__ver__ = "Password Generator v2"
__doc__ = f"""Simple password generator

Usage:
    {filename} [-luns] [options]
    {filename} --authorized-chars="<char_list>" [options]

Options:
    -h --help                           Show this screen
    -v --version                        Show version
    -c <nb>, --length <nb>              Length of the password [default: 16]
    -m <nb>, --multi <nb>               Number of passwords to generate [default: 1]
    --banned-chars="<char_list>"        Provide a list of banned character for the password creation

    -l, --lowercase                     Include lowercase letters in the password
    -u, --uppercase                     Include uppercase letters in the password
    -n, --numbers                       Include numbers in the password
    -s, --specials                      Include special characters in the password
    -x, --hexadecimals                  Inlcude hexadecimal charaters in the password
    --authorized-chars="<char_list>"    Provide a list of authorized character for the password creation

If no character option is specified and no authorized character list is provided, use all four by default

Character options are the following :
    lowercase letters:          {lowercase_letters}
    uppercase letters:          {uppercase_letters}
    numbers:                    {number_digits}
    special characters:         {special_characters}
"""

if __name__ == '__main__':
    arguments = docopt(__doc__, version=__ver__)
    # print(arguments)
    length = int(arguments["--length"])
    authorized_chars = arguments["--authorized-chars"]
    banned_chars = arguments["--banned-chars"]
    lowercase = arguments["--lowercase"]
    uppercase = arguments["--uppercase"]
    numbers = arguments["--numbers"]
    specials = arguments["--specials"]
    hexadecimals = arguments["--hexadecimals"]

    if authorized_chars is None:
        authorized_chars = ""
        if lowercase:
            authorized_chars += lowercase_letters
        if uppercase:
            authorized_chars += uppercase_letters
        if numbers:
            authorized_chars += number_digits
        if specials:
            authorized_chars += special_characters
        if hexadecimals:
            authorized_chars += number_digits + uppercase_letters[:6]
        if len(authorized_chars) == 0:
            # raise IndexError("You must specify at least one group of authorized characters.")
            authorized_chars = lowercase_letters + uppercase_letters + number_digits + special_characters
    if banned_chars is not None:
        char_list = list(authorized_chars)
        for char in set(banned_chars):
            try:
                char_list.remove(char)
            except ValueError:
                print(f"Character '{char}' not in the specified character set:\n{char_list}")
        authorized_chars = "".join(char_list)

    for i in range(int(arguments["--multi"])):
        print(generate_password(length, authorized_chars=authorized_chars))
