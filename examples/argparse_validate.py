#!/usr/bin/env python3


from argparse import ArgumentParser

from pathvalidate.argparse import filename, filepath


parser = ArgumentParser()
parser.add_argument("--filepath", type=filepath)
parser.add_argument("--filename", type=filename)
parser.parse_args()
