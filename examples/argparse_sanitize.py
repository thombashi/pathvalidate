#!/usr/bin/env python3

from argparse import ArgumentParser

from pathvalidate.argparse import sanitize_filename_arg, sanitize_filepath_arg


parser = ArgumentParser()
parser.add_argument("--filename", type=sanitize_filename_arg)
parser.add_argument("--filepath", type=sanitize_filepath_arg)
options = parser.parse_args()

if options.filename:
    print(f"filename: {options.filename}")

if options.filepath:
    print(f"filepath: {options.filepath}")
