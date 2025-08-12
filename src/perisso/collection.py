from typing import List
from archicad import Types as act
from .tapir_commands import tapir
from .enums import ElType, Filter
from .types import Color
from .utils import getPropValues, getDetails, getGeometry, acu, _pprint  # noqa: F401 fmt: skip


class ElementCollection:
	"""Fluent interface for filtering elements with method chaining."""

	def __init__(self, elements, *, _field=None, _propGUID: str = None):
		self.elements = elements
		self._field = _field
		self._propGUID = _propGUID
		self._pattern_handlers = {
			Filter.ID: lambda elements: getPropValues(
				builtin="General_ElementID", elements=elements
			),
			Filter.PARENT_ID: lambda elements: getPropValues(
				builtin="IdAndCategories_ParentId", elements=elements
			),
			Filter.HL_ID: lambda elements: getPropValues(
				builtin="IdAndCategories_HotlinkMasterID", elements=elements
			),
			Filter.HLE_ID: lambda elements: getPropValues(
				builtin="General_HotlinkAndElementID", elements=elements
			),
			Filter.LAYER: lambda elements: getPropValues(
				builtin="ModelView_LayerName", elements=elements
			),
			Filter.GUID: lambda elements: getPropValues(
				builtin="General_UniqueID", elements=elements
			),
			Filter.ELEMENT_TYPE: lambda elements: getDetails(
				Filter.ELEMENT_TYPE, elements
			),
			Filter.PROPERTY: lambda elements: getPropValues(
				propGUID=self._propGUID, elements=elements
			),
			# geometry
			Filter.HEIGHT: lambda elements: getGeometry(Filter.HEIGHT, elements),
			Filter.LENGTH: lambda elements: getGeometry(Filter.LENGTH, elements),
		}

	@classmethod
	def from_dict(cls, data: dict):
		"""Create ElementCollection from dictionary.

		Args:
			data (`dict`): An "elements" dict.

		>>> perisso().from_dict({"elements": [{"elementId": {"guid": "F6C4C267-0E38-DA48-9D66-D576DC855B3B"}}]})
		"""
		collection = cls(data["elements"])
		return collection

	def filterBy(self, field: Filter):
		"""Set the field to filter by. Accepts a Filter enum."""
		if isinstance(field, Filter):
			self._field = field
		else:
			raise TypeError("Field must be a valid Filter enum")
		return self

	def property(self, group: str, name: str):
		"""Must follow on a `.filterBy(Filter.PROPERTY)` to specify which Property should be read.
		Please note: When filtering to a property all elements that do not have the property available are discarded.

		Args:
			group (`str`): Property group name.
			name (`str`): Property name.
		"""
		if not self._field == Filter.PROPERTY:
			raise ValueError("`filterBy()` must be set to `Filter.PROPERTY'")

		self._propGUID = str(acu.GetUserDefinedPropertyId(group, name).guid)

		# Only include elements that have a "propertyValue" key (not "error")
		_prop_values_or_error = tapir.getPropertyValuesOfElements(self.elements, [self._propGUID])["propertyValuesForElements"]  # fmt: skip
		filtered = []
		for i, prop_result in enumerate(_prop_values_or_error):
			prop_value = prop_result["propertyValues"][0]
			if "propertyValue" in prop_value:
				filtered.append(self.elements[i])

		return ElementCollection(
			filtered, _field=Filter.PROPERTY, _propGUID=self._propGUID
		)

	def and_(self, other_collection_or_callable):
		"""Combine with another ElementCollection using AND logic (intersection).

		Args:
			other_collection_or_callable: Either an ElementCollection or a callable
				that takes this collection and returns an ElementCollection

		Returns:
			ElementCollection: New collection containing only elements present in both collections
		"""
		if callable(other_collection_or_callable):
			other_collection = other_collection_or_callable(
				ElementCollection(self.elements)
			)
		elif isinstance(other_collection_or_callable, ElementCollection):
			other_collection = other_collection_or_callable
		else:
			raise TypeError(
				"Argument must be an ElementCollection or callable returning one"
			)

		# Get GUIDs from the other collection
		other_guids = {
			element["elementId"]["guid"] for element in other_collection.elements
		}

		# Keep only elements that exist in both collections
		intersection_elements = [
			element
			for element in self.elements
			if element["elementId"]["guid"] in other_guids
		]

		return ElementCollection(intersection_elements)

	# region // string comparisons
	def startsWith(self, value: str | ElType, casesensitive: bool = True):
		if not self._field:
			raise ValueError("Must call filterBy() first")

		if isinstance(value, ElType):
			# get 'value' from enum
			value = value.value

		if not casesensitive:
			value = value.casefold()

		handler = self._pattern_handlers.get(self._field)
		if handler:
			ret_values = handler(self.elements)
			filtered = [
				self.elements[i]
				for i, item in enumerate(ret_values)
				if item["ok"]  # exclude errors
				and (
					str(item["value"]).casefold()
					if not casesensitive
					else str(item["value"])
				).startswith(value)
			]

		return ElementCollection(filtered)

	def endsWith(self, value: str | ElType, casesensitive: bool = True):
		if not self._field:
			raise ValueError("Must call filterBy() first")

		if isinstance(value, ElType):
			# get 'value' from enum
			value = value.value

		if not casesensitive:
			value = value.casefold()

		handler = self._pattern_handlers.get(self._field)
		if handler:
			ret_values = handler(self.elements)
			filtered = [
				self.elements[i]
				for i, item in enumerate(ret_values)
				if item["ok"]  # exclude errors
				and (
					str(item["value"]).casefold()
					if not casesensitive
					else str(item["value"])
				).endswith(value)
			]

		return ElementCollection(filtered)

	def contains(self, value: str | ElType, casesensitive: bool = True):
		if not self._field:
			raise ValueError("Must call filterBy() first")

		if isinstance(value, ElType):
			# get 'value' from enum
			value = value.value

		if not casesensitive:
			value = value.casefold()

		handler = self._pattern_handlers.get(self._field)
		if handler:
			ret_values = handler(self.elements)
			filtered = [
				self.elements[i]
				for i, item in enumerate(ret_values)
				if item["ok"]  # exclude errors
				and value
				in (
					str(item["value"]).casefold()
					if not casesensitive
					else str(item["value"])
				)
			]

		return ElementCollection(filtered)

	def equals(self, value: str | int | float | ElType, casesensitive: bool = True):
		"""Keep only the elements whose value match the input.
		Args:
			value (`str` | `int`| `float`| `ElType`): Value to check against.
			casesensitive (`bool`): Determines if the check should be perforemed case-sensitive.

		Returns:
			`ElementCollection`: Returns a new ElementCollection.
		"""
		if not self._field:
			raise ValueError("Must call filterBy() first")

		if isinstance(value, ElType):
			# get 'value' from enum
			value = value.value

		handler = self._pattern_handlers.get(self._field)
		if handler:
			ret_values = handler(self.elements)
			filtered = []
			for i, item in enumerate(ret_values):
				if item["ok"]:  # exclude errors
					if isinstance(value, (int, float)):
						try:
							item_value = float(item["value"])
							if item_value == value:
								filtered.append(self.elements[i])
						except (ValueError, TypeError):
							# Skip non-numeric values
							continue
					else:
						# String comparison
						if not casesensitive:
							value = value.casefold()

						item_str = (
							str(item["value"]).casefold()
							if not casesensitive
							else str(item["value"])
						)
						if value == item_str:
							filtered.append(self.elements[i])

		return ElementCollection(filtered)

	# endregion //

	# region // numeric comparisons
	def lessThan(self, value: int | float, inclusive: bool = False):
		"""Keep only elements whose numeric value is less than the input.
		Args:
			value (`int` | `float`): Numeric value to compare against.
			inclusive (`bool`): If True, uses <= instead of <.

		Returns:
			`ElementCollection`: Returns a new ElementCollection.
		"""
		if not self._field:
			raise ValueError("Must call filterBy() first")

		handler = self._pattern_handlers.get(self._field)
		if handler:
			ret_values = handler(self.elements)
			filtered = []
			for i, item in enumerate(ret_values):
				if item["ok"]:  # exclude errors
					try:
						item_value = float(item["value"])
						if inclusive:
							if item_value <= value:
								filtered.append(self.elements[i])
						else:
							if item_value < value:
								filtered.append(self.elements[i])
					except (ValueError, TypeError):
						# Skip non-numeric values
						continue

		return ElementCollection(filtered)

	def greaterThan(self, value: int | float, inclusive: bool = False):
		"""Keep only elements whose numeric value is greater than the input.
		Args:
			value (`int` | `float`): Numeric value to compare against.
			inclusive (`bool`): If True, uses >= instead of >.

		Returns:
			`ElementCollection`: Returns a new ElementCollection.
		"""
		if not self._field:
			raise ValueError("Must call filterBy() first")

		handler = self._pattern_handlers.get(self._field)
		if handler:
			ret_values = handler(self.elements)
			filtered = []
			for i, item in enumerate(ret_values):
				if item["ok"]:  # exclude errors
					try:
						item_value = float(item["value"])
						if inclusive:
							if item_value >= value:
								filtered.append(self.elements[i])
						else:
							if item_value > value:
								filtered.append(self.elements[i])
					except (ValueError, TypeError):
						# Skip non-numeric values
						continue

		return ElementCollection(filtered)

	def between(
		self, min_value: int | float, max_value: int | float, inclusive: bool = True
	):
		"""Keep only elements whose numeric value is between min and max values.
		Args:
			min_value (`int` | `float`): Minimum value (lower bound).
			max_value (`int` | `float`): Maximum value (upper bound).
			inclusive (`bool`): If True, includes boundary values.

		Returns:
			`ElementCollection`: Returns a new ElementCollection.
		"""
		if not self._field:
			raise ValueError("Must call filterBy() first")

		handler = self._pattern_handlers.get(self._field)
		if handler:
			ret_values = handler(self.elements)
			filtered = []
			for i, item in enumerate(ret_values):
				if item["ok"]:  # exclude errors
					try:
						item_value = float(item["value"])
						if inclusive:
							if min_value <= item_value <= max_value:
								filtered.append(self.elements[i])
						else:
							if min_value < item_value < max_value:
								filtered.append(self.elements[i])
					except (ValueError, TypeError):
						# Skip non-numeric values
						continue

		return ElementCollection(filtered)

	# endregion //
	# region 	//  Helper functions
	def get(self):
		"""Return the filtered elements."""
		return self.elements

	def count(self):
		"""Return the count of filtered elements."""
		return len(self.elements)

	def first(self):
		"""Return the first element or None if empty."""
		return self.elements[0] if self.elements else None

	def toNative(self):
		"""Return a native (original Archicad-Python connection) element list with their appropiate types."""
		return [
			act.ElementIdArrayItem(act.ElementId(item["elementId"]["guid"]))
			for item in self.elements
		]

	# endregion
	# region // actions
	def highlight(
		self,
		*,
		highlightcolor: Color | List[Color] = Color("green"),
		mutedcolor: Color = Color(164, 166, 165, 128),
		wireframe=True,
	):
		"""Highlight the elements in the Collection in the given color and mute all other elements.

		Args:
			highlightcolor (`Color | List[Color]`): A Color or list of Colors used to highlight the element(s).
			mutedcolor (`Color`): A Color to be used on the non-highlighted elements. Optional.
			wirefame (`bool`): Switch non-highlighted elements in the 3D window to wireframe. Optional.

		Example:
			>>> collection.highlight(highlightcolor=Color(230, 20, 10, 255), wireframe=False)
		"""
		tapir.HighlightElements(
			self.elements,
			highlightcolor=highlightcolor,
			mutedcolor=mutedcolor,
			wireframe=wireframe,
		)
		return self

	# endregion

	# region // __dunder__ methods
	def __len__(self):
		return len(self.elements)

	def __iter__(self):
		"""Make ElementCollection iterable over its elements."""
		return iter(self.elements)

	def __getitem__(self, key):
		"""Support slicing and indexing operations."""
		if isinstance(key, slice):
			# return a new ElementCollection with sliced elements
			sliced_elements = self.elements[key]
			return ElementCollection(sliced_elements)
		elif isinstance(key, int):
			# Handle negative indices properly
			if key < 0:
				key = len(self.elements) + key

			# Check bounds
			if key >= len(self.elements) or key < 0:
				raise IndexError("Element index out of range")

			# return the individual element at the given index
			return self.elements[key]
		else:
			raise TypeError("Index must be an integer or slice")

	def __str__(self):
		return f"Collection of {self.count()} element" + (
			"s" if self.count() > 1 else ""
		)

	# There is currently no nice way to make an object JSON serializable without
	# hacking or writing a JsonEncoder.
	# Instead one should just use the ".get()" method; then no error will occur.
	def __dict__(self):
		return {"elements": self.elements}

	def __contains__(self, item):
		"""Check if an element or GUID is in this ElementCollection."""
		if isinstance(item, str):
			return any(
				element["elementId"]["guid"] == item for element in self.elements
			)
		elif isinstance(item, dict) and "elementId" in item:
			guid = item["elementId"]["guid"]
			return any(
				element["elementId"]["guid"] == guid for element in self.elements
			)
		elif isinstance(item, ElementCollection):
			return all(element in self for element in item.elements)
		else:
			return False

	def __add__(self, other):
		"""Combine two ElementCollection instances, removing duplicates based on GUID."""
		if not isinstance(other, ElementCollection):
			raise TypeError("Can only add ElementCollection to ElementCollection")

		# Use a set to track unique GUIDs to avoid duplicates
		seen_guids = set()
		combined_elements = []

		# Add elements from self
		for element in self.elements:
			guid = element["elementId"]["guid"]
			if guid not in seen_guids:
				seen_guids.add(guid)
				combined_elements.append(element)

		# Add elements from other (only if not already present)
		for element in other.elements:
			guid = element["elementId"]["guid"]
			if guid not in seen_guids:
				seen_guids.add(guid)
				combined_elements.append(element)

		return ElementCollection(combined_elements)

	def __iadd__(self, other):
		"""In-place addition (+=) for ElementCollection instances."""
		if not isinstance(other, ElementCollection):
			raise TypeError("Can only add ElementCollection to ElementCollection")

		# Get existing GUIDs
		existing_guids = {element["elementId"]["guid"] for element in self.elements}

		# Add new elements that don't already exist
		for element in other.elements:
			guid = element["elementId"]["guid"]
			if guid not in existing_guids:
				self.elements.append(element)
				existing_guids.add(guid)

		return self

	def __sub__(self, other):
		"""Subtract ElementCollection instances, removing elements that exist in other."""
		if not isinstance(other, ElementCollection):
			raise TypeError(
				"Can only subtract ElementCollection from ElementCollection"
			)

		# Get GUIDs from other collection to remove
		guids_to_remove = {element["elementId"]["guid"] for element in other.elements}

		# Keep only elements whose GUIDs are not in the other collection
		filtered_elements = [
			element
			for element in self.elements
			if element["elementId"]["guid"] not in guids_to_remove
		]

		return ElementCollection(filtered_elements)

	def __isub__(self, other):
		"""In-place subtraction (-=) for ElementCollection instances."""
		if not isinstance(other, ElementCollection):
			raise TypeError(
				"Can only subtract ElementCollection from ElementCollection"
			)

		# Get GUIDs from other collection to remove
		guids_to_remove = {element["elementId"]["guid"] for element in other.elements}

		# Filter out elements that exist in other collection
		self.elements = [
			element
			for element in self.elements
			if element["elementId"]["guid"] not in guids_to_remove
		]

		return self

	# endregion
