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


def _is_guid(value: str) -> bool:
	"""Check if a string is a valid GUID format.

	Args:
		value (str): String to check

	Returns:
		bool: True if string matches GUID pattern, False otherwise
	"""
	if not isinstance(value, str):
		return False

	# GUID pattern: 8-4-4-4-12 hexadecimal digits
	guid_pattern = (
		r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
	)
	return bool(re.match(guid_pattern, value))


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
		if params:
			return self.acc.ExecuteAddOnCommand(
				self.act.AddOnCommandId("TapirCommand", command), params
			)
		else:
			return self.acc.ExecuteAddOnCommand(
				self.act.AddOnCommandId("TapirCommand", command)
			)

	# region 	Application Commands
	def GetTapirVersion(self) -> str:
		"""Retrieves the version of the installed Tapir Add-On."""
		name_ = "GetAddOnVersion"
		return self._run(name_)["version"]

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
		"""Retrieves information about the story sructure of the currently loaded project."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def SetStories(self, stories: List[Dict]) -> dict:
		"""Sets the story structure of the currently loaded project.
		This means, that the current structure will not be appended but replaced.

		Args:
			stories (`list[dict]`): A list of project stories, with these mandatory items: \n
			`dispOnSections` (`bool`): Story level lines should appear on sections and elevations.
			`level` (`float`): The story level.
			`name` (`str`): The name of the story.
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {"stories": stories}
		return self._run(name_, params)

	def GetHotlinks(self) -> dict:
		"""Gets the file system locations (path) of the hotlink modules. The hotlinks can have tree hierarchy in the project."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def OpenProject(self, path: str | Path) -> dict:
		"""Opens the given project."""
		name_ = inspect.currentframe().f_code.co_name
		path = _validate_path(path, io_op="r")
		params = {"projectFilePath": path}
		return self._run(name_, params)

	def GetGeoLocation(self) -> dict:
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

	def GetDetailsOfElements(self, elements: List[Dict[str, str]]) -> dict:
		"""Get details of given elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": elements}
		return self._run(name_, params)

	def SetDetailsOfElements(
		self, elements: List[Dict[str, str]], details: list
	) -> dict:
		"""Sets the details of the given elements (story, layer, order etc)."""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"elementsWithDetails": [
				{"elementId": el["elementId"], "details": det}
				for el, det in zip(elements, details)
			]
		}
		return self._run(name_, params)

	def Get3DBoundingBoxes(self, elements: List[Dict[str, str]]) -> Dict[str, Any]:
		"""Get 3D bounding boxes of elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": elements}
		return self._run(name_, params)

	def GetSubelementsOfHierarchicalElements(
		self, elements: List[Dict[str, str]]
	) -> dict:
		"""Gets the subelements of the given hierarchical elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": elements}
		return self._run(name_, params)

	def GetConnectedElements(
		self, elements: List[Dict[str, str]], connectedElementType: ElType
	) -> dict:
		"""Gets the subelements of the given hierarchical elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"elements": elements,
			"connectedElementType": connectedElementType.value,
		}
		return self._run(name_, params)

	def HighlightElements(
		self,
		elements: List[Dict[str, str]] = None,
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
		# A helper function – this does not exist as it's own Tapir command.
		return self.HighlightElements(elements=[None])

	def MoveElements(
		self, elements: List[Dict[str, str]], vector: Vector, copy: bool = False
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

	def DeleteElements(self, elements: List[Dict[str, str]]) -> dict:
		"""Deletes elements.
		Tapir: 1.2.1"""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": elements}
		return self._run(name_, params)

	def GetGDLParametersOfElements(self, elements: List[Dict[str, str]]) -> dict:
		"""Gets all the GDL parameters (name, type, value) of the given elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": elements}
		return self._run(name_, params)

	def SetGDLParametersOfElements(
		self, elements: List[Dict[str, str]], gdlParams: List[Dict]
	) -> dict:
		"""Sets the given GDL parameters of the given elements."""
		name_ = inspect.currentframe().f_code.co_name
		print(gdlParams)
		params = {
			"elementsWithGDLParameters": [
				{
					"elementId": el["elementId"],
					"gdlParameters": gdlParams,
				}
				for el in elements
			]
		}
		print(params)
		return self._run(name_, params)

	def GetClassificationsOfElements(
		self,
		elements: List[Dict[str, str]],
		classificationSystemIds: List[str] | List[Dict] = None,
		resolve: bool = False,
	) -> dict:
		"""Returns the classification of the given elements in the given classification systems.
		It also works for subelements of hierarchal elements.
		Use it with `acc.GetAllClassificationSystems()`.

		Args:
			elements (*`str`): Elements
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
			"elements": elements,
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
		elements: List[Dict[str, str]],
		classificationId: Dict = None,
		*,
		classificationSystemId: str = "",
		classificationItemId: str = "",
	) -> dict:
		"""Sets the classification of elements. In order to set the classification of an element to unclassified,
		omit the classificationItemId field. It works for subelements of hierarchal elements also.

		Either provide a full `classificationId` dict or the system and item ID.
		Those can be either GUIDS or real-named strings."""
		name_ = inspect.currentframe().f_code.co_name

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
	def CreateColumns(self, coors: List[Coordinate]) -> dict:
		"""Creates Column elements based on the given parameters."""
		name_ = inspect.currentframe().f_code.co_name
		params = {
			"columnsData": [{"coordinates": coor.to_3d().to_dict()} for coor in coors]
		}
		return self._run(name_, params)

	def CreateSlabs(
		self,
		coors: List[Coordinate] | Dict,
		arcs: List[Dict] = [],
		holes: List[Dict] = [],
		level: float = 0.0,
	) -> dict:
		"""Creates Slab elements based on the given parameters.

		Args:
			coors (`List[Coordinate] | Dict`): Coordinates as Coordinate object in a list, or a ready made dict.
			arcs: Looks like this: `[{"begIndex": 0, "endIndex": 1, "arcAngle": 3.14}]`"""
		name_ = inspect.currentframe().f_code.co_name
		if level is None:
			# if explicitely not providing level it should be stored in the coordinates
			level = coors[0].z
		if not isinstance(coors, dict):
			coors = [coor.to_2d().to_dict() for coor in coors]
		params = {
			"slabsData": [
				{
					"level": level,
					"polygonCoordinates": coors,
					"polygonArcs": arcs,
					"holes": holes,
				}
			]
		}
		return self._run(name_, params)

	def CreateZones(self, coors: List[Coordinate]) -> dict:
		"""Creates Zone elements based on the given parameters."""
		raise NotImplementedError
		params = {
			"columnsData": [{"coordinates": coor.to_3d().to_dict()} for coor in coors]
		}
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_, params)

	def CreatePolylines(self, coors: List[Coordinate]) -> dict:
		"""Creates Polyline elements based on the given parameters."""
		raise NotImplementedError
		params = {
			"columnsData": [{"coordinates": coor.to_3d().to_dict()} for coor in coors]
		}
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_, params)

	def CreateObjects(self, coors: List[Coordinate]) -> dict:
		"""Creates Object elements based on the given parameters."""
		raise NotImplementedError
		params = {
			"columnsData": [{"coordinates": coor.to_3d().to_dict()} for coor in coors]
		}
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_, params)

	def CreateMeshes(self, coors: List[Coordinate]) -> dict:
		"""Creates Mesh elements based on the given parameters."""
		raise NotImplementedError
		params = {
			"columnsData": [{"coordinates": coor.to_3d().to_dict()} for coor in coors]
		}
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_, params)

	# endregion
	# region 	Favorites Commands
	def ApplyFavoritesToElementDefaults(self, favoriteNames: str) -> dict:
		"""Apply the given favorites to their respective element tool defaults."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"favorites": [favoriteNames]}
		return self._run(name_, params)

	def CreateFavoritesFromElements(
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
	def GetAllProperties(self) -> dict:
		"""Returns all user defined and built-in properties."""
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_)

	def GetPropertyValuesOfElements(
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

	def SetPropertyValuesOfElements(
		self, elements: List[Dict[str, str]], propertyGUIDs: List[str]
	) -> Dict[str, Any]:
		"""
		Sets the property values of elements. It works for subelements of hierarchal elements also.
		"""
		raise NotImplementedError
		params = {
			"elements": elements,
			"properties": [{"propertyId": {"guid": pg}} for pg in propertyGUIDs],
		}
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_, params)

	def GetPropertyValuesOfAttributes(
		self, elements: List[Dict[str, str]], propertyGUIDs: List[str]
	) -> Dict[str, Any]:
		"""
		Returns the property values of the attributes for the given property.
		"""
		raise NotImplementedError
		params = {
			"elements": elements,
			"properties": [{"propertyId": {"guid": pg}} for pg in propertyGUIDs],
		}
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_, params)

	def SetPropertyValuesOfAttributes(
		self, elements: List[Dict[str, str]], propertyGUIDs: List[str]
	) -> Dict[str, Any]:
		"""
		Sets the property values of attributes.
		"""
		raise NotImplementedError
		params = {
			"elements": elements,
			"properties": [{"propertyId": {"guid": pg}} for pg in propertyGUIDs],
		}
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_, params)

	def CreatePropertyGroups(
		self, elements: List[Dict[str, str]], propertyGUIDs: List[str]
	) -> Dict[str, Any]:
		"""
		Creates Property Groups based on the given parameters.
		"""
		raise NotImplementedError
		params = {
			"elements": elements,
			"properties": [{"propertyId": {"guid": pg}} for pg in propertyGUIDs],
		}
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_, params)

	def DeletePropertyGroups(
		self, elements: List[Dict[str, str]], propertyGUIDs: List[str]
	) -> Dict[str, Any]:
		"""
		Deletes the given Custom Property Groups.
		"""
		raise NotImplementedError
		params = {
			"elements": elements,
			"properties": [{"propertyId": {"guid": pg}} for pg in propertyGUIDs],
		}
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_, params)

	def CreatePropertyDefinitions(
		self, elements: List[Dict[str, str]], propertyGUIDs: List[str]
	) -> Dict[str, Any]:
		"""
		Creates Custom Property Definitions based on the given parameters.
		"""
		raise NotImplementedError
		params = {
			"elements": elements,
			"properties": [{"propertyId": {"guid": pg}} for pg in propertyGUIDs],
		}
		name_ = inspect.currentframe().f_code.co_name
		return self._run(name_, params)

	def SeletePropertyDefinitions(
		self, elements: List[Dict[str, str]], propertyGUIDs: List[str]
	) -> Dict[str, Any]:
		"""
		Deletes the given Custom Property Definitions.
		"""
		raise NotImplementedError
		params = {
			"elements": elements,
			"properties": [{"propertyId": {"guid": pg}} for pg in propertyGUIDs],
		}
		name_ = inspect.currentframe().f_code.co_name
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

	def ReserveElements(self, elements: List[Dict[str, str]]) -> Dict[str, Any]:
		"""Performs a receive operation on the currently opened Teamwork project."""
		params = {"elements": elements}
		name_ = inspect.currentframe().f_code.co_name
		if self._twTest(name_):
			return self._run(name_, params)
		return None

	def ReleaseElements(self, elements: List[Dict[str, str]]) -> Dict[str, Any]:
		"""Releases elements in Teamwork mode."""
		params = {"elements": elements}
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
			publisherSetName (*`str`): The name of the publisher set.
			outputPath (`str | Path`): Full local or LAN path for publishing. Optional, by
				default the path set in the settings of the publisher set will be used.
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {"publisherSetName": publisherSetName}
		if outputPath is not None:
			params["outputPath"] = _validate_path(outputPath)
		return self._run(name_, params)

	def UpdateDrawings(self, elements: List[Dict[str, str]]) -> Dict[str, Any]:
		"""Performs a drawing update on the given elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": elements}
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

	# TODO:
	def GetViewSettings(self, navigatorItemIds: List[Dict[str, str]]) -> Dict[str, str]:
		"""Sets the view settings of navigator items."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"navigatorItemIdsWithViewSettings": navigatorItemIds}
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

	# TODO:
	def DeleteIssue(
		self, name: str, parentIssueId: str, acceptAllElements: bool = False
	) -> dict:
		"""Deletes the specified issue.

		Args:
			acceptAllElements (`bool`): Accept all creation/deletion/modification of the deleted issue. By default false.
		"""
		name_ = inspect.currentframe().f_code.co_name
		params = {"name": name}
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
		self, issueId, elements: List[Dict[str, str]]
	) -> Dict[str, Any]:
		"""Detaches elements from the specified issue."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"issueId": issueId, "elements": elements}
		return self._run(name_, params)

	# TODO:
	def GetElementsAttachedToIssue(
		self, issueId, elements: List[Dict[str, str]]
	) -> Dict[str, Any]:
		"""Detaches elements from the specified issue."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"issueId": issueId, "elements": elements}
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
		self, elements: List[Dict[str, str]]
	) -> Dict[str, Any]:
		"""Retrieves the changes belong to the given elements."""
		name_ = inspect.currentframe().f_code.co_name
		params = {"elements": elements}
		return self._run(name_, params)

	# endregion


# Export a singleton
tapir = TapirCommands()
