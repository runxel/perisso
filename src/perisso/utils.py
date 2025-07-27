import json
from archicad import ACConnection
from archicad.releases import Commands, Types, Utilities
from .enums import Filter

# Connection setup
conn = ACConnection.connect()
if not conn:
	raise Exception("No Archicad instance running!")

acc: Commands = conn.commands
acu: Utilities = conn.utilities
act: Types = conn.types


def rtc(command: str, *args):
	"""Run a Tapir Command \n
	Uses the official `archicad` package.
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


def getPropValues(*, builtin: str = None, propGUID: str = None, elements: dict) -> list:
	"""Get Properties"""
	if builtin and propGUID is None:
		propGUID = str(acu.GetBuiltInPropertyId(builtin).guid)
	_param = {
		"elements": elements,
		"properties": [{"propertyId": {"guid": propGUID}}],
	}
	_pprint(_param)
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


def getDetails(type_: Filter, elements: dict) -> list:
	json_ = rtc("GetDetailsOfElements", {"elements": elements})["detailsOfElements"]
	ret_values = []
	if type_ == Filter.ELEMENT_TYPE:
		# ElementType can never be error
		ret_values = [{"ok": True, "value": i["type"]} for i in json_]
	return ret_values


# result = read_field(json_data)

# if result["ok"]:
# 	print(result["value"])
# else:
# 	print("Error:", result["error"])
