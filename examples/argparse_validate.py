#!/usr/bin/env python3

from argparse import ArgumentParser

from pathvalidate.argparse import validate_filename_arg, validate_filepath_arg


parser = ArgumentParser()
parser.add_argument("--filename", type=validate_filename_arg)
parser.add_argument("--filepath", type=validate_filepath_arg)
options = parser.parse_args()

if options.filename:
    print(f"filename: {options.filename}")

if options.filepath:
    print(f"filepath: {options.filepath}")
