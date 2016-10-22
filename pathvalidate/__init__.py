# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import

from ._error import NullNameError
from ._error import InvalidNameError
from ._error import InvalidCharError
from ._error import InvalidCharWindowsError
from ._error import InvalidLengthError
from ._error import ReservedNameError
from ._error import ValidReservedNameError
from ._error import InvalidReservedNameError

from ._app import validate_excel_sheet_name
from ._app import sanitize_excel_sheet_name
from ._file import validate_filename
from ._file import validate_file_path
from ._file import sanitize_filename
from ._file import sanitize_file_path
from ._symbol import replace_symbol
from ._sqlite import validate_sqlite_table_name
from ._sqlite import validate_sqlite_attr_name
from ._var_name import validate_python_var_name
from ._var_name import sanitize_python_var_name
