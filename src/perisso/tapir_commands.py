import os
import inspect
from typing import Dict, List, Any, Literal, TYPE_CHECKING
from pathlib import Path

# Only import for type checking, not at runtime
if TYPE_CHECKING:
	from .collection import ElementCollection

from .connection import acc, act
from .enums import ElType, AttrType, ProjectInfo
from .types import Vector, Coordinate, Polyline, Polygon, Color
from .type_utils import polygon_centroid
from .helper import zip_repeat_last, _printcol
from .guid import _is_guid


def _ensure_elem_list(elements):
	"""Helper function to return the list, not an object."""
	# Import here to avoid circular imports
	from .collection import ElementCollection

	if isinstance(elements, ElementCollection):
		return elements.get()
	return elements


def _validate_path(
	path: str | Path, file_ending: str = None, io_op: Literal[None, "r", "w"] = None
) -> str:
	"""Validates a Path and returns the normalized string path.

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
		if params:
			return self.acc.ExecuteAddOnCommand(
				self.act.AddOnCommandId("TapirCommand", command), params
			)
		else:
			return self.acc.ExecuteAddOnCommand(
				self.act.AddOnCommandId("TapirCommand", command)
			)

	# region 	Helper Defs
	def _find_idx_of_attr(self, attributeType: str | AttrType, nameOrGuid: str) -> int:
		"""Finds the index of an attribute by name or GUID.

		Args:
			attributeType: The type of attribute to search in
			nameOrGuid: Either the name or GUID of the attribute to find

		Returns:
			int: The index of the attribute

		Raises:
			ValueError: If the attribute is not found
		"""
		attr_response = self.GetAttributesByType(attributeType)
		attributes = attr_response.get("attributes", [])

		if _is_guid(nameOrGuid):
			# Search by GUID
			for attr in attributes:
				if attr["attributeId"]["guid"] == nameOrGuid:
					return attr["index"]
		else:
			# Search by name
			for attr in attributes:
				if attr["name"] == nameOrGuid:
					return attr["index"]

		# If not found, raise an error
		attr_type_str = (
			attributeType.value
			if isinstance(attributeType, AttrType)
			else attributeType
		)
		raise ValueError(
			f"Attribute '{nameOrGuid}' not found in {attr_type_str} attributes"
		)

	def _find_guid_of_attr(self, attributeType: str | AttrType, name: str) -> str:
		"""Finds the GUID of an Attribute. If not found raises a ValueError."""
		attr_response = self.GetAttributesByType(attributeType)
		attributes = attr_response.get("attributes", [])

		# Search by name
		for attr in attributes:
			if attr["name"] == name:
				return attr["attributeId"]["guid"]

		# If not found, raise an error
		attr_type_str = (
			attributeType.value
			if isinstance(attributeType, AttrType)
			else attributeType
		)
		raise ValueError(f"Attribute '{name}' not found in {attr_type_str} attributes")

	# endregion
	# region 	Application Commands
	def GetAddOnVersion(self) -> str:
		"""Retrieves the version of the installed Tapir Add-On."""
		# OG Tapir
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)["version"]

	def GetTapirVersion(self) -> str:
		"""Retrieves the version of the installed Tapir Add-On."""
		# Alias Function which is better named :)
		return self.GetAddOnVersion()

	def GetArchicadLocation(self) -> str:
		"""Retrieves the location of the currently running Archicad executable."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)["archicadLocation"]

	def QuitArchicad(self) -> dict:
		"""Performs a quit operation on the currently running Archicad instance."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def GetCurrentWindowType(self) -> str:
		"""Returns the type of the current (active) window."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)["currentWindowType"]

	# endregion
	# region 	Project Commands
	def GetProjectInfo(self) -> dict:
		"""Retrieves information about the currently loaded project."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def GetProjectInfoFields(self) -> dict:
		"""Retrieves the names and values of all project info fields."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def SetProjectInfoField(
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

	def GetStories(self) -> dict:
		"""Retrieves information about the story structure of the project."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def SetStories(
		self, names: list[str], levels: list[float], dispOnSections: list[bool] = None
	) -> dict:
		"""Sets the story structure of the project. \n
		This means that the current structure will not be appended but replaced.

		Args:
			names (`str`): The name of the story.
			levels (`float`): The story level.
			dispOnSections (`bool`): Determines if story level lines should appear on sections and elevations.
				Reverts to `True` if not specified.
		"""
		name_ = inspect.currentframe().f_code.co_name

		if dispOnSections is None:
			dispOnSections = [True for _ in range(len(levels))]

		params = {
			"stories": [
				{"dispOnSections": display, "level": level, "name": name}
				for name, level, display in zip_repeat_last(
					names, levels, dispOnSections
				)
			]
		}
		return self._run(name_, params)

	def GetHotlinks(self) -> dict:
		"""Gets the file system locations (path) of the hotlink modules.
		The hotlinks can have a tree hierarchy in the project."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def OpenProject(self, path: str | Path) -> dict:
		"""Opens the given project."""
		name_ = inspect.currentframe().f_code.co_name
		path = _validate_path(path, io_op="r")
		params = {"projectFilePath": path}
		return self._run(name_, params)

	def GetGeoLocation(self) -> dict:
		"""Gets the project's location details."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	# endregion
	# region 	Element Commands

	# The following commands are not integrated, since Perisso covers it:
	# 	GetSelectedElements
	# 	GetElementsByType
	# 	GetAllElements
	# 	FilterElements

	def ChangeSelectionOfElements(
		self,
		addElem: "ElementCollection" | List[Dict[str, str]] = None,
		subElem: "ElementCollection" | List[Dict[str, str]] = None,
	) -> dict:
		"""Modifies the current selection of elements in Archicad by Adding or Removing a number of elements from it."""
		name_ = inspect.currentframe().f_code.co_name
		addElem = _ensure_elem_list(addElem)
		subElem = _ensure_elem_list(subElem)
		params = {
			"addElementsToSelection": addElem,
			"removeElementsFromSelection": subElem,
		}
		return self._run(name_, params)

	def GetDetailsOfElements(
		self, elements: "ElementCollection" | List[Dict[str, str]]
	) -> dict:
		"""Get details of given elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": _ensure_elem_list(elements)}
		return self._run(name_, params)

	def SetDetailsOfElements(
		self,
		elements: "ElementCollection" | List[Dict[str, str]],
		*,
		story: int = None,
		layer: int | str = None,
		drawIndex: int = None,
		typeSpecificDetails: dict = None,
	) -> dict:
		"""Sets the details of the given elements (story, layer, order etc).

		Args:
			elements (*`ElementCollection`): Elements to modify
			story: Optional story index
			layer: Optional layer (index or name)
			drawIndex: Optional drawing order index
			typeSpecificDetails: Optional type-specific details (currently: Only Walls supported)
		"""
		name_ = inspect.currentframe().f_code.co_name
		elements = _ensure_elem_list(elements)

		# Build details dict only with provided parameters
		details_base = {}
		if story is not None:
			details_base["floorIndex"] = story
		if layer is not None:
			if isinstance(layer, str):
				# name or GUID
				details_base["layerIndex"] = self._find_idx_of_attr(
					AttrType.LAYER, layer
				)
			else:
				details_base["layerIndex"] = layer
		if drawIndex is not None:
			details_base["drawIndex"] = drawIndex
		if typeSpecificDetails is not None:
			details_base.update(typeSpecificDetails)

		params = {
			"elementsWithDetails": [
				{"elementId": el["elementId"], "details": details_base}
				for el in elements
			]
		}
		return self._run(name_, params)

	def Get3DBoundingBoxes(
		self, elements: "ElementCollection" | List[Dict[str, str]]
	) -> Dict[str, any]:
		"""Get 3D bounding boxes of elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": _ensure_elem_list(elements)}
		return self._run(name_, params)

	def GetSubelementsOfHierarchicalElements(
		self, elements: "ElementCollection" | List[Dict[str, str]]
	) -> dict:
		"""Gets the subelements of the given hierarchical elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": _ensure_elem_list(elements)}
		return self._run(name_, params)

	def GetConnectedElements(
		self,
		elements: "ElementCollection" | List[Dict[str, str]],
		connectedElementType: ElType | str,
	) -> dict:
		"""Gets the subelements of the given hierarchical elements."""
		name_ = inspect.currentframe().f_code.co_name
		if isinstance(connectedElementType, ElType):
			connElem = connectedElementType.value
		else:
			connElem = connectedElementType
		params = {
			"elements": _ensure_elem_list(elements),
			"connectedElementType": connElem,
		}
		return self._run(name_, params)

	def GetZoneBoundaries(
		self,
		zone: "ElementCollection" | Dict[str, str],
	) -> Dict:
		"""Gets the boundaries of the given Zone (connected elements, neighbour zones, etc.)."""
		name_ = inspect.currentframe().f_code.co_name
		el = _ensure_elem_list(zone)
		params = {"zoneElementId": el["elementId"]}
		return self._run(name_, params)

	def GetCollisions(
		self,
		elementGroup1: "ElementCollection" | List[Dict[str, str]],
		elementGroup2: "ElementCollection" | List[Dict[str, str]],
		volumeTolerance: float = 0.001,
		performSurfaceCheck: bool = False,
		surfaceTolerance: float = 0.001,
	) -> dict:
		"""Detects collisions between the given two groups of elements.

		Args:
			elementGroup1 (`ElementCollection` | `List[Dict[str, str]]`): List of elements.
			elementGroup2 (`ElementCollection` | `List[Dict[str, str]]`): List of elements.
			volumeTolerance (`float`): Intersection body volume greater than this value will be considered as a collision.
			    Default value is 0.001.
			performSurfaceCheck (`bool`): Enables surface collision check. If disabled the `surfaceTolerance`
			    value will be ignored. By default it's false.
			surfaceTolerance (`float`): Intersection body surface area greater than this value will be
			    considered as a collision. Default value is 0.001.
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"elementsGroup1": _ensure_elem_list(elementGroup1),
			"elementsGroup2": _ensure_elem_list(elementGroup2),
			"settings": {
				"volumeTolerance": volumeTolerance,
				"performSurfaceCheck": performSurfaceCheck,
				"surfaceTolerance": surfaceTolerance,
			},
		}
		return self._run(name_, params)

	def HighlightElements(
		self,
		elements: "ElementCollection" | List[Dict[str, str]] = None,
		*,
		highlightcolor: Color | List[Color] = Color("green"),
		mutedcolor: Color = Color(164, 166, 165, 128),
		wireframe=True,
	) -> None:
		"""Highlight the elements in the given color and mute all other elements.

		Args:
			highlightcolor (`Color | List[Color]`): A Color or list of Colors used to highlight the element(s).
			mutedcolor (`Color`): A Color to be used on the non-highlighted elements. Optional.
			wirefame (`bool`): Switch non-highlighted elements in the 3D window to wireframe. Optional.
		"""
		name_ = inspect.currentframe().f_code.co_name

		elements = _ensure_elem_list(elements)

		if not isinstance(highlightcolor, list):
			highlightcolor = [highlightcolor.rgba for _ in elements]
		else:
			highlightcolor = [
				color.rgba if isinstance(color, Color) else color
				for color in highlightcolor
			]

		if len(highlightcolor) != len(elements):
			if len(highlightcolor) > len(elements):
				# Truncate the color list to match elements
				highlightcolor = highlightcolor[: len(elements)]
			elif len(highlightcolor) > 0:
				# Repeat the last color until we have enough colors for all elements
				last_color = highlightcolor[-1]
				while len(highlightcolor) < len(elements):
					highlightcolor.append(last_color)
			else:
				# If somehow we have an empty color list, use default color
				default_rgba = Color("green").rgba
				highlightcolor = [default_rgba for _ in elements]

		params = {
			"elements": elements,
			"highlightedColors": highlightcolor,
			"wireframe3D": wireframe,
			"nonHighlightedColor": mutedcolor.rgba,
		}
		return self._run(name_, params)

	def ClearHighlight(self):
		"""Clear all highlighting in Archicad."""
		# A helper function – this does not actually exist as it's own Tapir command.
		return self.HighlightElements(elements=[None])

	def MoveElements(
		self,
		elements: "ElementCollection" | List[Dict[str, str]],
		vector: Vector,
		copy: bool = False,
	):
		"""Moves elements with a given vector."""
		name_ = inspect.currentframe().f_code.co_name
		elements = _ensure_elem_list(elements)
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

	def DeleteElements(
		self, elements: "ElementCollection" | List[Dict[str, str]]
	) -> dict:
		"""Deletes elements.
		Tapir: 1.2.1"""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": _ensure_elem_list(elements)}
		return self._run(name_, params)

	def GetGDLParametersOfElements(
		self, elements: "ElementCollection" | List[Dict[str, str]]
	) -> dict:
		"""Gets all the GDL parameters (name, type, value) of the given elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": _ensure_elem_list(elements)}
		return self._run(name_, params)

	def SetGDLParametersOfElements(
		self,
		elements: "ElementCollection" | List[Dict[str, str]],
		gdlParams: List[Dict] | List[tuple],
	) -> dict:
		"""Sets the given GDL parameters of the given elements.

		Args:
			elements (*`ElementCollection`|`List[Dict[str, str]]`): The list of objects that should be altered.
			gdlParams (*`List[Dict]`|`List[tuple]`): Either a list of dicts (see Tapir docs) or as a shortcut a list of
			   tuples where the first item is the name of the GDL Parameter as a string and the second item is the value
			   the parameter should be assigned to.
		"""
		name_ = inspect.currentframe().f_code.co_name

		elements = _ensure_elem_list(elements)

		# Check if all elements are dicts
		if gdlParams and all(isinstance(item, dict) for item in gdlParams):
			# in that case we can just use it as is
			# this is meant for everything beyond just setting a single Parameter
			params = {
				"elementsWithGDLParameters": [
					{
						"elementId": el["elementId"],
						"gdlParameters": gdlParams,
					}
					for el in elements
				]
			}
		# Check if all elements are tuples
		elif gdlParams and all(isinstance(item, tuple) for item in gdlParams):
			# with tuples we can assume that first item is the name and the second the new assigned value
			params = {
				"elementsWithGDLParameters": [
					{
						"elementId": el["elementId"],
						"gdlParameters": [
							{"name": gp[0], "value": gp[1]} for gp in gdlParams
						],
					}
					for el in elements
				]
			}
		else:
			raise TypeError(
				"The argument for `gdlParams` must be a list of dicts or tuples."
			)

		return self._run(name_, params)

	def GetClassificationsOfElements(
		self,
		elements: "ElementCollection" | List[Dict[str, str]],
		classificationSystemIds: List[str] | List[Dict] = None,
		resolve: bool = False,
	) -> dict:
		"""Returns the classification of the given elements in the given classification systems.
		It also works for subelements of hierarchal elements.
		Use it with `acc.GetAllClassificationSystems()`.

		Args:
			elements (*): Elements
			classificationSystemIds (`List[str] | List[Dict]`): GUIDs of the Classification Systems as strings, or
				a ready made List of Dicts, like `[{'classificationSystemId': {'guid': 'B6636241-937D-234D-902F-2D30E4BD0FB8'}, ...]`
			resolve (`bool`): If True, returns human-readable names instead of GUIDs
		"""
		name_ = inspect.currentframe().f_code.co_name

		if classificationSystemIds is None:
			# means we check for all available Classifications
			_cls = acc.GetAllClassificationSystems()
			_csid = []
			for cs in _cls:
				_csid.append(cs.to_dict()["classificationSystemId"]["guid"])
			classificationSystemIds = _csid

		# classificationSystemIds is List[str], or was 'None' before and is now a list of strings
		if isinstance(classificationSystemIds[0], str):
			classificationSystemIds = [
				{"classificationSystemId": {"guid": cs}}
				for cs in classificationSystemIds
			]
		# else it should be a List[Dict] and we passing this thru directly
		params = {
			"elements": _ensure_elem_list(elements),
			"classificationSystemIds": classificationSystemIds,
		}
		result = self._run(name_, params)

		if not resolve:
			return result

		# Resolve classification names
		def _find_classification_name_in_tree(tree: list, target_guid: str) -> str:
			"""Recursively search for classification item by GUID in the tree."""
			for item in tree:
				if isinstance(item, self.act.ClassificationItemArrayItem):
					# first level is of type "ClassificationItemArrayItem", so we need to make a dict first
					# at deeper levels the input tree (recursion duh!) _is_ already a dict
					item = item.to_dict()
				classification_item = item["classificationItem"]
				if classification_item["classificationItemId"]["guid"] == target_guid:
					return classification_item["id"]

				# Search in children if they exist
				if "children" in classification_item:
					found = _find_classification_name_in_tree(
						classification_item["children"], target_guid
					)
					if found:
						return found
			return None

		# Get all classification systems for name resolution
		all_systems = self.acc.GetAllClassificationSystems()
		system_lookup = {}
		classification_trees = {}

		# Build lookup tables
		for system in all_systems:
			system_dict = system.to_dict()
			system_guid = system_dict["classificationSystemId"]["guid"]
			system_name = system_dict["name"]
			system_lookup[system_guid] = system_name

			# Get classification tree for this system
			actcsid = self.act.ClassificationSystemId(system_guid)
			tree = self.acc.GetAllClassificationsInSystem(actcsid)
			classification_trees[system_guid] = tree

		# Process the original results list
		resolved_results = []

		for element_classification in result["elementClassifications"]:
			element_resolved = []

			for classification in element_classification["classificationIds"]:
				system_guid = classification["classificationSystemId"]["guid"]
				item_guid = classification["classificationItemId"]["guid"]

				# Get system name
				system_name = system_lookup.get(system_guid, "Unknown System")

				# Get classification name
				classification_name = None
				if item_guid != "00000000-0000-0000-0000-000000000000":
					tree = classification_trees.get(system_guid, [])
					classification_name = _find_classification_name_in_tree(
						tree, item_guid
					)

				element_resolved.append(
					{
						"classificationSystemName": system_name,
						"classificationName": classification_name,
					}
				)

			resolved_results.append(element_resolved)

		return resolved_results

	def SetClassificationsOfElements(
		self,
		elements: "ElementCollection" | List[Dict[str, str]],
		classificationId: Dict = None,
		*,
		classificationSystemId: str = "",
		classificationItemId: str = "",
	) -> dict:
		"""Sets the classification of elements. In order to set the classification of an element to unclassified,
		omit the 'classificationItemId' field. It works for subelements of hierarchal elements also.

		Either provide a full `classificationId` dict or the system and item ID.
		Those can be either GUIDS or real-named strings."""
		name_ = inspect.currentframe().f_code.co_name

		elements = _ensure_elem_list(elements)

		if classificationId and classificationSystemId != "":
			raise ValueError(
				"Warning: Do not provide both `classificationId` and `classificationSystemId`!"
			)

		# Build classificationId if not provided
		if classificationId is None:
			if classificationSystemId == "":
				raise ValueError(
					"Either `classificationId` or `classificationSystemId` must be provided"
				)

			# Handle classificationSystemId - convert name to GUID if needed
			if _is_guid(classificationSystemId):
				system_guid = classificationSystemId
			else:
				# Find GUID by name
				all_systems = self.acc.GetAllClassificationSystems()
				system_guid = None
				for system in all_systems:
					system_dict = system.to_dict()
					if system_dict["name"] == classificationSystemId:
						system_guid = system_dict["classificationSystemId"]["guid"]
						break

				if system_guid is None:
					raise ValueError(
						f"Classification system not found: {classificationSystemId}"
					)

			# Handle classificationItemId - convert name to GUID if needed
			item_guid = None
			if classificationItemId != "":
				if _is_guid(classificationItemId):
					item_guid = classificationItemId
				else:
					# Find GUID by name in the classification tree
					actcsid = self.act.ClassificationSystemId(system_guid)
					tree = self.acc.GetAllClassificationsInSystem(actcsid)

					def _find_guid_by_name(tree: list, target_name: str) -> str:
						"""Recursively search for classification item GUID by name."""
						for item in tree:
							if isinstance(item, self.act.ClassificationItemArrayItem):
								item = item.to_dict()
							classification_item = item["classificationItem"]
							if classification_item["id"] == target_name:
								return classification_item["classificationItemId"][
									"guid"
								]

							# Search in children if they exist
							if "children" in classification_item:
								found = _find_guid_by_name(
									classification_item["children"], target_name
								)
								if found:
									return found
						return None

					item_guid = _find_guid_by_name(tree, classificationItemId)
					if item_guid is None:
						# that should unset that Classification
						pass

			# Build the classificationId dict
			classificationId = {"classificationSystemId": {"guid": system_guid}}
			if item_guid is not None:
				classificationId["classificationItemId"] = {"guid": item_guid}

		params = {
			"elementClassifications": [
				{"elementId": el["elementId"], "classificationId": classificationId}
				for el in elements
			]
		}
		return self._run(name_, params)

	# endregion
	# region 	Create Elements
	def CreateColumns(self, coors: Coordinate | list[Coordinate]) -> dict:
		"""Creates Column elements based on the given parameters."""
		name_ = inspect.currentframe().f_code.co_name
		if isinstance(coors, list):
			coors = [coors]
		params = {
			"columnsData": [{"coordinates": coor.to_3d().to_dict()} for coor in coors]
		}
		return self._run(name_, params)

	def CreateSlabs(
		self,
		polylines: List[Polyline] | Polyline,
		holes: List[Polyline] = None,
		level: float = 0.0,
	) -> dict:
		"""Creates Slab elements based on the given parameters.

		Args:
			polylines: Polyline objects defining the slab boundary, or list of Polylines for multiple slabs.
			holes: Optional list of Polyline objects defining holes in the slab.
			level (`float`): Z-level of the slab.

		Note: All polylines will be automatically closed for slab creation.
		"""
		name_ = inspect.currentframe().f_code.co_name

		# Handle single Polyline or list of Polylines
		if isinstance(polylines, Polyline):
			polylines = [polylines]

		slabs_data = []
		for polyline in polylines:
			# Ensure the polyline is closed for slab creation
			if not polyline.is_closed:
				polyline.close()

			# Convert polyline to dictionary format
			polyline_dict = polyline.to_dict()

			# Prepare holes data
			holes_data = []
			if holes:
				for hole in holes:
					if isinstance(hole, Polyline):
						# Ensure hole polylines are also closed
						if not hole.is_closed:
							hole.close()

						hole_dict = hole.to_dict()
						hole_data = {"polygonCoordinates": hole_dict["coordinates"]}

						# Add arcs if they exist for this hole
						if "arcs" in hole_dict:
							hole_data["polygonArcs"] = hole_dict["arcs"]

						holes_data.append(hole_data)
					else:
						raise TypeError("Holes must be Polyline objects")

			# Build slab data structure
			slab_data = {
				"level": level,
				"polygonCoordinates": polyline_dict["coordinates"],
				"holes": holes_data,
			}

			# Add arcs if they exist
			if "arcs" in polyline_dict:
				slab_data["polygonArcs"] = polyline_dict["arcs"]

			slabs_data.append(slab_data)

		params = {"slabsData": slabs_data}
		return self._run(name_, params)

	def CreateZones(
		self,
		zoneName: str = "",
		zoneNumber: str = "",
		story: int = None,
		*,
		zoneCategory: str | Any = None,
		geometryType: Literal["auto", "manual"] = "auto",
		coorAuto: Coordinate = None,
		coorsManual: Polygon = None,
		stampPosition: Coordinate = None,
	) -> dict:
		"""Creates Zone elements based on the given parameters."""
		name_ = inspect.currentframe().f_code.co_name

		if stampPosition is None:
			if geometryType == "manual":
				if coorsManual is None:
					raise ValueError(
						"In this configuration you need to set the outline manually."
					)
				_poly = [coor for coor in coorsManual]
				centroid = polygon_centroid(_poly)
			else:
				if coorAuto is None:
					raise ValueError(
						"In this configuration you need to set the reference Position ('coorAuto')."
					)
				centroid = coorAuto
		else:
			centroid = stampPosition
		zst_pos = {"x": centroid.x, "y": centroid.y}

		if zoneCategory is None:
			# Get all zone categories and find the one with the lowest index
			zone_cats_response = self.GetAttributesByType(AttrType.ZONECATEGORY)
			attributes = zone_cats_response.get("attributes", [])
			if attributes:
				# Find attribute with lowest index
				lowest_attr = min(attributes, key=lambda x: x["index"])
				zoneCategory = {"guid": lowest_attr["attributeId"]["guid"]}
		else:
			# Check if zoneCategory is already a GUID or needs to be resolved by name
			if isinstance(zoneCategory, str):
				if _is_guid(zoneCategory):
					# It's already a GUID
					zoneCategory = {"guid": zoneCategory}
				else:
					# It's a name, so let's find the corresponding GUID
					zone_cats_response = self.GetAttributesByType(AttrType.ZONECATEGORY)
					attributes = zone_cats_response.get("attributes", [])
					found_guid = None
					for attr in attributes:
						if attr["name"] == zoneCategory:
							found_guid = attr["attributeId"]["guid"]
							break

					if found_guid is None:
						raise ValueError(f"Zone category '{zoneCategory}' not found.")

					zoneCategory = {"guid": found_guid}
			# If it's already a dict with guid, leave it as is

		if geometryType == "auto":
			geo = {"referencePosition": {"x": coorAuto.x, "y": coorAuto.y}}
		else:
			geo = {coorsManual.to_dict()}

		params = {
			"zonesData": [
				{
					"name": zoneName,
					"numberStr": zoneNumber,
					"categoryAttributeId": zoneCategory,
					"stampPosition": zst_pos,
					"geometry": geo,
				}
			]
		}

		if story is not None:
			params["zonesData"][0]["floorIndex"] = story
		# print(params)
		return self._run(name_, params)

	def CreatePolylines(
		self, polylines: List[Polyline] | Polyline, floorInd: int = None
	) -> dict:
		"""Creates Polyline elements based on the given parameters."""
		name_ = inspect.currentframe().f_code.co_name

		# Handle single Polyline or list of Polylines
		if isinstance(polylines, Polyline):
			polylines = [polylines]

		polylines_data = []
		for polyline in polylines:
			# Convert polyline to dictionary format
			polyline_dict = polyline.to_dict()

			# Add floor index if specified
			if floorInd is not None:
				polyline_dict["floorInd"] = floorInd

			polylines_data.append(polyline_dict)

		params = {"polylinesData": polylines_data}
		return self._run(name_, params)

	def CreateObjects(
		self,
		objName: str | list[str],
		coors: Coordinate | list[Coordinate],
		dimensions: tuple[float] | list[tuple[float]] = None,
	) -> dict:
		"""Places Objects in the project based on the given parameters. \n
		List lengths can differ. The last item will be repeated.

		Dimensions are optional.
		"""
		name_ = inspect.currentframe().f_code.co_name

		if not isinstance(objName, list):
			objName = [objName]
		if not isinstance(coors, list):
			coors = [coors]

		if dimensions is None:
			params = {
				"objectsData": [
					{
						"libraryPartName": name,
						"coordinates": coor.to_3d().to_dict(),
					}
					for name, coor in zip_repeat_last(objName, coors)
				]
			}
		else:
			if not isinstance(dimensions, list):
				dimensions = [dimensions]

			params = {
				"objectsData": [
					{
						"libraryPartName": name,
						"coordinates": coor.to_3d().to_dict(),
						"dimensions": dim,
					}
					for name, coor, dim in zip_repeat_last(objName, coors, dimensions)
				]
			}

		return self._run(name_, params)

	def CreateMeshes(
		self,
		outline: Polygon,
		level: float,
		skirtType: Literal[
			"SurfaceOnlyWithoutSkirt", "WithSkirt", "SolidBodyWithSkirt"
		],
		skirtLevel: float = None,
		story: int = None,
		sublines: list[Coordinate] = None,
	) -> dict:
		"""Creates Meshes based on the given parameters.

		Args:
			story: Index of the Home Story.
			level: The Z reference level of the mesh.
			skirtLevel: Skirt height (optional).
			sublines: The leveling sublines inside the polygon of the mesh. Just an unordered list of 3D-Coordinates
		"""
		name_ = inspect.currentframe().f_code.co_name

		params = {
			"meshesData": [
				{
					"skirtType": skirtType,
					"polygonCoordinates": outline.polygon_coordinates(),
				}
			]
		}

		if outline.has_arcs:
			params["polygonArcs"] = outline.polygon_arcs
		if outline.hole_count:
			params["holes"] = outline.holes
		if story is not None:
			params["floorIndex"] = story
		if skirtLevel is not None:
			params["skirtLevel"] = skirtLevel
		if level is not None:
			params["level"] = level
		if sublines is not None:
			...

		return self._run(name_, params)

	# endregion
	# region 	Favorites Commands
	def GetFavoritesByType(self, elementType: ElType | str) -> List[str]:
		"""Returns a list of the names of all favorites of the given element type.

		Args:
			elementType (*`ElType`|`str`): The element type of the requested favorites.
		"""
		name_ = inspect.currentframe().f_code.co_name
		if isinstance(elementType, ElType):
			et = elementType.value
		else:
			et = elementType
		params = {"elementType": et}
		return self._run(name_, params)["favorites"]

	def ApplyFavoritesToElementDefaults(self, favoriteNames: str) -> dict:
		"""Apply the given favorites to their respective element tool defaults."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"favorites": [favoriteNames]}
		return self._run(name_, params)

	def CreateFavoritesFromElements(
		self,
		elements: "ElementCollection" | List[Dict[str, str]],
		favoriteNames: List[str],
	) -> dict:
		"""Create favorites from the given elements."""
		name_ = inspect.currentframe().f_code.co_name
		elements = _ensure_elem_list(elements)
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
	def GetAllProperties(self) -> dict:
		"""Returns all user defined and built-in properties."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def GetPropertyValuesOfElements(
		self,
		elements: "ElementCollection" | List[Dict[str, str]],
		propertyGUIDs: List[str],
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
			"elements": _ensure_elem_list(elements),
			"properties": [{"propertyId": {"guid": pg}} for pg in propertyGUIDs],
		}
		return self._run(name_, params)

	def SetPropertyValuesOfElements(
		self,
		elements: "ElementCollection" | List[Dict[str, str]],
		propertyGUID: str,
		value: str,
	) -> Dict[str, Any]:
		"""
		Sets the property values of elements. It works for subelements of hierarchal elements also.
		"""
		name_ = inspect.currentframe().f_code.co_name
		elements = _ensure_elem_list(elements)
		params = {
			"elementPropertyValues": [
				{
					"elementId": el,
					"propertyId": {"guid": propertyGUID},
					"propertyValue": {"value": value},
				}
				for el in elements
			]
		}
		return self._run(name_, params)

	def GetPropertyValuesOfAttributes(
		self,
		attributeGUIDs: List[str],
		propertyGUIDs: List[str],
	) -> Dict[str, Any]:
		"""
		Returns the property values of the attributes for the given property.
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"attributeIds": [{"attributeId": {"guid": ag}} for ag in attributeGUIDs],
			"properties": [{"propertyId": {"guid": pg}} for pg in propertyGUIDs],
		}
		return self._run(name_, params)

	def SetPropertyValuesOfAttributes(
		self, attributeGUIDs: List[str], propertyGUID: str, propertyValue: str
	) -> Dict[str, Any]:
		"""
		Sets the property values of attributes.
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"attributePropertyValues": [
				{
					"attributeId": {"guid": ag},
					"propertyId": {"guid": propertyGUID},
					"propertyValue": {"value": propertyValue},
				}
				for ag in attributeGUIDs
			],
		}
		return self._run(name_, params)

	def CreatePropertyGroups(
		self, property_groups: List[str | tuple | Dict[str, str]]
	) -> Dict[str, Any]:
		"""
		Creates new Property Groups.

		Args:
			property_groups (`List[str | tuple | Dict[str, str]]`): Property groups to create.
				Supports mixed input formats:
				- Strings (name only): `"Group1"`
				- Tuples (name, description): `("Group1", "My description")`
				- Dicts with name and optional description: `{"name": "Group1", "description": "My description"}`

				Example: `["Materials", ("Structural", "Load-bearing elements"), {"name": "MEP"}]`
		"""
		name_ = inspect.currentframe().f_code.co_name

		# Normalize input to list of dicts
		normalized_groups = []
		for group in property_groups:
			if isinstance(group, str):
				# Just a name provided
				normalized_groups.append(
					{"propertyGroup": {"name": group, "description": ""}}
				)
			elif isinstance(group, tuple):
				# Tuple provided: (name, description)
				if len(group) < 1 or len(group) > 2:
					raise ValueError(
						"Tuple must have 1 or 2 elements: (name) or (name, description)"
					)
				name = group[0]
				description = group[1] if len(group) == 2 else ""
				normalized_groups.append(
					{"propertyGroup": {"name": name, "description": description}}
				)
			elif isinstance(group, dict):
				# Dict provided, ensure required name field
				if "name" not in group:
					raise ValueError("Property group dict must contain 'name' field")
				normalized_groups.append(
					{
						"propertyGroup": {
							"name": group["name"],
							"description": group.get("description", ""),
						}
					}
				)
			else:
				raise TypeError("Property groups must be strings, tuples, or dicts")

		params = {"propertyGroups": normalized_groups}
		print(params)
		return self._run(name_, params)

	def DeletePropertyGroups(self, propertyGUIDs: List[str]) -> Dict[str, Any]:
		"""
		Deletes the given Custom Property Groups.
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"propertyGroupIds": [
				{"propertyGroupId": {"guid": pg}} for pg in propertyGUIDs
			],
		}
		return self._run(name_, params)

	def CreatePropertyDefinitions(
		self,
		name: str,
		*,
		description: str = "",
		group: str,
		type: Literal[
			"number",
			"integer",
			"string",
			"boolean",
			"length",
			"area",
			"volume",
			"angle",
			"numberList",
			"integerList",
			"stringList",
			"booleanList",
			"lengthList",
			"areaList",
			"volumeList",
			"angleList",
			"singleEnum",
			"multiEnum",
		],
		isEditable: bool = True,
		defaultValue: Any | list[Any] | Literal["userUndefined", "notAvailable"],
		possibleEnumValues: list[Any] | None = None,
		expression: str | list[str] = None,
		availability: str = None,
	) -> Dict[str, Any]:
		"""
		Creates Custom Property Definitions based on the given parameters.

		Args:
			name (`str`): The name given to the new property.
			description (`str`, optional): A textual description for the property.
			possibleEnumValues: The possible enum values of the property when the property type is enumeration.
			availability: The identifiers of classification items the new property is available for.
			group: The property group defined by either its name or GUID.
		"""
		name_ = inspect.currentframe().f_code.co_name

		if defaultValue and expression:
			raise ValueError(
				"You can not define both a default value and an expression."
			)

		_propDef = {
			"propertyDefinition": {
				"name": name,
				"description": description,
				"type": type,
				"isEditable": isEditable,
			}
		}

		if availability is not None:
			_propDef["propertyDefinition"]["availability"] = [
				{"classificationItemId": {"guid": guid}} for guid in availability
			]

		# Group name
		if _is_guid(group):
			_propDef["group"] = {"propertyGroupId": {"guid": group}}
		else:
			_propDef["group"] = {"name": group}

		# Define enums
		# NOTE:
		# What does "nonlocalized" values mean in this context?...
		if type == "singleEnum" or type == "multiEnum":
			_propDef["possibleEnumValues"] = {
				[
					{
						"enumValue": {
							"enumValueId": {"type": "displayValue"},
							"displayValue": enumv,
							# "nonLocalizedValue": ...,
						}
					}
					for enumv in possibleEnumValues
				]
			}

		# Use either expression or the default value
		if expression:
			_propDef["defaultValue"] = {"expressions": [expr for expr in expression]}
		else:  # not an expression
			if defaultValue == "userUndefined" or defaultValue == "notAvailable":
				# it's not clear to me what "notAvailable" even means
				_propDef["defaultValue"] = {
					"basicDefaultValue": {
						"type": type,
						"status": defaultValue,
					}
				}
			else:
				if (
					type == "numberlist"
					or type == "integerList"
					or type == "stringList"
					or type == "booleanList"
					or type == "lengthList"
					or type == "areaList"
					or type == "volumeList"
					or type == "angleList"
				):
					if not (isinstance(defaultValue, list)):
						raise ValueError(
							f"For {type=} the provided 'defaultValue' needs to be a list, not '{type(type)}'."
						)

				if type == "singleEnum":
					_defv = {
						"type": "displayValue",
						"displayValue": defaultValue,
						# I have no clue what "nonlocalized values" are...
						# "nonLocalizedValue": defaultValue,
					}
				elif type == "multiEnum":
					_defv = [
						{
							"enumValueId": {
								"type": "displayValue",  # "nonLocalizedValue"
								"displayValue": dv,
								# it's either/or
								# "nonLocalizedValue": defaultValue,
							}
						}
						for dv in defaultValue
					]
				else:
					_defv = defaultValue

				_propDef["defaultValue"] = {
					"basicDefaultValue": {
						"type": type,
						"status": "normal",
						"value": _defv,
					}
				}

		params = {"propertyDefinitions": [_propDef]}
		print(params)
		return self._run(name_, params)

	def DeletePropertyDefinitions(
		self, elements: List[Dict[str, str]], propertyGUIDs: List[str]
	) -> Dict[str, Any]:
		"""
		Deletes the given Custom Property Definitions.
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"propertyIds": [{"propertyId": {"guid": pg}} for pg in propertyGUIDs],
		}
		return self._run(name_, params)

	# endregion
	# region 	Attribute Commands
	def GetAttributesByType(self, attributeType: str | AttrType) -> Dict[str, Any]:
		"""Returns the details of every attribute of the given type."""
		name_ = inspect.currentframe().f_code.co_name
		if isinstance(attributeType, AttrType):
			attributeType = attributeType.value
		params = {"attributeType": attributeType}
		return self._run(name_, params)

	def CreateLayers(
		self, layerData: list, overwriteExisting: bool = False
	) -> Dict[str, Any]:
		"""Creates Layers based on the given parameters."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"layerDataArray": layerData, "overwriteExisting": overwriteExisting}
		return self._run(name_, params)

	def CreateBuildingMaterials(
		self, bmatData: list, overwriteExisting: bool = False
	) -> Dict[str, Any]:
		"""Creates Building Materials based on the given parameters."""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"buildingMaterialDataArray": bmatData,
			"overwriteExisting": overwriteExisting,
		}
		return self._run(name_, params)

	def CreateComposites(
		self, compositeData: list, overwriteExisting: bool = False
	) -> Dict[str, Any]:
		"""Creates Composite based on the given parameters."""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"compositeDataArray": compositeData,
			"overwriteExisting": overwriteExisting,
		}
		return self._run(name_, params)

	def CreateSurfaces(
		self,
		name: str,
		overwriteExisting: bool,
		materialType: Literal[
			"General",
			"Simple",
			"Matte",
			"Metal",
			"Plastic",
			"Glass",
			"Glowing",
			"Constant",
		],
		ambientReflection: float,
		diffuseReflection: float,
		specularReflection: float,
		transparency: float,
		shine: float,
		transparencyAttenuation: float,
		emissionAttenuation: float,
		surfaceColor: Color,
		specularColor: Color,
		emissionColor: Color,
		fillId: str,  # guid of attribute
		textureName: str,
		rotAngle: float = 0.0,
		xSize: float = 1.0,
		ySize: float = 1.0,
		fillRectangle: bool = True,
		fitPicture: bool = True,
		mirrorX: bool = False,
		mirrorY: bool = False,
		useAlphaChannel: bool = False,
		alphaAffectsTransparency: bool = False,
		alphaAffectsSurfaceColor: bool = False,
		alphaAffectsAmbientColor: bool = False,
		alphaAffectsSpecularColor: bool = False,
		alphaAffectsDiffuseColor: bool = False,
	) -> dict:
		"""Creates Surface attributes based on the given parameters."""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"surfaceDataArray": [
				{
					"name": name,
					"materialType": materialType,
					"ambientReflection": ambientReflection,
					"diffuseReflection": diffuseReflection,
					"specularReflection": specularReflection,
					"transparency": transparency,
					"shine": shine,
					"transparencyAttenuation": transparencyAttenuation,
					"emissionAttenuation": emissionAttenuation,
					"surfaceColor": {
						"red": surfaceColor.rgb_float[0],
						"green": surfaceColor.rgb_float[1],
						"blue": surfaceColor.rgb_float[2],
					},
					"specularColor": {
						"red": specularColor.rgb_float[0],
						"green": specularColor.rgb_float[1],
						"blue": specularColor.rgb_float[2],
					},
					"emissionColor": {
						"red": emissionColor.rgb_float[0],
						"green": emissionColor.rgb_float[1],
						"blue": emissionColor.rgb_float[2],
					},
					"texture": {
						"name": textureName,
						"rotationAngle": rotAngle,
						"xSize": xSize,
						"ySize": ySize,
						"FillRectangle": fillRectangle,
						"FitPicture": fitPicture,
						"mirrorX": mirrorX,
						"mirrorY": mirrorY,
						"useAlphaChannel": useAlphaChannel,
						"alphaChannelChangesTransparency": alphaAffectsTransparency,
						"alphaChannelChangesSurfaceColor": alphaAffectsSurfaceColor,
						"alphaChannelChangesAmbientColor": alphaAffectsAmbientColor,
						"alphaChannelChangesSpecularColor": alphaAffectsSpecularColor,
						"alphaChannelChangesDiffuseColor": alphaAffectsDiffuseColor,
					},
				}
			],
			"overwriteExisting": overwriteExisting,
		}
		if _is_guid(fillId):
			params["surfaceDataArray"]["fillId"] = {"attributeId": {"guid": fillId}}
		else:
			_fillguid = self._find_guid_of_attr(
				AttrType.FILL,
				fillId,
			)
			params["surfaceDataArray"]["fillId"] = {"attributeId": {"guid": _fillguid}}
		return self._run(name_, params)

	def GetBuildingMaterialPhysicalProperties(
		self, attributeIds: list
	) -> Dict[str, Any]:
		"""Retrieves the physical properties of the given Building Materials."""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"attributeIds": attributeIds,
		}
		return self._run(name_, params)

	# endregion
	# region 	Library Commands
	def GetLibraries(self) -> Dict[str, Any]:
		"""Gets the list of loaded libraries."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def ReloadLibraries(self) -> Dict[str, Any]:
		"""Executes the reload libraries command."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def AddFilesToEmbeddedLibrary(self, inputPath: Path, libPath: str = "") -> dict:
		"""Adds the given files into the embedded library.

		Args:
			inputPath (*`str`): The path to the input file.
			libPath(`str`): The relative path to the new file inside embedded library.
		"""
		# TODO: make with lists
		name_ = inspect.currentframe().f_code.co_name

		# is the file available?
		_in = _validate_path(inputPath, io_op="r")

		# if the libPath is empty we just put in the name of the file
		if not libPath:
			libPath = Path(_in).name
		# if the outputPath is just a folder append the file name
		if libPath[-1] == "/":
			libPath = libPath + Path(_in).name
		params = {
			"files": [{"inputPath": _in, "outputPath": libPath}],
		}
		return self._run(name_, params)

	# endregion
	# region 	Teamwork Commands
	def _twTest(self, command: str) -> bool:
		"""Internal function that will warn if a file is not a TW file."""
		if not self.getProjectInfo()["isTeamwork"]:
			_printcol(f"Not a Teamwork file! Command »{command}« will not be sent.")
			return False
		return True

	def TeamworkSend(self) -> Dict[str, Any]:
		"""Performs a send operation on the currently opened Teamwork project."""
		name_ = inspect.currentframe().f_code.co_name
		if self._twTest(name_):
			return self._run(name_)
		return None

	def TeamworkReceive(self) -> Dict[str, Any]:
		"""Performs a receive operation on the currently opened Teamwork project."""
		name_ = inspect.currentframe().f_code.co_name
		if self._twTest(name_):
			return self._run(name_)
		return None

	def ReserveElements(
		self, elements: "ElementCollection" | List[Dict[str, str]]
	) -> Dict[str, Any]:
		"""Performs a receive operation on the currently opened Teamwork project."""
		params = {"elements": _ensure_elem_list(elements)}
		name_ = inspect.currentframe().f_code.co_name
		if self._twTest(name_):
			return self._run(name_, params)
		return None

	def ReleaseElements(
		self, elements: "ElementCollection" | List[Dict[str, str]]
	) -> Dict[str, Any]:
		"""Releases elements in Teamwork mode."""
		params = {"elements": _ensure_elem_list(elements)}
		name_ = inspect.currentframe().f_code.co_name
		if self._twTest(name_):
			return self._run(name_, params)
		return None

	# endregion
	# region 	Navigator Commands
	def PublishPublisherSet(
		self, publisherSetName: str, outputPath: str | Path = None
	) -> Dict[str, Any]:
		"""Performs a publish operation on the currently opened project. Only the given publisher set will be published.

		Args:
			publisherSetName (* `str`): The name of the publisher set.
			outputPath (`str | Path`): Full local or LAN path for publishing. Optional, by
				default the path set in the settings of the publisher set will be used.
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {"publisherSetName": publisherSetName}
		if outputPath is not None:
			params["outputPath"] = _validate_path(outputPath)
		return self._run(name_, params)

	def UpdateDrawings(
		self, elements: "ElementCollection" | List[Dict[str, str]]
	) -> Dict[str, Any]:
		"""Performs a drawing update on the given elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": _ensure_elem_list(elements)}
		return self._run(name_, params)

	def GetDatabaseIdFromNavigatorItemId(
		self, navigatorItemIds: List[Dict[str, str]]
	) -> Dict[str, str]:
		"""Gets the ID of the database associated with the supplied Navigator item ID."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"navigatorItemIds": navigatorItemIds}
		return self._run(name_, params)

	def GetModelViewOptions(self) -> Dict[str, str]:
		"""Gets all model view options."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def GetViewSettings(self, navigatorItems: str | list[str]) -> dict:
		"""Sets the view settings of navigator items."""
		name_ = inspect.currentframe().f_code.co_name
		if isinstance(navigatorItems, str):
			navigatorItems = [navigatorItems]
		params = {
			"navigatorItemIds": [
				{"navigatorItemId": {"guid": navitem}} for navitem in navigatorItems
			]
		}
		return self._run(name_, params)

	def GetView2DTransformations(
		self, databases: List[Dict[str, str]]
	) -> Dict[str, str]:
		"""Get zoom and rotation of 2D views."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"databases": databases}
		return self._run(name_, params)

	# endregion
	# region 	Issue Management Commands
	def CreateIssue(self, name: str, parentIssueId: str, tagText: str = None) -> dict:
		"""Creates a new issue.

		Args:
			name (`str`): The name of the issue.
			parentIssueId (`str`): The identifier of an issue.
			tagText (`str`): Tag text of the issue, optional.
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {"name": name, "parentIssueId": parentIssueId, "tagText": tagText}
		return self._run(name_, params)

	def DeleteIssue(self, issueId: str, acceptAllElements: bool = False) -> dict:
		"""Deletes the specified issue.

		Args:
			acceptAllElements (`bool`): Accept all creation/deletion/modification of the deleted issue. By default false.
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {"issueId": {"guid": issueId}, "acceptAllElements": acceptAllElements}
		return self._run(name_, params)

	def GetIssues(self) -> Dict[str, Any]:
		"""Retrieves information about existing issues."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def AddCommentToIssue(
		self, issueId, text: str, author: str = "", status: str = "Unknown"
	) -> Dict[str, Any]:
		"""Adds a new comment to the specified issue."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"issueId": issueId, "author": author, "status": status, "text": text}
		return self._run(name_, params)

	def GetCommentsFromIssue(self, issueId) -> Dict[str, Any]:
		"""Adds a new comment to the specified issue."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"issueId": issueId}
		return self._run(name_, params)

	def AttachElementsToIssue(self, issueId, elements) -> Dict[str, Any]:
		"""Adds a new comment to the specified issue."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"issueId": issueId}
		return self._run(name_, params)

	def DetachElementsFromIssue(
		self, issueId, elements: "ElementCollection" | List[Dict[str, str]]
	) -> Dict[str, Any]:
		"""Detaches elements from the specified issue."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"issueId": issueId, "elements": _ensure_elem_list(elements)}
		return self._run(name_, params)

	def GetElementsAttachedToIssue(
		self, issueId: str, elements: "ElementCollection" | List[Dict[str, str]]
	) -> Dict[str, Any]:
		"""Retrieves attached elements of the specified issue, filtered by attachment type."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"issueId": {"guid": issueId}, "elements": _ensure_elem_list(elements)}
		return self._run(name_, params)

	def ExportIssuesToBCF(
		self,
		issues: List[Dict],
		exportPath: str | Path,
		useExternalId: bool,
		alignBySurveyPoint: bool = False,
	) -> Dict[str, Any]:
		"""Exports specified issues to a BCF file.

		Args:
			issues (*`List[Dict]`): A list of Issues.
			exportPath (*`str | Path`): The path to the BCF file, including it's name.
			useExternalId (*`bool`): Use external IFC ID or Archicad IFC ID as referenced in BCF topics.
			alignBySurveyPoint (*`bool`): Align BCF views by Archicad Survey Point instead of the Archicad Project Origin.

		Raises:
			ValueError: If exportPath is invalid or doesn't end with .bcf
			FileNotFoundError: If parent directory doesn't exist
			PermissionError: If no write permission for directory or file
		"""
		name_ = inspect.currentframe().f_code.co_name

		# Validate and normalize the export path
		validated_path = _validate_path(exportPath, "bcf", "w")

		params = {
			"issues": issues,
			"exportPath": validated_path,
			"useExternalId": useExternalId,
			"alignBySurveyPoint": alignBySurveyPoint,
		}
		return self._run(name_, params)

	def ImportIssuesFromBCF(
		self,
		importPath: str | Path,
		alignBySurveyPoint: bool = False,
	) -> Dict[str, Any]:
		"""Imports issues from the specified BCF file.

		Args:
			importPath (*`str | Path`): The path to the BCF file, including it's name.
			alignBySurveyPoint (*`bool`): Align BCF views by Archicad Survey Point instead of the Archicad Project Origin.

		Raises:
			ValueError: If exportPath is invalid or doesn't end with .bcf
			FileNotFoundError: If parent directory doesn't exist
		"""
		name_ = inspect.currentframe().f_code.co_name

		# Validate and normalize
		validated_path = _validate_path(importPath, "bcf")

		params = {
			"importPath": validated_path,
			"alignBySurveyPoint": alignBySurveyPoint,
		}
		return self._run(name_, params)

	# endregion
	# region 	Revision Management Commands
	def GetRevisionIssues(self) -> Dict[str, Any]:
		"""Retrieves all issues."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def GetRevisionChanges(self) -> Dict[str, Any]:
		"""Retrieves all changes."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def GetDocumentRevisions(self) -> Dict[str, Any]:
		"""Retrieves all document revisions."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def GetCurrentRevisionChangesOfLayouts(
		self, layoutDatabaseIds: List[Dict]
	) -> Dict[str, Any]:
		"""Retrieves all document revisions."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"layoutDatabaseIds": layoutDatabaseIds}
		return self._run(name_, params)

	def GetRevisionChangesOfElements(
		self, elements: "ElementCollection" | List[Dict[str, str]]
	) -> Dict[str, Any]:
		"""Retrieves the changes belong to the given elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": _ensure_elem_list(elements)}
		return self._run(name_, params)

	# endregion


# Export a singleton
tapir = TapirCommands()
