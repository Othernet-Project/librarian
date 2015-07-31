#!/usr/bin/python2

import hashlib


def hash_token(token):
    sha256 = hashlib.sha256()
    sha256.update(token.encode('utf8'))
    return sha256.hexdigest()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate SHA-256 hexdigest '
                                     'from emergency reset token')
    parser.add_argument('token', metavar='TOKEN')
    args = parser.parse_args()

    print(hash_token(args.token))
