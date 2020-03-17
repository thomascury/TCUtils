from os import urandom as random

from docopt import docopt


def generate_password(length, authorized_chars):
    return ''.join(authorized_chars[r % len(authorized_chars)] for r in random(length))


lowercase_letters = "abcdefghijklmnopqrstuvwxyz"
uppercase_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
number_digits = "0123456789"
special_characters = "~!#$%^&*()-=+[]\\{}:;\"'<>?/"

__ver__ = "Password Generator v1"
__doc__ = f"""Password Generator.

Usage:
    password_generator.py [options] [<nb_of_characters>]
    password_generator.py (-h | --help)
    password_generator.py --version

Options:
    -h --help                   Show this screen.
    --version                   Show version.
    <nb_of_characters>          Number of characters in the password [default: 16].
    -l, --lowercase             Include lowercase letters in the password.
    -u, --uppercase             Include uppercase letters in the password.
    -n, --numbers               Include numbers in the password.
    -s, --specials              Include special_characters characters in the password.

If no character option is specified, use all four by default.

Character options are the following :
    lowercase letters:          {lowercase_letters}
    uppercase letters:          {uppercase_letters}
    numbers:                    {number_digits}
    special characters:         {special_characters}
"""

if __name__ == '__main__':
    arguments = docopt(__doc__, version=__ver__)
    # print(arguments)
    length = arguments["<nb_of_characters>"] is not None and int(arguments["<nb_of_characters>"]) or 16
    lowercase = arguments["--lowercase"]
    uppercase = arguments["--uppercase"]
    numbers = arguments["--numbers"]
    specials = arguments["--specials"]

    authorized_chars = ""
    if lowercase:
        authorized_chars += lowercase_letters
    if uppercase:
        authorized_chars += uppercase_letters
    if numbers:
        authorized_chars += number_digits
    if specials:
        authorized_chars += special_characters
    if len(authorized_chars) == 0:
        # raise IndexError("You must specify at least one group of authorized characters.")
        authorized_chars = lowercase_letters + uppercase_letters + number_digits + special_characters

    print(generate_password(length, authorized_chars=authorized_chars))
