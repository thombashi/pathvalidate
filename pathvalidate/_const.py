import enum
from typing import Final


DEFAULT_MIN_LEN: Final = 1
INVALID_CHAR_ERR_MSG_TMPL: Final = "invalids=({invalid})"


_NTFS_RESERVED_FILE_NAMES: Final = (
    "$Mft",
    "$MftMirr",
    "$LogFile",
    "$Volume",
    "$AttrDef",
    "$Bitmap",
    "$Boot",
    "$BadClus",
    "$Secure",
    "$Upcase",
    "$Extend",
    "$Quota",
    "$ObjId",
    "$Reparse",
)  # Only in root directory


@enum.unique
class LengthBehavior(enum.Enum):
    """Length policy applied after character replacement and before name handlers."""

    #: Keep the full name; final validation can still reject its length.
    KEEP = "keep"
    #: Truncate the entire name (the default).
    TRIM = "trim"
    #: Truncate the stem while preserving the final extension.
    TRIM_NAME = "trim_name"
    #: Raise INVALID_LENGTH if the name exceeds the byte budget.
    ERROR = "error"


@enum.unique
class Platform(enum.Enum):
    """
    Platform specifier enumeration.
    """

    #: POSIX compatible platform.
    POSIX = "POSIX"

    #: platform independent. note that absolute paths cannot specify this.
    UNIVERSAL = "universal"

    LINUX = "Linux"
    WINDOWS = "Windows"
    MACOS = "macOS"
