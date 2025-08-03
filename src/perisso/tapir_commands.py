import inspect
from typing import Dict, List, Any
from pathlib import Path
import os
from .connection import acc, act
from .enums import ElType, AttrType
from .vector import Vector, Coordinate


def _printcol(text: str):
	text = "\033[91m" + text + "\033[0m"
	print(text)


def _validate_path(path: str | Path, file_ending: str = None, io_op: str = None) -> str:
	"""Validate Path and return normalized string path.

	Args:
		path (*`str | Path`): Path to a file, can include a filename.
		file_ending (`str`): File ending, that needs to be tested for.
		io_op (`str`): I/O operation that should be accomplished. Can be "r" for read or "w" for write.

	Returns:
		Normalized string path for JSON interface.

	Raises:
		ValueError: If path is invalid or doesn't end with the right suffix.
		FileNotFoundError: If parent directory doesn't exist.
	"""
	# Convert to Path object for easier handling
	path = Path(path)

	if file_ending is not None:
		if not file_ending.startswith("."):
			file_ending = "." + file_ending
		# Check if path has right extension
		if path.suffix.lower() != file_ending:
			raise ValueError(
				f"Export path must end with »{file_ending}«, got: {path.suffix}"
			)

	# Check if parent directory exists
	parent_dir = path.parent
	# if not parent_dir.exists():
	# 	raise FileNotFoundError(f"Parent directory does not exist: {parent_dir}")

	# Check if parent directory is actually a directory
	# if not parent_dir.is_dir():
	# 	raise ValueError(f"Parent path is not a directory: {parent_dir}")

	if io_op == "w":
		# Check if we have write permissions to the parent directory
		if not os.access(parent_dir, os.W_OK):
			raise PermissionError(f"No write permission for directory: {parent_dir}")

		# If file already exists, check if we can overwrite it
		if path.exists() and not os.access(path, os.W_OK):
			raise PermissionError(f"No write permission for existing file: {path}")

	if io_op == "r":
		# Check if file exists for read operations
		if not path.exists():
			raise FileNotFoundError(f"File does not exist: {path}")

		# Check if we have read permissions
		if not os.access(path, os.R_OK):
			raise PermissionError(f"No read permission for file: {path}")

	return str(path)


class TapirCommands:
	"""Wrapper for Tapir commands providing IDE intellisense support."""

	def __init__(self):
		self.acc = acc
		self.act = act

	def _run(self, command: str, params: any = None):
		"""Runs the actual command with optional parameters."""
		# Make sure it starts Uppercase, because the commands are registered
		# case-sensitive in Archicad.
		command = command[0].upper() + command[1:]
		if params:
			return self.acc.ExecuteAddOnCommand(
				self.act.AddOnCommandId("TapirCommand", command), params
			)
		else:
			return self.acc.ExecuteAddOnCommand(
				self.act.AddOnCommandId("TapirCommand", command)
			)


# Export a singleton
tapir = TapirCommands()
