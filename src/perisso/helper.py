from .enums import AttrType


# `zip()` stops at the shortest list,
# `itertool` needs either a "fillvalue" to be set, or it cycles.
# Instead we want to repeat the last item in the smaller lists:
def zip_repeat_last(*lists):
	max_len = max(map(len, lists))
	for i in range(max_len):
		yield tuple(lst[i] if i < len(lst) else lst[-1] for lst in lists)


def _printcol(text: str):
	text = "\033[91m" + text + "\033[0m"
	print(text)


def fetch_attribute_guid(attribute_type: AttrType, name: str) -> str:
	"""Fetches the GUID of an Attribute by name using the Tapir interface.

	Args:
		attribute_type: The attribute type (AttrType enum or string).
		name: The name of the attribute to find.

	Returns:
		str: The GUID of the attribute.

	Raises:
		ValueError: If the attribute does not exist.
	"""
	from .tapir_commands import tapir

	attr_response = tapir.GetAttributesByType(attribute_type)
	attributes = attr_response.get("attributes", [])

	# Search by name
	for attr in attributes:
		if attr["name"] == name:
			return attr["attributeId"]["guid"]

	# If not found, raise an error
	attr_type_str = (
		attribute_type.value if isinstance(attribute_type, AttrType) else attribute_type
	)
	raise ValueError(f"Attribute '{name}' not found in {attr_type_str} attributes")
