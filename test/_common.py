# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
import random
import string


char_list = [x for x in string.digits + string.ascii_letters]


def make_random_str(length):
    return "".join([random.choice(char_list) for _i in range(length)])
