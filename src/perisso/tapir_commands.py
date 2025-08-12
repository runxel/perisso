import inspect
import re
from typing import Dict, List, Any
from pathlib import Path
import os
from .connection import acc, act
from .enums import ElType, AttrType, ProjectInfo
from .types import Vector, Coordinate, Color


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

	# region Application Commands
	def getTapirVersion(self) -> str:
		"""Retrieves the version of the installed Tapir Add-On."""
		name_ = "GetAddOnVersion"
		return self._run(name_)["version"]

	def getArchicadLocation(self) -> str:
		"""Retrieves the location of the currently running Archicad executable."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)["archicadLocation"]

	def quitArchicad(self) -> dict:
		"""Performs a quit operation on the currently running Archicad instance."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def getCurrentWindowType(self) -> str:
		"""Returns the type of the current (active) window."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)["currentWindowType"]

	# endregion
	# region 	Project Commands
	def getProjectInfo(self) -> dict:
		"""Retrieves information about the currently loaded project."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def getProjectInfoFields(self) -> dict:
		"""Retrieves the names and values of all project info fields."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def setProjectInfoField(
		self, projectInfoId: str | ProjectInfo, projectInfoValue: str
	) -> dict:
		"""Sets the value of a project info field.

		Args:
			projectInfoId (`str | ProjectInfo`): The ID of the project info field, either as a string
				or a `ProjectInfo`-class member (enum).
			projectInfoValue (`str`): The new value of the project info field.
		"""
		name_ = inspect.currentframe().f_code.co_name
		if isinstance(projectInfoId, ProjectInfo):
			projectInfoId = projectInfoId.value
		params = {"projectInfoId": projectInfoId, "projectInfoValue": projectInfoValue}
		return self._run(name_, params)

	def getStories(self) -> dict:
		"""Retrieves information about the story sructure of the currently loaded project."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def getHotlinks(self) -> dict:
		"""Gets the file system locations (path) of the hotlink modules. The hotlinks can have tree hierarchy in the project."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def openProject(self, path: str | Path) -> dict:
		"""Opens the given project."""
		name_ = inspect.currentframe().f_code.co_name
		path = _validate_path(path, io_op="r")
		params = {"projectFilePath": path}
		return self._run(name_, params)

	def getGeoLocation(self) -> dict:
		"""Gets the project location details."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	# endregion
	# region 	Element Commands

	# The following commands are not integrated, since Perisso covers it:
	# 	GetSelectedElements
	# 	GetElementsByType
	# 	GetAllElements
	# 	ChangeSelectionOfElements
	# 	FilterElements

	def getDetailsOfElements(self, elements: List[Dict[str, str]]) -> dict:
		"""Get details of given elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": elements}
		return self._run(name_, params)
	def get3DBoundingBoxes(self, elements: List[Dict[str, str]]) -> Dict[str, Any]:
		"""Get 3D bounding boxes of elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": elements}
		return self._run(name_, params)

	def getSubelementsOfHierarchicalElements(
		self, elements: List[Dict[str, str]]
	) -> dict:
		"""Gets the subelements of the given hierarchical elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": elements}
		return self._run(name_, params)

	def getConnectedElements(
		self, elements: List[Dict[str, str]], connectedElementType: ElType
	) -> dict:
		"""Gets the subelements of the given hierarchical elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"elements": elements,
			"connectedElementType": connectedElementType.value,
		}
		return self._run(name_, params)

	def highlightElements(
		self,
		elements: Dict[str, str] = None,
		*,
		hightlightcolor: list[list[int]] = [[77, 235, 103, 100]],
		mutedcolor: list[int] = [164, 166, 165, 128],
		wireframe=True,
	) -> None:
		"""Highlight the elements in the given color and mutes all other elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"elements": elements,
			"highlightedColors": hightlightcolor,
			"wireframe3D": wireframe,
			"nonHighlightedColor": mutedcolor,
		}
		return self._run(name_, params)

	def clearHighlight(self):
		"""Clear all highlighting in Archicad."""
		# A helper function – this does not exist as it's own Tapir command.
		return self.highlightElements(elements=[None])

	def moveElements(
		self, elements: Dict[str, str], vector: Vector, copy: bool = False
	):
		"""Moves elements with a given vector."""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"elementsWithMoveVectors": [
				{
					"elementId": el["elementId"],
					"moveVector": vector.to_3d().to_dict(),
					"copy": copy,
				}
				for el in elements
			]
		}
		return self._run(name_, params)

	def getGDLParametersOfElements(self, elements: List[Dict[str, str]]) -> dict:
		"""Gets all the GDL parameters (name, type, value) of the given elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": elements}
		return self._run(name_, params)
	# endregion
	# region 	Create Elements
	def createColumns(self, coors: List[Coordinate]) -> dict:
		"""Creates Column elements based on the given parameters."""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"columnsData": [{"coordinates": coor.to_3d().to_dict()} for coor in coors]
		}
		return self._run(name_, params)
	# endregion
	# region 	Favorites Commands
	def applyFavoritesToElementDefaults(self, favoriteNames: str) -> dict:
		"""Apply the given favorites to their respective element tool defaults."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"favorites": [favoriteNames]}
		return self._run(name_, params)

	def createFavoritesFromElements(
		self, elements: List[Dict[str, str]], favoriteNames: List[str]
	) -> dict:
		"""Create favorites from the given elements."""
		name_ = inspect.currentframe().f_code.co_name
		if isinstance(favoriteNames, str):
			# make sure we get a list
			favoriteNames = [favoriteNames]
		params = {
			"favoritesFromElements": [
				{
					"elementId": el["elementId"],
					"favorite": favname,
				}
				for el, favname in zip(elements, favoriteNames)
			]
		}
		return self._run(name_, params)

	# endregion
	# region 	Property Commands
	def getAllProperties(self) -> dict:
		"""Returns all user defined and built-in properties."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def getPropertyValuesOfElements(
		self, elements: List[Dict[str, str]], propertyGUIDs: List[str]
	) -> Dict[str, Any]:
		"""
		Get property values of elements.

		Args:
			elements: List of element dictionaries with identification info
			properties: List of property parameters with propertyId mappings

		Returns:
			Dictionary containing the property values for the requested elements
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"elements": elements,
			"properties": [{"propertyId": {"guid": pg}} for pg in propertyGUIDs],
		}
		return self._run(name_, params)
	# endregion
	# region 	Attribute Commands
	# endregion
	# region 	Library Commands
	def getLibraries(self) -> Dict[str, Any]:
		"""Gets the list of loaded libraries."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def reloadLibraries(self) -> Dict[str, Any]:
		"""Executes the reload libraries command."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	# endregion
	# region 	Teamwork Commands
	def _twTest(self, command: str) -> bool:
		"""Internal function that will warn if a file is not a TW file."""
		if not self.getProjectInfo()["isTeamwork"]:
			_printcol(f"Not a Teamwork file! Command »{command}« will not be sent.")
			return False
		return True

	def teamworkSend(self) -> Dict[str, Any]:
		"""Performs a send operation on the currently opened Teamwork project."""
		name_ = inspect.currentframe().f_code.co_name
		if self._twTest(name_):
			return self._run(name_)
		return None
	# endregion
	# region 	Navigator Commands

	# endregion
	# region 	Issue Management Commands
	# endregion
	# region 	Revision Management Commands
	def getRevisionIssues(self) -> Dict[str, Any]:
		"""Retrieves all issues."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def getRevisionChanges(self) -> Dict[str, Any]:
		"""Retrieves all changes."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def getDocumentRevisions(self) -> Dict[str, Any]:
		"""Retrieves all document revisions."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)
	# endregion


# Export a singleton
tapir = TapirCommands()
