Tips
------------

Sanitize dot-files or dot-directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
