"""Utility modules for Context-Fabric.

This module provides helper functions, file operations, and other utilities.
"""

from cfabric.utils.helpers import (
    itemize,
    fitemize,
    collectFormats,
    check32,
    console,
    makeExamples,
    flattenToSet,
    deepSize,
)
from cfabric.utils.files import (
    expanduser,
    unexpanduser,
    LOCATIONS,
    setDir,
    expandDir,
    dirExists,
    normpath,
    splitExt,
    scanDir,
)
from cfabric.utils.timestamp import Timestamp, SILENT_D, DEEP, silentConvert
from cfabric.utils.attrs import AttrDict, deepdict
from cfabric.utils.cli import readArgs

__all__ = [
    # helpers
    "itemize",
    "fitemize",
    "collectFormats",
    "check32",
    "console",
    "makeExamples",
    "flattenToSet",
    "deepSize",
    # files
    "expanduser",
    "unexpanduser",
    "LOCATIONS",
    "setDir",
    "expandDir",
    "dirExists",
    "normpath",
    "splitExt",
    "scanDir",
    # timestamp
    "Timestamp",
    "SILENT_D",
    "DEEP",
    "silentConvert",
    # attrs
    "AttrDict",
    "deepdict",
    # cli
    "readArgs",
]
