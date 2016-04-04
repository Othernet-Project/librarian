import random
import string


def generate_random_key(letters=True, digits=True, punctuation=True,
                        length=50):
    charset = []
    if letters:
        charset.append(string.ascii_letters)
    if digits:
        charset.append(string.digits)
    if punctuation:
        charset.append(string.punctuation)

    if not charset:
        return ''

    chars = (''.join(charset).replace('\'', '')
                             .replace('"', '')
                             .replace('\\', ''))
    return ''.join([random.choice(chars) for i in range(length)])
