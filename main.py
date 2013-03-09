#!/usr/bin/env python3
# -*-coding:Utf-8 -*
import argparse
from client import BaseBot, Base, Mine

class Bot(BaseBot):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A clever bot for the whitenight game.')
    parser.add_argument('host')
    parser.add_argument('-p', '--port', default=4321, type=int)
    parser.add_argument('username')
    args = parser.parse_args()
    Bot(args.host, args.port, args.username).run()
