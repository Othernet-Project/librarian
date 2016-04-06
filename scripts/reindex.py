#!/usr/bin/env python

from fsal import client


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--socket', '-s', help='FSAL socket path',
                        metavar='PATH')
    args = parser.parse_args()
    fc = client.FSAL(args.socket)
    fc.refresh()

if __name__ == '__main__':
    main()
