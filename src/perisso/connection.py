from archicad import ACConnection
from archicad.releases import Commands, Types, Utilities

# Connection setup
conn = ACConnection.connect()
if not conn:
	raise Exception("No Archicad instance running!")

acc: Commands = conn.commands
acu: Utilities = conn.utilities
act: Types = conn.types
