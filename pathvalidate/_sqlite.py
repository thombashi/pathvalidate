# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

from ._common import _validate_null_string
from ._error import ReservedNameError


__SQLITE_RESERVED_KEYWORDS = [
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


def validate_sqlite_name(name):
    """
    :param str name: Name to validate.
    :raises pathvalidate.NullNameError: If the ``name`` is empty.
    :raises pathvalidate.ReservedNameError: If the ``name`` is equals to
        `SQLite Keywords
        <https://www.sqlite.org/lang_keywords.html>`__
    """

    _validate_null_string(name)

    if name.upper() in __SQLITE_RESERVED_KEYWORDS:
        raise ReservedNameError(
            "{:s} is a reserved keyword by sqlite".format(name))
