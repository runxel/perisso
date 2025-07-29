import json
from archicad import ACConnection
from archicad.releases import Commands, Types, Utilities
from .enums import Filter, ElType

# Connection setup
conn = ACConnection.connect()
if not conn:
	raise Exception("No Archicad instance running!")

acc: Commands = conn.commands
acu: Utilities = conn.utilities
act: Types = conn.types


def rtc(command: str, *args):
	"""Run a Tapir Command \n
	Uses the official `archicad` package for that.

	Args:
		command (`str`): The name of the tapir command to be run.
		*args (`dict`): Usually a dict with the additional parameters.
			Could look like this: `{"elements": perisso().get()}`
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


def _toNative(elements: list):
	"""Return a native (original Archicad-Python connection) element list with their appropiate types."""
	return [
		act.ElementIdArrayItem(act.ElementId(item["elementId"]["guid"]))
		for item in elements
	]


def getPropValues(*, builtin: str = None, propGUID: str = None, elements: dict) -> list:
	"""Get Properties with the orginal Archicad-Python connection."""
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


def _getPropValues(*, builtin: str = None, propGUID: str = None, elements: dict ) -> list:  # fmt: skip
	"""Get Properties with Tapir. This is now only used for builtin properties. \n
	It has the severe backdraw that there are no type hints and all values are stringified.
	See also: https://github.com/ENZYME-APD/tapir-archicad-automation/issues/285"""
	if builtin and (propGUID is None):
		propGUID = str(acu.GetBuiltInPropertyId(builtin).guid)
	_param = {
		"elements": elements,
		"properties": [{"propertyId": {"guid": propGUID}}],
	}
	json_ = rtc("GetPropertyValuesOfElements", _param)["propertyValuesForElements"]
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


def getDetails(filter: Filter, elements: dict) -> list:
	json_ = rtc("GetDetailsOfElements", {"elements": elements})["detailsOfElements"]
	ret_values = []
	if filter == Filter.ELEMENT_TYPE:
		# ElementType can never be error
		ret_values = [{"ok": True, "value": i["type"]} for i in json_]
	else:
		raise NotImplementedError
	return ret_values


def getGeometry(filter: Filter, elements: dict) -> list:
	ret_values = []
	elem_types = getDetails(filter=Filter.ELEMENT_TYPE, elements=elements)
	if filter == Filter.HEIGHT:
		for i, item in enumerate(elements):
			if elem_types[i]["value"] == ElType.MORPH.value:
				ret_values.append({"ok": True, "value": _getBBoxSize([item])[0]["z"]})
			else:
				ret_values.append({"ok": False, "error": "not implemented"})
	else:
		raise NotImplementedError
	return ret_values


def _getBBoxSize(elements: dict) -> list:
	"""Gets the size of the fitted Bounding Box of the elements."""
	ret_values = []
	bboxes_raw = rtc("Get3DBoundingBoxes", {"elements": elements})
	for i, item in enumerate(bboxes_raw["boundingBoxes3D"]):
		dimensions = {
			"x": item["boundingBox3D"]["xMax"] - item["boundingBox3D"]["xMin"],
			"y": item["boundingBox3D"]["yMax"] - item["boundingBox3D"]["yMin"],
			"z": item["boundingBox3D"]["zMax"] - item["boundingBox3D"]["zMin"],
		}
		ret_values.append(dimensions)
	return ret_values
