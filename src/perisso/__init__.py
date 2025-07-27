# This file initializes the perisso package.

from .core import perisso, clearhighlight
from .enums import Filter, ElType
from .version import version as __version__


__all__ = [
	"perisso",
	"clearhighlight",
	"Filter",
	"ElType",
	"__version__",
]
