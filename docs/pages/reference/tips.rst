Tips
------------

Handle dot directory entries (``.`` and ``..``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The path components ``.`` (current directory) and ``..`` (parent directory) are reserved names according to the underlying file system specifications:

- POSIX: `IEEE Std 1003.1-2017, Section 4.13 Pathname Resolution <https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap04.html>`__ defines them as the special filenames *dot* and *dot-dot*, which always refer to the directory itself and its parent directory, respectively.
- Windows: `Naming Files, Paths, and Namespaces <https://learn.microsoft.com/windows/win32/fileio/naming-a-file>`__ and `MS-FSCC 2.1.5.1 Dot Directory Names <https://learn.microsoft.com/openspecs/windows_protocols/ms-fscc/fccd0313-0364-45bd-b75c-924fd6a5662f>`__ likewise reserve them as dot directory names.

In principle they would be subject to both validation and sanitization.
However, since these names appear very frequently in real-world inputs (e.g., relative paths), ``pathvalidate`` excludes them from the default reserved-name checks for both ``validate_*`` and ``sanitize_*`` functions.
If you need to treat them as reserved, specify ``additional_reserved_names=[".", ".."]`` as shown in the sections below.

Sanitize dot directory entries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When you process filenames or filepaths containing ``.`` or ``..`` with the ``sanitize_filename`` function or the ``sanitize_filepath`` function, by default, ``sanitize_filename`` does nothing, and ``sanitize_filepath`` normalizes the filepaths:

.. code-block:: python

    print(sanitize_filename("."))
    print(sanitize_filepath("hoge/./foo"))

.. code-block:: console

    .
    hoge/foo

If you would like to replace ``.`` and ``..`` like other reserved words, you need to specify the arguments as follows:

.. code-block:: python

    from pathvalidate import sanitize_filepath, sanitize_filename
    from pathvalidate.error import ValidationError


    def always_add_trailing_underscore(e: ValidationError) -> str:
        if e.reusable_name:
            return e.reserved_name

        return f"{e.reserved_name}_"


    print(
        sanitize_filename(
            ".",
            reserved_name_handler=always_add_trailing_underscore,
            additional_reserved_names=[".", ".."],
        )
    )

    print(
        sanitize_filepath(
            "hoge/./foo",
            normalize=False,
            reserved_name_handler=always_add_trailing_underscore,
            additional_reserved_names=[".", ".."],
        )
    )

.. code-block:: console

    ._
    hoge/._/foo

Validate dot directory entries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
By default, ``validate_filename`` and ``validate_filepath`` accept ``.`` and ``..`` as valid names and do not raise a ``ValidationError``:

.. code-block:: python

    from pathvalidate import validate_filename

    validate_filename(".")
    validate_filename("..")

If you would like to reject ``.`` and ``..`` like other reserved names, specify them via the ``additional_reserved_names`` argument:

.. code-block:: python

    from pathvalidate import validate_filename
    from pathvalidate.error import ValidationError

    try:
        validate_filename(".", additional_reserved_names=[".", ".."])
    except ValidationError as e:
        print(e)

.. code-block:: console

    [PV1002] found a reserved name by a platform: '.' is a reserved name, platform=universal, reusable_name=False

The same option is available for ``is_valid_filename`` / ``is_valid_filepath`` to obtain a boolean result without raising:

.. code-block:: python

    from pathvalidate import is_valid_filename

    print(is_valid_filename("."))
    print(is_valid_filename(".", additional_reserved_names=[".", ".."]))

.. code-block:: console

    True
    False
