from time import sleep
from perisso import perisso, tapir, Filter, ElType, Vector, Coordinate

# initialize an ElementCollection
elements = perisso()

# string representation
print(elements)

# get the number of elements in the set
print(len(elements))

# check with its GUID if an element is the ElementCollection
print("216E9CE2-8007-334A-9D8C-FB0EC7EC083C" in elements)

# use some GUIDs to handbuild a perisso ElementCollection
manufactured = perisso().from_dict(
	{
		"elements": [
			{"elementId": {"guid": "F6C4C267-0E38-DA48-9D66-D576DC855B3B"}},
			{"elementId": {"guid": "1306C37A-7C0E-E549-97C6-3F4A60BD819E"}},
		]
	}
)

# get only a certain element type
beams_only = elements.filterBy(Filter.ELEMENT_TYPE).equals("Beam").get()
print(beams_only)

# you can also chain multiple filters
col_elements = (
	elements.filterBy(Filter.ELEMENT_TYPE)
	.equals(ElType.COLUMN)
	.filterBy(Filter.ID)
	.contains("123")
	.get()
)
print(col_elements)

wanted = (
	elements.filterBy(Filter.PROPERTY)
	.property("Prop Group Name", "Prop Name")
	.between(1.0, 2.5)
)
print(wanted)

# perisso supports slicing, too
print(col_elements[0])

# create ElementCollection from output:
created = tapir.CreateSlabs(...)
new_slabs = perisso().from_dict(created)
duplicated = perisso().from_dict(
	tapir.MoveElements(created.get(), Vector(5, 10), copy=True)
)

# delete Elements
tapir.DeleteElements(duplicated.get())

# intuitively add sets to each other
beams = elements.filterBy(Filter.ELEMENT_TYPE).equals(ElType.BEAM)
columns = elements.filterBy(Filter.ELEMENT_TYPE).equals(ElType.COLUMN)
structural = beams + columns + new_slabs
print(structural)

# additional functionalities:
perisso().filterBy(Filter.PROPERTY).property("Prop Group Name", "Prop Name").equals(
	"test"
).highlight()
sleep(5)
tapir.clearHighlight()
