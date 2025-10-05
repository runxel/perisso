import re


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
