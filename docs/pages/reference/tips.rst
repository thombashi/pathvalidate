Tips
------------

Choose how to handle long names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``sanitize_filename``, ``sanitize_filepath``, ``FileNameSanitizer`` and
``FilePathSanitizer`` accept ``length_behavior`` as a :py:class:`~pathvalidate.LengthBehavior`
member or an exact lowercase string: ``"keep"``, ``"trim"``, ``"trim_name"`` or
``"error"``. The default remains ``TRIM``. Length is measured in encoded bytes,
after invalid character replacement and before name handlers and Windows edge
cleanup. These policies leave the existing effective ``max_len`` limits unchanged.

``TRIM_NAME`` preserves only the final extension (including its dot), as defined
by ``posixpath.splitext``. It keeps the longest stem prefix that fits when encoded
together with that extension, counting any BOM once and preserving code point
boundaries. It can produce an empty stem; it does not preserve grapheme clusters.
Dotfiles such as ``.bashrc`` have no extension and use the existing ``TRIM`` behavior.

.. code-block:: python

    from pathvalidate import LengthBehavior, ValidationError, sanitize_filename

    print(sanitize_filename("archive.tar.gz", max_len=10, platform="linux",
                            fs_encoding="utf-8", length_behavior=LengthBehavior.TRIM_NAME))
    print(sanitize_filename("abc.txt", max_len=4, platform="linux",
                            fs_encoding="utf-8", length_behavior="trim_name"))
    try:
        sanitize_filename("abc.txt", max_len=3, platform="linux",
                          fs_encoding="utf-8", length_behavior="trim_name")
    except ValidationError as error:
        print(error.reason.name)

.. code-block:: console

    archive.gz
    .txt
    INVALID_LENGTH

An extension that cannot fit raises ``INVALID_LENGTH`` without falling back to
``TRIM``. ``ERROR`` raises the same reason immediately when the replaced name is
overlong. Both include the replaced component value, encoded byte count, encoding
and platform. Neither waits for ``validate_after_sanitize``.

``KEEP`` retains the full length while still applying default name cleanup and
handlers. Final validation remains available and can reject the result:

.. code-block:: python

    print(sanitize_filename("CON.txt", max_len=3, platform="windows",
                            fs_encoding="utf-8", length_behavior="keep"))
    try:
        sanitize_filename("CON.txt", max_len=3, platform="windows",
                          fs_encoding="utf-8", length_behavior="keep",
                          validate_after_sanitize=True)
    except ValidationError as error:
        print(error.reason.name)

.. code-block:: console

    CON_.txt
    INVALID_AFTER_SANITIZE

Handlers run once in their existing order and may grow or alter the output;
Windows cleanup may remove a trailing dot. The length policy is not reapplied
to handler output. Final validation checks that output when requested. An injected
class validator keeps its original protocol and error priority; ``KEEP`` does not
override its decisions.

For paths, each ordinary directory and filename component receives the same
policy and budget. The budget is not shared or divided, and drive/UNC and special
NTFS branches retain their existing handling. Combined paths can still exceed
``max_len`` even with ``ERROR``:

.. code-block:: python

    from pathvalidate import sanitize_filepath

    print(sanitize_filepath("abcdefgh.txt/ijklmnop.log", max_len=8,
                            platform="linux", fs_encoding="utf-8", normalize=False,
                            length_behavior="trim_name"))
    print(sanitize_filepath("abc/def", max_len=3, platform="linux",
                            fs_encoding="utf-8", length_behavior="error"))
    try:
        sanitize_filepath("abc/def", max_len=3, platform="linux",
                          fs_encoding="utf-8", length_behavior="error",
                          validate_after_sanitize=True)
    except ValidationError as error:
        print(error.reason.name)

.. code-block:: console

    abcd.txt/ijkl.log
    abc/def
    INVALID_LENGTH

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
