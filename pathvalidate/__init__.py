# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import

from .__version__ import __author__, __copyright__, __email__, __license__, __version__
from ._app import sanitize_excel_sheet_name, validate_excel_sheet_name
from ._common import (
    ascii_symbol_list,
    ascii_symbols,
    replace_unprintable_char,
    unprintable_ascii_char_list,
    unprintable_ascii_chars,
    validate_null_string,
)
from ._file import (
    Platform,
    sanitize_file_path,
    sanitize_filepath,
    sanitize_filename,
    validate_file_path,
    validate_filepath,
    validate_filename,
)
from ._ltsv import sanitize_ltsv_label, validate_ltsv_label
from ._symbol import replace_symbol, validate_symbol
from .error import (
    ErrorReason,
    InvalidCharError,
    InvalidLengthError,
    InvalidReservedNameError,
    NullNameError,
    ReservedNameError,
    ValidationError,
    ValidReservedNameError,
)
