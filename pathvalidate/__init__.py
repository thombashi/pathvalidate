# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import

from .__version__ import __author__, __copyright__, __email__, __license__, __version__
from ._common import (
    ascii_symbols,
    replace_unprintable_char,
    unprintable_ascii_chars,
    validate_null_string,
)
from ._file import (
    FileNameSanitizer,
    FilePathSanitizer,
    Platform,
    is_valid_filename,
    is_valid_filepath,
    normalize_platform,
    sanitize_file_path,
    sanitize_filename,
    sanitize_filepath,
    validate_file_path,
    validate_filename,
    validate_filepath,
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
