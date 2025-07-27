from time import sleep
from perisso import perisso, clearhighlight, Filter, ElType

# initialize an ElementCollection
elements = perisso()

# string representation
print(elements)

# get the number of elements in the set
print(len(elements))

# check with its GUID if an element is the ElementCollection
print("216E9CE2-8007-334A-9D8C-FB0EC7EC083C" in elements)

# get only beams
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

# perisso supports slicing, too
print(col_elements[0])

# intuitively add sets to each other
beams = elements.filterBy(Filter.ELEMENT_TYPE).equals(ElType.BEAM)
columns = elements.filterBy(Filter.ELEMENT_TYPE).equals(ElType.COLUMN)
structural = beams + columns
print(structural)

# additional functionalities:
perisso().filterBy(Filter.PROPERTY).property("Prop Group Name", "Prop Name").equals("test").highlight()
sleep(5)
clearhighlight()
