Errors
---------------

.. autoclass:: pathvalidate.error.ErrorReason
    :members:
    :undoc-members:
    :show-inheritance:

.. table:: List of Errors

    +--------+------------------------+------------------------------------------------------+
    |  Code  |          Name          |                     Description                      |
    +========+========================+======================================================+
    | PV1001 | NULL_NAME              | the value must not be an empty string                |
    +--------+------------------------+------------------------------------------------------+
    | PV1002 | RESERVED_NAME          | found a reserved name by a platform                  |
    +--------+------------------------+------------------------------------------------------+
    | PV1100 | INVALID_CHARACTER      | invalid characters found                             |
    +--------+------------------------+------------------------------------------------------+
    | PV1101 | INVALID_LENGTH         | found an invalid string length                       |
    +--------+------------------------+------------------------------------------------------+
    | PV1200 | FOUND_ABS_PATH         | found an absolute path where must be a relative path |
    +--------+------------------------+------------------------------------------------------+
    | PV1201 | MALFORMED_ABS_PATH     | found a malformed absolute path                      |
    +--------+------------------------+------------------------------------------------------+
    | PV2000 | INVALID_AFTER_SANITIZE | found invalid value after sanitizing                 |
    +--------+------------------------+------------------------------------------------------+

.. autoexception:: pathvalidate.error.ValidationError
    :members:
    :undoc-members:
    :show-inheritance:
