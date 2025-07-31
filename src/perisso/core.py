from archicad import ACConnection
from archicad.releases import Commands, Types, Utilities
from .collection import ElementCollection
from .utils import run_tapir_command

# Connection setup
conn = ACConnection.connect()
if not conn:
	raise Exception("No Archicad instance running!")

acc: Commands = conn.commands
acu: Utilities = conn.utilities
act: Types = conn.types


def perisso(*, selection=False):
	"""Get all elements as an ElementCollection instance.

	Arguments:
		<None>: If no arguments are given ...
		elements: The name of this object.
		selection: If `True`, only the currently selected elements will be added to the ElementCollection.
	"""
	if selection:
		elements_data = run_tapir_command("GetSelectedElements")
		if len(elements_data["elements"]) == 0:
			elements_data = run_tapir_command("GetAllElements")
	else:
		elements_data = run_tapir_command("GetAllElements")
	return ElementCollection(elements_data["elements"])
