<a id="v3.3.1"></a>
# [v3.3.1](https://github.com/thombashi/pathvalidate/releases/tag/v3.3.1) - 2025-06-15

* Modify to use `repr()` for `value` formatting in error messages and validation descriptions

**Full Changelog**: https://github.com/thombashi/pathvalidate/compare/v3.3.0...v3.3.1

[Changes][v3.3.1]


<a id="v3.3.0"></a>
# [v3.3.0](https://github.com/thombashi/pathvalidate/releases/tag/v3.3.0) - 2025-06-15

* Add `value` to the `INVALID_LENGTH` validation error
* Ensure that the `invalids` value of `INVALID_CHARACTER` is unique

**Full Changelog**: https://github.com/thombashi/pathvalidate/compare/v3.2.3...v3.3.0

[Changes][v3.3.0]


<a id="v3.2.3"></a>
# [v3.2.3](https://github.com/thombashi/pathvalidate/releases/tag/v3.2.3) - 2025-01-03

## What's Changed
* Fix dot-files validation by [@thombashi](https://github.com/thombashi) in [#60](https://github.com/thombashi/pathvalidate/pull/60) (Thanks to [@slingshotvfx](https://github.com/slingshotvfx))

**Full Changelog**: https://github.com/thombashi/pathvalidate/compare/v3.2.2...v3.2.3

[Changes][v3.2.3]


<a id="v3.2.2"></a>
# [v3.2.2](https://github.com/thombashi/pathvalidate/releases/tag/v3.2.2) - 2025-01-01

- Fix the detection logic of the reservation words for the file name on Windows: [#57](https://github.com/thombashi/pathvalidate/issues/57) (Thanks to [@jplarocque](https://github.com/jplarocque))
- Drop support for Python 3.7/3.8
- Refactor type annotations

**Full Changelog**: https://github.com/thombashi/pathvalidate/compare/v3.2.1...v3.2.2

[Changes][v3.2.2]


<a id="v3.2.1"></a>
# [v3.2.1](https://github.com/thombashi/pathvalidate/releases/tag/v3.2.1) - 2024-08-23

## What's Changed
* Test Python 3.12 in CIs by [@MatthieuDartiailh](https://github.com/MatthieuDartiailh) in [#40](https://github.com/thombashi/pathvalidate/pull/40)
* Bump actions/setup-python from 4 to 5 by [@dependabot](https://github.com/dependabot) in [#36](https://github.com/thombashi/pathvalidate/pull/36)
* Bump actions/upload-artifact from 3 to 4 by [@dependabot](https://github.com/dependabot) in [#38](https://github.com/thombashi/pathvalidate/pull/38)
* Bump actions/download-artifact from 3 to 4 by [@dependabot](https://github.com/dependabot) in [#37](https://github.com/thombashi/pathvalidate/pull/37)
* Fix CI by [@thombashi](https://github.com/thombashi) in [#41](https://github.com/thombashi/pathvalidate/pull/41)
* Update the CI workflow to include a job that publishes packages to TestPyPI by [@thombashi](https://github.com/thombashi) in [#42](https://github.com/thombashi/pathvalidate/pull/42)
* Fix coverage report by [@thombashi](https://github.com/thombashi) in [#45](https://github.com/thombashi/pathvalidate/pull/45)
* Fix `sanitize_filename` truncation by [@7x11x13](https://github.com/7x11x13) in [#48](https://github.com/thombashi/pathvalidate/pull/48)
* Fix validation functions of filepaths by [@thombashi](https://github.com/thombashi) in [#55](https://github.com/thombashi/pathvalidate/pull/55)
  - If `platform` argument is `windows` or `universal`, filepaths ending with a space or a period should be detected as an error
  - Fix POSIX-style absolute paths were not detected as errors with `platform="windows"` or `platform="universal"` on Python 3.12 and below
* Add support for Python 3.13 by [@thombashi](https://github.com/thombashi) in [#56](https://github.com/thombashi/pathvalidate/pull/56)
* Improve type annotations
* Add a build and publish workflow
* Add Sigstore signatures to release assets
* Update copyright year to include the last update year: [#54](https://github.com/thombashi/pathvalidate/issues/54) (Thanks to [@Flimm](https://github.com/Flimm))
* Add CHANGELOG


## New Contributors
* [@MatthieuDartiailh](https://github.com/MatthieuDartiailh) made their first contribution in [#40](https://github.com/thombashi/pathvalidate/pull/40)
* [@dependabot](https://github.com/dependabot) made their first contribution in [#36](https://github.com/thombashi/pathvalidate/pull/36)
* [@7x11x13](https://github.com/7x11x13) made their first contribution in [#48](https://github.com/thombashi/pathvalidate/pull/48)

**Full Changelog**: https://github.com/thombashi/pathvalidate/compare/v3.2.0...v3.2.1

[Changes][v3.2.1]


<a id="v3.2.0"></a>
# [v3.2.0](https://github.com/thombashi/pathvalidate/releases/tag/v3.2.0) - 2023-09-17

- Add `reserved_name_handler` argument to `sanitize_filename` function and `sanitize_filepath` function
- Add `NullValueHandler` class and `ReservedNameHandler` class
- Add `fs_encoding` property and `byte_count` property to `ValidationError` class
- Add `additional_reserved_names` argument to validate/sanitize functions to allow custom reserved names
- Modify the return value format of `ValidationError.__str__` method
- Improve type annotations

**Full Changelog**: https://github.com/thombashi/pathvalidate/compare/v3.1.0...v3.2.0

[Changes][v3.2.0]


<a id="v3.1.0"></a>
# [v3.1.0](https://github.com/thombashi/pathvalidate/releases/tag/v3.1.0) - 2023-07-16

- Fix validation error messages to show the `target-platform` properly: [#34](https://github.com/thombashi/pathvalidate/issues/34) (Thanks to [@matanster](https://github.com/matanster))
- Fix README: out of date with the actual error generated by `validate_filename` [#35](https://github.com/thombashi/pathvalidate/issues/35) (Thanks to [@hXtreme](https://github.com/hXtreme))
- Add `description` property to `ErrorReason` class
- Add `as_slog` method to `ValidationError` class
- Add `docs` extras
- Change the type of the return value of `ValidationError.reason` from `Optional[ErrorReason]` to `ErrorReason`
- Update `[build-system]`
- Drop support for Python 3.6


**Full Changelog**: https://github.com/thombashi/pathvalidate/compare/v3.0.0...v3.1.0

[Changes][v3.1.0]


<a id="v3.0.0"></a>
# [v3.0.0](https://github.com/thombashi/pathvalidate/releases/tag/v3.0.0) - 2023-05-22

## What's Changed
- Trim heading spaces in Windows by [@eggplants](https://github.com/eggplants) in [#28](https://github.com/thombashi/pathvalidate/pull/28)
- Consider filesystem encoding for length calculations: [#26](https://github.com/thombashi/pathvalidate/issues/26) (Thanks to [@virlos](https://github.com/virlos))
- Fix type model: [#29](https://github.com/thombashi/pathvalidate/issues/29) (Thanks to [@rogalski](https://github.com/rogalski))
- Fix sanitizing of filenames that only consist of whitespaces and periods
- Add `validate_unprintable_char` function
- Add `validate_after_sanitize` keyword argument to `sanitize_filename` and `sanitize_filepath` functions
- Add error codes to `ErrorReason`
- Add `zip_safe=False` to `setup`
- Modify to accept `pathvalidate.Platform` type as `platform` arguments
- Rename type alias from `Handler` to `NullValueHandler`
- Remove `InvalidLengthError` to use `ValidationError`
- Improve type annotations
- Make it possible to import `FileNameValidator` and `FilePathValidator` classes from the package root
- Change constructor arguments of `FileNameSanitizer` and `FilePathSanitizer` classes
  - Remove `min_len`
  - Add `validator`
- Remove deprecated functions
- Modify error messages
- Refactoring

**Full Changelog**: https://github.com/thombashi/pathvalidate/compare/v2.5.2...v3.0.0


[Changes][v3.0.0]


<a id="v2.5.2"></a>
# [v2.5.2](https://github.com/thombashi/pathvalidate/releases/tag/v2.5.2) - 2022-08-20

- Add support for Python 3.11: [#22](https://github.com/thombashi/pathvalidate/issues/22) (Thanks to [@hegjon](https://github.com/hegjon))

**Full Changelog**: https://github.com/thombashi/pathvalidate/compare/v2.5.1...v2.5.2


[Changes][v2.5.2]


<a id="v2.5.1"></a>
# [v2.5.1](https://github.com/thombashi/pathvalidate/releases/tag/v2.5.1) - 2022-07-31

## What's Changed
* Add `__all__` by [@eggplants](https://github.com/eggplants) in [#24](https://github.com/thombashi/pathvalidate/pull/24)
* Add `DeprecationWarning` to deprecated functions


## New Contributors
* [@eggplants](https://github.com/eggplants) made their first contribution in [#24](https://github.com/thombashi/pathvalidate/pull/24)

**Full Changelog**: https://github.com/thombashi/pathvalidate/compare/v2.5.0...v2.5.1

[Changes][v2.5.1]


<a id="v2.5.0"></a>
# [v2.5.0](https://github.com/thombashi/pathvalidate/releases/tag/v2.5.0) - 2021-09-26

- Add support for Python 3.10
- Drop support for Python 3.5
- Add `null_value_handler` argument to `sanitize_filename`/`sanitize_filepath` functions: [#20](https://github.com/thombashi/pathvalidate/issues/20) (Thanks to @ 
mkbloke)
- Add `AbstractSanitizer`/`AbstractValidator` classes to import path
- Add `replace_ansi_escape` function
- Add `setup-ci` target to `Makefile`
- Modify `min_len`/`max_len` to use default values when assigned minus values


[Changes][v2.5.0]


<a id="v2.4.1"></a>
# [v2.4.1](https://github.com/thombashi/pathvalidate/releases/tag/v2.4.1) - 2021-04-03

- Fix filename validations that include `'\'` (backslash) on other than Windows: [#18](https://github.com/thombashi/pathvalidate/issues/18) (Thanks to [@Traktormaster](https://github.com/Traktormaster))


[Changes][v2.4.1]


<a id="v2.4.0"></a>
# [v2.4.0](https://github.com/thombashi/pathvalidate/releases/tag/v2.4.0) - 2021-03-21

- Add `exclude_symbols` argument to `replace_symbol` function
- Fix permissions of files included in `sdist` package binary (Thanks to [@hegjon](https://github.com/hegjon))


[Changes][v2.4.0]


<a id="v2.3.2"></a>
# [v2.3.2](https://github.com/thombashi/pathvalidate/releases/tag/v2.3.2) - 2021-01-03

- Fix to disallow file name/path that only white spaces for `universal` platform

[Changes][v2.3.2]


<a id="v2.3.1"></a>
# [v2.3.1](https://github.com/thombashi/pathvalidate/releases/tag/v2.3.1) - 2020-12-13

- Modify to accept file name/path that consists only whitespaces: [#15](https://github.com/thombashi/pathvalidate/issues/15) (Thank to [@Traktormaster](https://github.com/Traktormaster))


[Changes][v2.3.1]


<a id="v2.3.0"></a>
# [v2.3.0](https://github.com/thombashi/pathvalidate/releases/tag/v2.3.0) - 2020-05-03

- Change not to process for `"."`/`".."` by sanitization functions: [#13](https://github.com/thombashi/pathvalidate/issues/13) (Thanks to [@ProfElectric](https://github.com/ProfElectric))
- Change to normalize with `sanitize_filepath` in default
- Add normalize interface to `sanitize_filepath`


[Changes][v2.3.0]


<a id="v2.2.2"></a>
# [v2.2.2](https://github.com/thombashi/pathvalidate/releases/tag/v2.2.2) - 2020-03-28

- Improve file path validation for Windows platform: [#12](https://github.com/thombashi/pathvalidate/issues/12) (Thanks to [@bschollnick](https://github.com/bschollnick))
- Fix `__str__` method
- Fix to avoid raise an exception when an absolute path includes `"."`/`".."`
- Modify an error message
- Modify raising exception from `NullNameError` to `ValidationError` of `validate_pathtype`


[Changes][v2.2.2]


<a id="v2.2.1"></a>
# [v2.2.1](https://github.com/thombashi/pathvalidate/releases/tag/v2.2.1) - 2020-03-20

- Fix to include `py.typed` to the package


[Changes][v2.2.1]


<a id="v2.2.0"></a>
# [v2.2.0](https://github.com/thombashi/pathvalidate/releases/tag/v2.2.0) - 2020-02-12

- Add `POSIX` as a platform
- Add a reserved keyword for macOS
- Change platform of `validate_filepath_arg`/`sanitize_filepath_arg` to `'auto'`: [#11](https://github.com/thombashi/pathvalidate/issues/11) (Thanks to [@freelanceAndy](https://github.com/freelanceAndy))


[Changes][v2.2.0]


<a id="v2.1.0"></a>
# [v2.1.0](https://github.com/thombashi/pathvalidate/releases/tag/v2.1.0) - 2020-02-01

- Add `check_reserved` argument to validate/sanitize functions
- Add `'/'` as a reserved file path for Linux/macOS
- Suppress errors when sanitizing null values
- Fix `max_len` value check for file names
- Include type annotation information to the package
- Remove `dev` extras_require
- Bug fixes


[Changes][v2.1.0]


<a id="v2.0.0"></a>
# [v2.0.0](https://github.com/thombashi/pathvalidate/releases/tag/v2.0.0) - 2020-01-13

- Change to be more strict validation for absolute paths
- Fix argparse validator/sanitizer failed when empty inputs
- Bug fixes


[Changes][v2.0.0]


<a id="v1.1.0"></a>
# [v1.1.0](https://github.com/thombashi/pathvalidate/releases/tag/v1.1.0) - 2020-01-04

- Modify validate/sanitize functions for `argparse`
- Modify validate/sanitize functions for `click`
- Update `dev` extras


[Changes][v1.1.0]


<a id="v1.0.0"></a>
# [v1.0.0](https://github.com/thombashi/pathvalidate/releases/tag/v1.0.0) - 2020-01-03

- Drop Python 2 support
- Modify to use Python 3 functionality
- Update `extras_require`
- Bug fixes
- Remove a deprecated property


[Changes][v1.0.0]


<a id="v0.29.1"></a>
# [v0.29.1](https://github.com/thombashi/pathvalidate/releases/tag/v0.29.1) - 2020-01-02

- Fix file path length validation: [#10](https://github.com/thombashi/pathvalidate/issues/10) (Thanks to [@UncleGoogle](https://github.com/UncleGoogle))
- Add `.asc` files of packages to PyPI


[Changes][v0.29.1]


<a id="v0.29.0"></a>
# [v0.29.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.29.0) - 2019-06-16

- Add filename/filepath validators for `argparse`/`click`
- Modify error messages

[Changes][v0.29.0]


<a id="v0.28.2"></a>
# [v0.28.2](https://github.com/thombashi/pathvalidate/releases/tag/v0.28.2) - 2019-05-18

- Fix to properly escape special chars for validation error messages: [#9](https://github.com/thombashi/pathvalidate/issues/9) (Thanks to [@UncleGoogle](https://github.com/UncleGoogle))

[Changes][v0.28.2]


<a id="v0.28.0"></a>
# [v0.28.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.28.0) - 2019-05-01

- Drop support for Python 3.4

[Changes][v0.28.0]


<a id="v0.26.0"></a>
# [v0.26.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.26.0) - 2019-03-15

- Add support for NTFS reserved names
- Improve drive letter handling

[Changes][v0.26.0]


<a id="v0.25.0"></a>
# [v0.25.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.25.0) - 2019-03-14

- Add `CLOCK$` as a reserved filename for Windows platform: [#8](https://github.com/thombashi/pathvalidate/issues/8) (Thanks to [@sparr](https://github.com/sparr))
- Improve reserved name detection
- Add `reserved_name` property to `ReservedNameError` class


[Changes][v0.25.0]


<a id="v0.24.1"></a>
# [v0.24.1](https://github.com/thombashi/pathvalidate/releases/tag/v0.24.1) - 2019-02-12

- Fix improper error messages
- Improve error message readability

[Changes][v0.24.1]


<a id="v0.24.0"></a>
# [v0.24.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.24.0) - 2019-02-03

- Add `is_valid_filename`/`is_valid_filepath` function
- Add `FileNameSanitizer`/`FilePathSanitizer` classes
- Add minimum length validation support
- Remove deprecated functions


[Changes][v0.24.0]


<a id="v0.23.0"></a>
# [v0.23.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.23.0) - 2019-01-06

- Improve sanitization/validation for files
- Add `.` and `..` as reserved keywords for files
- Add limit to `max_filename_len`
- Fix platform specific sanitization: [#7](https://github.com/thombashi/pathvalidate/issues/7)
- Fix reserved keywords sanitization/validation for files
- Integrate `InvalidCharWindowsError` into `InvalidCharError`
- Change to use `ReservedNameError` instead of `InvalidReservedNameError`
- Breaking changes
    - Rename a property for `FileSanitizer` from `platform_name` to `platform`
    - Rename methods argument from `platform_name` to `platform`


[Changes][v0.23.0]


<a id="v0.22.0"></a>
# [v0.22.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.22.0) - 2018-12-23

- Add universal (platform independent) filename/filepath sanitization/validation
- Treat ASCII whitespace other than normal space as invalid on Windows [#6](https://github.com/thombashi/pathvalidate/issues/6) (Thanks to [@nyuszika7h](https://github.com/nyuszika7h))


[Changes][v0.22.0]


<a id="v0.21.1"></a>
# [v0.21.1](https://github.com/thombashi/pathvalidate/releases/tag/v0.21.1) - 2018-07-28

- Add support for PathLike object
- Bug fixes


[Changes][v0.21.1]


<a id="v0.18.0"></a>
# [v0.18.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.18.0) - 2018-07-07

- Add validations/sanitizations for unprintable characters
- Add support for Python 3.7

[Changes][v0.18.0]


<a id="v0.15.0"></a>
# [v0.15.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.15.0) - 2017-03-18

- Remove package dependencies
    - pathvalidate functions are expected to passing unicode strings.


[Changes][v0.15.0]


<a id="v0.14.0"></a>
# [v0.14.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.14.0) - 2017-02-11

- Change max file name/path length to configurable
- Add support for Python 3.6
- Bug fixes


[Changes][v0.14.0]


<a id="v0.13.0"></a>
# [v0.13.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.13.0) - 2017-01-03

- Add JavaScript validator/sanitizer
- Bug fixes


[Changes][v0.13.0]


<a id="v0.11.0"></a>
# [v0.11.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.11.0) - 2016-12-25

- Add multibyte character validate/sanitize support


[Changes][v0.11.0]


<a id="v0.10.0"></a>
# [v0.10.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.10.0) - 2016-12-23

- Add LTSV support


[Changes][v0.10.0]


<a id="v0.9.1"></a>
# [v0.9.1](https://github.com/thombashi/pathvalidate/releases/tag/v0.9.1) - 2016-11-17

- Support UTF8


[Changes][v0.9.1]


<a id="v0.9.0"></a>
# [v0.9.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.9.0) - 2016-11-13

- Add validate_symbol function


[Changes][v0.9.0]


<a id="v0.8.2"></a>
# [v0.8.2](https://github.com/thombashi/pathvalidate/releases/tag/v0.8.2) - 2016-10-27

- Fix Windows path validation
- Bug fixes


[Changes][v0.8.2]


<a id="v0.6.0"></a>
# [v0.6.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.6.0) - 2016-09-19

- Add SQLite name validation function


[Changes][v0.6.0]


<a id="v0.5.2"></a>
# [v0.5.2](https://github.com/thombashi/pathvalidate/releases/tag/v0.5.2) - 2016-08-20

- Fix validate/sanitize of excel sheet
- Subdividing errors
- Add file name validation for Windows reserved names and path length


[Changes][v0.5.2]


<a id="v0.5.1"></a>
# [v0.5.1](https://github.com/thombashi/pathvalidate/releases/tag/v0.5.1) - 2016-07-23

- Modify error handling


[Changes][v0.5.1]


<a id="v0.5.0"></a>
# [v0.5.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.5.0) - 2016-07-17

- Drop support for Python 2.6
- Add validate_excel_sheet_name function
- Add sanitize_excel_sheet_name function


[Changes][v0.5.0]


<a id="v0.4.2"></a>
# [v0.4.2](https://github.com/thombashi/pathvalidate/releases/tag/v0.4.2) - 2016-06-19

- Make pytest-runner a conditional requirement


[Changes][v0.4.2]


<a id="v0.4.1"></a>
# [v0.4.1](https://github.com/thombashi/pathvalidate/releases/tag/v0.4.1) - 2016-05-29

- Modify replace_symbol function behavior


[Changes][v0.4.1]


<a id="v0.4.0"></a>
# [v0.4.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.4.0) - 2016-05-28

- Add validate_file_path/sanitize_file_path functions
- Fix validate/sanitize filename functions
- Fix validate/sanitize python variable name functions


[Changes][v0.4.0]


<a id="v0.3.0"></a>
# [v0.3.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.3.0) - 2016-05-22

- Add validate_python_var_name function


[Changes][v0.3.0]


<a id="v0.2.0"></a>
# [v0.2.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.2.0) - 2016-05-21

- Add sanitize_python_var_name function


[Changes][v0.2.0]


<a id="v0.1.0"></a>
# [v0.1.0](https://github.com/thombashi/pathvalidate/releases/tag/v0.1.0) - 2016-03-24



[Changes][v0.1.0]


[v3.3.1]: https://github.com/thombashi/pathvalidate/compare/v3.3.0...v3.3.1
[v3.3.0]: https://github.com/thombashi/pathvalidate/compare/v3.2.3...v3.3.0
[v3.2.3]: https://github.com/thombashi/pathvalidate/compare/v3.2.2...v3.2.3
[v3.2.2]: https://github.com/thombashi/pathvalidate/compare/v3.2.1...v3.2.2
[v3.2.1]: https://github.com/thombashi/pathvalidate/compare/v3.2.0...v3.2.1
[v3.2.0]: https://github.com/thombashi/pathvalidate/compare/v3.1.0...v3.2.0
[v3.1.0]: https://github.com/thombashi/pathvalidate/compare/v3.0.0...v3.1.0
[v3.0.0]: https://github.com/thombashi/pathvalidate/compare/v2.5.2...v3.0.0
[v2.5.2]: https://github.com/thombashi/pathvalidate/compare/v2.5.1...v2.5.2
[v2.5.1]: https://github.com/thombashi/pathvalidate/compare/v2.5.0...v2.5.1
[v2.5.0]: https://github.com/thombashi/pathvalidate/compare/v2.4.1...v2.5.0
[v2.4.1]: https://github.com/thombashi/pathvalidate/compare/v2.4.0...v2.4.1
[v2.4.0]: https://github.com/thombashi/pathvalidate/compare/v2.3.2...v2.4.0
[v2.3.2]: https://github.com/thombashi/pathvalidate/compare/v2.3.1...v2.3.2
[v2.3.1]: https://github.com/thombashi/pathvalidate/compare/v2.3.0...v2.3.1
[v2.3.0]: https://github.com/thombashi/pathvalidate/compare/v2.2.2...v2.3.0
[v2.2.2]: https://github.com/thombashi/pathvalidate/compare/v2.2.1...v2.2.2
[v2.2.1]: https://github.com/thombashi/pathvalidate/compare/v2.2.0...v2.2.1
[v2.2.0]: https://github.com/thombashi/pathvalidate/compare/v2.1.0...v2.2.0
[v2.1.0]: https://github.com/thombashi/pathvalidate/compare/v2.0.0...v2.1.0
[v2.0.0]: https://github.com/thombashi/pathvalidate/compare/v1.1.0...v2.0.0
[v1.1.0]: https://github.com/thombashi/pathvalidate/compare/v1.0.0...v1.1.0
[v1.0.0]: https://github.com/thombashi/pathvalidate/compare/v0.29.1...v1.0.0
[v0.29.1]: https://github.com/thombashi/pathvalidate/compare/v0.29.0...v0.29.1
[v0.29.0]: https://github.com/thombashi/pathvalidate/compare/v0.28.2...v0.29.0
[v0.28.2]: https://github.com/thombashi/pathvalidate/compare/v0.28.0...v0.28.2
[v0.28.0]: https://github.com/thombashi/pathvalidate/compare/v0.26.0...v0.28.0
[v0.26.0]: https://github.com/thombashi/pathvalidate/compare/v0.25.0...v0.26.0
[v0.25.0]: https://github.com/thombashi/pathvalidate/compare/v0.24.1...v0.25.0
[v0.24.1]: https://github.com/thombashi/pathvalidate/compare/v0.24.0...v0.24.1
[v0.24.0]: https://github.com/thombashi/pathvalidate/compare/v0.23.0...v0.24.0
[v0.23.0]: https://github.com/thombashi/pathvalidate/compare/v0.22.0...v0.23.0
[v0.22.0]: https://github.com/thombashi/pathvalidate/compare/v0.21.1...v0.22.0
[v0.21.1]: https://github.com/thombashi/pathvalidate/compare/v0.18.0...v0.21.1
[v0.18.0]: https://github.com/thombashi/pathvalidate/compare/v0.15.0...v0.18.0
[v0.15.0]: https://github.com/thombashi/pathvalidate/compare/v0.14.0...v0.15.0
[v0.14.0]: https://github.com/thombashi/pathvalidate/compare/v0.13.0...v0.14.0
[v0.13.0]: https://github.com/thombashi/pathvalidate/compare/v0.11.0...v0.13.0
[v0.11.0]: https://github.com/thombashi/pathvalidate/compare/v0.10.0...v0.11.0
[v0.10.0]: https://github.com/thombashi/pathvalidate/compare/v0.9.1...v0.10.0
[v0.9.1]: https://github.com/thombashi/pathvalidate/compare/v0.9.0...v0.9.1
[v0.9.0]: https://github.com/thombashi/pathvalidate/compare/v0.8.2...v0.9.0
[v0.8.2]: https://github.com/thombashi/pathvalidate/compare/v0.6.0...v0.8.2
[v0.6.0]: https://github.com/thombashi/pathvalidate/compare/v0.5.2...v0.6.0
[v0.5.2]: https://github.com/thombashi/pathvalidate/compare/v0.5.1...v0.5.2
[v0.5.1]: https://github.com/thombashi/pathvalidate/compare/v0.5.0...v0.5.1
[v0.5.0]: https://github.com/thombashi/pathvalidate/compare/v0.4.2...v0.5.0
[v0.4.2]: https://github.com/thombashi/pathvalidate/compare/v0.4.1...v0.4.2
[v0.4.1]: https://github.com/thombashi/pathvalidate/compare/v0.4.0...v0.4.1
[v0.4.0]: https://github.com/thombashi/pathvalidate/compare/v0.3.0...v0.4.0
[v0.3.0]: https://github.com/thombashi/pathvalidate/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/thombashi/pathvalidate/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/thombashi/pathvalidate/tree/v0.1.0

<!-- Generated by https://github.com/rhysd/changelog-from-release v3.9.0 -->
