import json
from typing import Dict, List, TYPE_CHECKING
from .connection import acc, acu, act
from .enums import Filter, ElType
from .types import Coordinate, Arc
from .tapir_commands import tapir, _ensure_elem_list

# Only import for type checking, not at runtime
if TYPE_CHECKING:
	from .collection import ElementCollection


def run_tapir_command(command: str, *args):
	"""Invoke a Tapir Command \n
	Uses the official `archicad` package to run it.

	Deprecated: Use the typed `tapir` object instead for better IDE support.

	Args:
		command (`str`): The name of the tapir command to be run.
		*args (`dict`): Usually a dict with the additional parameters.
			Could look like this: `{"elements": perisso().get()}` or just `{"elements": perisso()}`
	"""
	if args:
		return acc.ExecuteAddOnCommand(
			act.AddOnCommandId("TapirCommand", command), *args
		)
	else:
		return acc.ExecuteAddOnCommand(act.AddOnCommandId("TapirCommand", command))


def _pprint(d):
	"""Pretty Print a `<dict>` response."""
	print(json.dumps(d, indent=3))
	return


def _toNative(elements):
	"""Return a native (original Archicad-Python connection) element list with their appropiate types.

	Args:
		elements: List of elements or ElementCollection instance
	"""
	elements = _ensure_elem_list(elements)
	return [
		act.ElementIdArrayItem(act.ElementId(item["elementId"]["guid"]))
		for item in elements
	]


def getPropValues(
	*,
	builtin: str = None,
	propGUID: str = None,
	elements: "ElementCollection" | List[Dict[str, str]],
) -> list:
	"""Get Properties with the original Archicad-Python connection.

	Args:
		builtin: Built-in property name
		propGUID: Property GUID
		elements: List of elements or ElementCollection instance
	"""
	elements = _ensure_elem_list(elements)

	if builtin and (propGUID is None):
		# ... except for built-ins
		return _getPropValues(builtin=builtin, elements=elements)

	pidai = act.PropertyIdArrayItem(act.PropertyId(propGUID))
	json_ = acc.GetPropertyValuesOfElements(_toNative(elements), [pidai])

	ret_values = []
	# normalize:
	for item in json_:  # item is "PropertyValuesWrapper"
		# so far I've not come across errors
		ret_values.append(
			{"ok": True, "value": item.propertyValues[0].propertyValue.value}
		)
	return ret_values


def _getPropValues(
	*,
	builtin: str = None,
	propGUID: str = None,
	elements: "ElementCollection" | List[Dict[str, str]],
) -> list:
	"""Get Properties with Tapir. This is now only used for builtin properties. \n
	It has the severe backdraw that there are no type hints and all values are stringified.
	See also: https://github.com/ENZYME-APD/tapir-archicad-automation/issues/285

	Args:
		builtin: Built-in property name
		propGUID: Property GUID
		elements: List of elements or ElementCollection instance
	"""
	elements = _ensure_elem_list(elements)

	if builtin and (propGUID is None):
		propGUID = str(acu.GetBuiltInPropertyId(builtin).guid)
	json_ = tapir.GetPropertyValuesOfElements(elements, [propGUID])[
		"propertyValuesForElements"
	]
	ret_values = []
	# normalize:
	for i in json_:
		if "error" in i["propertyValues"][0]:
			ret_values.append(
				{"ok": False, "error": i["propertyValues"][0]["error"]["message"]}
			)
		else:
			ret_values.append(
				{"ok": True, "value": i["propertyValues"][0]["propertyValue"]["value"]}
			)
	return ret_values


def getDetails(
	filter: Filter, elements: "ElementCollection" | List[Dict[str, str]]
) -> list:
	"""Get element details.

	Args:
		filter: Filter type to apply
		elements: List of elements or ElementCollection instance
	"""
	elements = _ensure_elem_list(elements)
	json_ = tapir.GetDetailsOfElements(elements)["detailsOfElements"]
	ret_values = []
	if filter == Filter.ELEMENT_TYPE:
		# ElementType can never be error
		ret_values = [{"ok": True, "value": i["type"]} for i in json_]
	else:
		raise NotImplementedError
	return ret_values


def getGeometry(
	filter: Filter, elements: "ElementCollection" | List[Dict[str, str]]
) -> list:
	"""Get geometric properties of elements.

	Args:
		filter: Filter type to apply (HEIGHT, LENGTH)
		elements: List of elements or ElementCollection instance
	"""
	elements = _ensure_elem_list(elements)
	ret_values = []
	details = tapir.GetDetailsOfElements(elements)["detailsOfElements"]
	if filter == Filter.HEIGHT:
		for i, item in enumerate(elements):
			if details[i]["type"] == ElType.MORPH.value:
				ret_values.append({"ok": True, "value": getBBoxSize([item])[0]["z"]})
			elif details[i]["type"] == ElType.SLAB.value:
				ret_values.append(
					{"ok": True, "value": details[i]["details"]["thickness"]}
				)
			else:
				ret_values.append({"ok": False, "error": "not implemented"})
	elif filter == Filter.LENGTH:
		for i, item in enumerate(elements):
			if details[i]["type"] == ElType.POLYLINE.value:
				coordinates = details[i]["details"]["coordinates"]
				arcs = details[i]["details"].get("arcs", None)
				try:
					length = _calculate_polyline_length(coordinates, arcs)
					ret_values.append({"ok": True, "value": length})
				except Exception as e:
					ret_values.append(
						{"ok": False, "error": f"calculation error: {str(e)}"}
					)
			else:
				ret_values.append({"ok": False, "error": "not implemented"})
	else:
		raise NotImplementedError
	return ret_values


def getBBoxSize(elements: "ElementCollection" | List[Dict[str, str]]) -> list:
	"""Gets the size of the fitted Bounding Box of the elements.

	Args:
		elements: List of elements or ElementCollection instance
	"""
	elements = _ensure_elem_list(elements)
	ret_values = []
	bboxes_raw = tapir.Get3DBoundingBoxes(elements)
	for i, item in enumerate(bboxes_raw["boundingBoxes3D"]):
		dimensions = {
			"x": item["boundingBox3D"]["xMax"] - item["boundingBox3D"]["xMin"],
			"y": item["boundingBox3D"]["yMax"] - item["boundingBox3D"]["yMin"],
			"z": item["boundingBox3D"]["zMax"] - item["boundingBox3D"]["zMin"],
		}
		ret_values.append(dimensions)
	return ret_values


def _calculate_polyline_length(coordinates: list, arcs: list = None) -> float:
	"""Calculate the total length of a polyline with optional arc segments.

	Args:
		coordinates: List of coordinate dictionaries
		arcs: Optional list of arc definitions

	Returns:
		Total length of the polyline
	"""
	if len(coordinates) < 2:
		return 0.0

	# Convert coordinate dictionaries to Coordinate objects
	coord_objects = [Coordinate.from_dict(coord) for coord in coordinates]

	total_length = 0.0
	arc_lookup = {}

	# Create a lookup for arc segments if they exist
	if arcs:
		for arc in arcs:
			# Store arc info by the segment indices
			arc_lookup[(arc["begIndex"], arc["endIndex"])] = arc["arcAngle"]

	# Calculate length for each segment
	for i in range(len(coord_objects) - 1):
		start_point = coord_objects[i]
		end_point = coord_objects[i + 1]

		# Check if this segment is an arc
		if (i, i + 1) in arc_lookup:
			# This is an arc segment
			arc_angle = arc_lookup[(i, i + 1)]
			arc = Arc(start_point, end_point, arc_angle)
			segment_length = arc.length
		else:
			# This is a straight segment
			segment_length = start_point.distance_to(end_point)

		total_length += segment_length

	return total_length
