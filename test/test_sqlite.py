# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
import string

import pytest

from pathvalidate import *


RESERVED_KEYWORDS_UPPER = [
    "ABORT", "ACTION", "ADD", "AFTER", "ALL", "ALTER", "ANALYZE", "AND", "AS",
    "ASC", "ATTACH", "AUTOINCREMENT",
    "BEFORE", "BEGIN", "BETWEEN", "BY",
    "CASCADE", "CASE", "CAST", "CHECK", "COLLATE", "COLUMN", "COMMIT",
    "CONFLICT", "CONSTRAINT", "CREATE", "CROSS", "CURRENT_DATE",
    "CURRENT_TIME", "CURRENT_TIMESTAMP",
    "DATABASE", "DEFAULT", "DEFERRABLE", "DEFERRED", "DELETE", "DESC",
    "DETACH", "DISTINCT", "DROP",
    "EACH", "ELSE", "END", "ESCAPE", "EXCEPT", "EXCLUSIVE", "EXISTS",
    "EXPLAIN",
    "FAIL", "FOR", "FOREIGN", "FROM", "FULL",
    "GLOB", "GROUP",
    "HAVING",
    "IF", "IGNORE", "IMMEDIATE", "IN", "INDEX", "INDEXED", "INITIALLY",
    "INNER", "INSERT", "INSTEAD", "INTERSECT", "INTO", "IS", "ISNULL",
    "JOIN",
    "KEY",
    "LEFT", "LIKE", "LIMIT",
    "MATCH", "NATURAL",
    "NO", "NOT", "NOTNULL", "NULL",
    "OF", "OFFSET", "ON", "OR", "ORDER", "OUTER",
    "PLAN", "PRAGMA", "PRIMARY",
    "QUERY",
    "RAISE", "RECURSIVE", "REFERENCES", "REGEXP", "REINDEX", "RELEASE",
    "RENAME", "REPLACE", "RESTRICT", "RIGHT", "ROLLBACK", "ROW",
    "SAVEPOINT", "SELECT", "SET",
    "TABLE", "TEMP", "TEMPORARY", "THEN", "TO", "TRANSACTION", "TRIGGER",
    "UNION", "UNIQUE", "UPDATE", "USING",
    "VACUUM", "VALUES", "VIEW", "VIRTUAL",
    "WHEN", "WHERE", "WITH", "WITHOUT",
]
RESERVED_KEYWORDS_LOWER = [keyword for keyword in RESERVED_KEYWORDS_UPPER]


class Test_validate_python_var_name:
    VALID_CHAR_LIST = [
        c for c in string.digits + string.ascii_letters + "_"
    ]

    @pytest.mark.parametrize(["value"], [
        [keyword_upper + keyword_lower]
        for keyword_upper, keyword_lower
        in zip(RESERVED_KEYWORDS_UPPER, RESERVED_KEYWORDS_LOWER)
    ])
    def test_normal(self, value):
        validate_sqlite_name(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, NullNameError],
        ["", NullNameError],
        [1, ValueError],
        [True, ValueError],
    ])
    def test_exception_type(self, value, expected):
        with pytest.raises(expected):
            validate_sqlite_name(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [reserved_keyword, ReservedNameError]
        for reserved_keyword
        in RESERVED_KEYWORDS_UPPER + RESERVED_KEYWORDS_LOWER
    ])
    def test_exception_reserved(self, value, expected):
        with pytest.raises(expected):
            validate_sqlite_name(value)
