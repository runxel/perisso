from archicad import Types as act
from .enums import ElType, Filter
from .utils import getPropValues, getDetails, rtc, acu, _pprint  # noqa: F401


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
		}

	def filterBy(self, field: Filter):
		"""Set the field to filter by. Accepts a Filter enum."""
		if isinstance(field, Filter):
			self._field = field
		else:
			raise TypeError("Field must be a valid Filter enum")
		return self

	def property(self, group: str, name: str):
		"""When filtering to a property all elements that do not have the property available are discarded."""
		if not self._field == Filter.PROPERTY:
			raise ValueError("`filterBy()` must be set to `Filter.PROPERTY'")

		self._propGUID = str(acu.GetUserDefinedPropertyId(group, name).guid)

		# Only include elements that have a "propertyValue" key (not "error")
		_param = {
			"elements": self.elements,
			"properties": [{"propertyId": {"guid": self._propGUID}}],
		}
		_prop_values_or_error = rtc("GetPropertyValuesOfElements", _param)["propertyValuesForElements"]  # fmt: skip
		filtered = []
		for i, prop_result in enumerate(_prop_values_or_error):
			prop_value = prop_result["propertyValues"][0]
			if "propertyValue" in prop_value:
				filtered.append(self.elements[i])

		return ElementCollection(
			filtered, _field=Filter.PROPERTY, _propGUID=self._propGUID
		)

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

	def equals(self, value: str | ElType, casesensitive: bool = True):
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
				== (
					str(item["value"]).casefold()
					if not casesensitive
					else str(item["value"])
				)
			]

		return ElementCollection(filtered)

	# endregion //

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

	# region // actions
	def highlight(
		self,
		*,
		color: list[int] = [77, 235, 103, 100],
		noncolor: list[int] = [164, 166, 165, 128],
		wireframe=True,
	):
		# Validate color parameter
		if not isinstance(color, list) or len(color) != 4:
			raise ValueError("Color must be a list of exactly 4 integers")
		if not all(isinstance(c, int) for c in color):
			raise ValueError("All color values must be integers")
		# Validate nonhighlightedcolor parameter
		if not isinstance(noncolor, list) or len(noncolor) != 4:
			raise ValueError("noncolor must be a list of exactly 4 integers")
		if not all(isinstance(c, int) for c in noncolor):
			raise ValueError("All noncolor values must be integers")

		_param = {
			"elements": self.elements,
			"highlightedColors": [color],
			"wireframe3D": wireframe,
			"nonHighlightedColor": noncolor,
		}
		rtc("HighlightElements", _param)
		return self

	# endregion

	# region // __dunder__ methods
	def __len__(self):
		return len(self.elements)

	def __getitem__(self, key):
		"""Support slicing and indexing operations."""
		if isinstance(key, slice):
			# return a new ElementCollection with sliced elements
			return ElementCollection(self.elements[key])
		elif isinstance(key, int):
			# return the individual element at the given index
			return self.elements[key]
		else:
			raise TypeError("Index must be an integer or slice")

	def __str__(self):
		return f"Collection of {self.count()} element" + (
			"s" if self.count() > 1 else ""
		)

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
