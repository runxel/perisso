from typing import Union, Iterator, Tuple
import math
import random


class Vector:
	"""A vector class for translation vectors. \n
	Used for moving and copying.
	"""

	def __init__(self, x: float, y: float, z: float = None):
		"""Initialize a vector with x, y and optionally z coordinates.

		Args:
		    x: X coordinate
		    y: Y coordinate
		    z: Z coordinate (optional, makes it 3D if provided)
		"""
		self.x = float(x)
		self.y = float(y)
		self.z = float(z) if z is not None else None

	@property
	def is_2d(self) -> bool:
		"""Check if this is a 2D vector."""
		return self.z is None

	@property
	def is_3d(self) -> bool:
		"""Check if this is a 3D vector."""
		return self.z is not None

	@property
	def magnitude(self) -> float:
		"""Calculate the magnitude (length) of the vector."""
		if self.is_2d:
			return math.sqrt(self.x**2 + self.y**2)
		else:
			return math.sqrt(self.x**2 + self.y**2 + self.z**2)

	@property
	def length(self) -> float:
		"""Alias for magnitude."""
		return self.magnitude

	def normalize(self) -> "Vector":
		"""Return a normalized (unit) vector."""
		mag = self.magnitude
		if mag == 0:
			raise ValueError("Cannot normalize zero vector")

		if self.is_2d:
			return Vector(self.x / mag, self.y / mag)
		else:
			return Vector(self.x / mag, self.y / mag, self.z / mag)

	def dot(self, other: "Vector") -> float:
		"""Calculate dot product with another vector."""
		if not isinstance(other, Vector):
			raise TypeError("Can only calculate dot product with another Vector")

		# Convert to same dimensionality
		if self.is_2d and other.is_3d:
			return self.x * other.x + self.y * other.y
		elif self.is_3d and other.is_2d:
			return self.x * other.x + self.y * other.y
		elif self.is_2d and other.is_2d:
			return self.x * other.x + self.y * other.y
		else:  # both 3D
			return self.x * other.x + self.y * other.y + self.z * other.z

	def cross(self, other: "Vector") -> "Vector":
		"""Calculate cross product with another vector (returns 3D vector)."""
		if not isinstance(other, Vector):
			raise TypeError("Can only calculate cross product with another Vector")

		# Convert both to 3D for cross product
		self_z = self.z if self.is_3d else 0
		other_z = other.z if other.is_3d else 0

		return Vector(
			self.y * other_z - self_z * other.y,
			self_z * other.x - self.x * other_z,
			self.x * other.y - self.y * other.x,
		)

	def distance_to(self, other: "Vector") -> float:
		"""Calculate distance to another vector."""
		diff = self - other
		return diff.magnitude

	def angle_to(self, other: "Vector") -> float:
		"""Calculate angle (in radians) to another vector."""
		dot_product = self.dot(other)
		magnitudes = self.magnitude * other.magnitude

		if magnitudes == 0:
			raise ValueError("Cannot calculate angle with zero vector")

		cos_angle = dot_product / magnitudes
		# Clamp to avoid floating point errors
		cos_angle = max(-1, min(1, cos_angle))
		return math.acos(cos_angle)

	def to_2d(self) -> "Vector":
		"""Convert to 2D vector (drops Z component)."""
		return Vector(self.x, self.y)

	def to_3d(self, z: float = 0) -> "Vector":
		"""Convert to 3D vector (adds Z component if missing)."""
		if self.is_3d:
			return Vector(self.x, self.y, self.z)
		else:
			return Vector(self.x, self.y, z)

	def to_dict(self) -> dict:
		"""Convert to dictionary representation."""
		if self.is_2d:
			return {"x": self.x, "y": self.y}
		else:
			return {"x": self.x, "y": self.y, "z": self.z}

	@classmethod
	def from_dict(cls, data: dict) -> "Vector":
		"""Create vector from dictionary."""
		return cls(data["x"], data["y"], data.get("z"))

	@classmethod
	def zero_2d(cls) -> "Vector":
		"""Create a 2D zero vector."""
		return cls(0, 0)

	@classmethod
	def zero_3d(cls) -> "Vector":
		"""Create a 3D zero vector."""
		return cls(0, 0, 0)

	@classmethod
	def unit_x(cls, is_3d: bool = False) -> "Vector":
		"""Create a unit vector in X direction."""
		return cls(1, 0, 0 if is_3d else None)

	@classmethod
	def unit_y(cls, is_3d: bool = False) -> "Vector":
		"""Create a unit vector in Y direction."""
		return cls(0, 1, 0 if is_3d else None)

	@classmethod
	def unit_z(cls) -> "Vector":
		"""Create a unit vector in Z direction (3D only)."""
		return cls(0, 0, 1)

	# Mathematical operations
	def __add__(self, other: Union["Vector", float]) -> "Vector":
		"""Add vectors or scalar."""
		if isinstance(other, Vector):
			if self.is_2d and other.is_2d:
				return Vector(self.x + other.x, self.y + other.y)
			elif self.is_3d and other.is_3d:
				return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
			else:
				# Mixed dimensionality - convert to 3D
				self_3d = self.to_3d()
				other_3d = other.to_3d()
				return Vector(
					self_3d.x + other_3d.x,
					self_3d.y + other_3d.y,
					self_3d.z + other_3d.z,
				)
		elif isinstance(other, (int, float)):
			if self.is_2d:
				return Vector(self.x + other, self.y + other)
			else:
				return Vector(self.x + other, self.y + other, self.z + other)
		else:
			raise TypeError("Can only add Vector or numeric value")

	def __radd__(self, other: Union[float, int]) -> "Vector":
		"""Right addition for scalars."""
		return self.__add__(other)

	def __sub__(self, other: Union["Vector", float]) -> "Vector":
		"""Subtract vectors or scalar."""
		if isinstance(other, Vector):
			if self.is_2d and other.is_2d:
				return Vector(self.x - other.x, self.y - other.y)
			elif self.is_3d and other.is_3d:
				return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
			else:
				# Mixed dimensionality - convert to 3D
				self_3d = self.to_3d()
				other_3d = other.to_3d()
				return Vector(
					self_3d.x - other_3d.x,
					self_3d.y - other_3d.y,
					self_3d.z - other_3d.z,
				)
		elif isinstance(other, (int, float)):
			if self.is_2d:
				return Vector(self.x - other, self.y - other)
			else:
				return Vector(self.x - other, self.y - other, self.z - other)
		else:
			raise TypeError("Can only subtract Vector or numeric value")

	def __rsub__(self, other: Union[float, int]) -> "Vector":
		"""Right subtraction for scalars."""
		if isinstance(other, (int, float)):
			if self.is_2d:
				return Vector(other - self.x, other - self.y)
			else:
				return Vector(other - self.x, other - self.y, other - self.z)
		else:
			raise TypeError("Can only subtract from numeric value")

	def __mul__(self, scalar: Union[float, int]) -> "Vector":
		"""Multiply by scalar."""
		if isinstance(scalar, (int, float)):
			if self.is_2d:
				return Vector(self.x * scalar, self.y * scalar)
			else:
				return Vector(self.x * scalar, self.y * scalar, self.z * scalar)
		else:
			raise TypeError("Can only multiply by numeric value")

	def __rmul__(self, scalar: Union[float, int]) -> "Vector":
		"""Right multiplication by scalar."""
		return self.__mul__(scalar)

	def __truediv__(self, scalar: Union[float, int]) -> "Vector":
		"""Divide by scalar."""
		if isinstance(scalar, (int, float)):
			if scalar == 0:
				raise ValueError("Cannot divide by zero")
			if self.is_2d:
				return Vector(self.x / scalar, self.y / scalar)
			else:
				return Vector(self.x / scalar, self.y / scalar, self.z / scalar)
		else:
			raise TypeError("Can only divide by numeric value")

	def __neg__(self) -> "Vector":
		"""Negate vector."""
		if self.is_2d:
			return Vector(-self.x, -self.y)
		else:
			return Vector(-self.x, -self.y, -self.z)

	def __abs__(self) -> float:
		"""Return magnitude of vector."""
		return self.magnitude

	# Comparison operations
	def __eq__(self, other) -> bool:
		"""Check equality with another vector."""
		if not isinstance(other, Vector):
			return False

		if self.is_2d and other.is_2d:
			return self.x == other.x and self.y == other.y
		elif self.is_3d and other.is_3d:
			return self.x == other.x and self.y == other.y and self.z == other.z
		else:
			return False

	def __ne__(self, other) -> bool:
		"""Check inequality with another vector."""
		return not self.__eq__(other)

	# Container operations
	def __getitem__(self, index: int) -> float:
		"""Get component by index (0=x, 1=y, 2=z)."""
		if index == 0:
			return self.x
		elif index == 1:
			return self.y
		elif index == 2:
			if self.is_2d:
				raise IndexError("2D vector has no z component")
			return self.z
		else:
			raise IndexError("Vector index out of range")

	def __setitem__(self, index: int, value: float):
		"""Set component by index (0=x, 1=y, 2=z)."""
		if index == 0:
			self.x = float(value)
		elif index == 1:
			self.y = float(value)
		elif index == 2:
			if self.is_2d:
				raise IndexError("2D vector has no z component")
			self.z = float(value)
		else:
			raise IndexError("Vector index out of range")

	def __len__(self) -> int:
		"""Return dimension of vector (2 or 3)."""
		return 2 if self.is_2d else 3

	def __iter__(self) -> Iterator[float]:
		"""Iterate over components."""
		yield self.x
		yield self.y
		if self.is_3d:
			yield self.z

	# String representations
	def __str__(self) -> str:
		"""Simple string representation."""
		if self.is_2d:
			return f"Vector2D({self.x}, {self.y})"
		else:
			return f"Vector3D({self.x}, {self.y}, {self.z})"

	def __repr__(self) -> str:
		"""Detailed string representation."""
		if self.is_2d:
			return f"Vector({self.x}, {self.y})"
		else:
			return f"Vector({self.x}, {self.y}, {self.z})"


class Coordinate:
	"""A coordinate class that can handle both 2D and 3D points in space."""

	def __init__(self, x: float, y: float, z: float = None):
		"""Initialize a coordinate with x, y and optionally z values.

		Args:
		    x: X coordinate
		    y: Y coordinate
		    z: Z coordinate (optional, makes it 3D if provided)
		"""
		self.x = float(x)
		self.y = float(y)
		self.z = float(z) if z is not None else None

	@property
	def is_2d(self) -> bool:
		"""Check if this is a 2D coordinate."""
		return self.z is None

	@property
	def is_3d(self) -> bool:
		"""Check if this is a 3D coordinate."""
		return self.z is not None

	def distance_to(self, other: "Coordinate") -> float:
		"""Calculate distance to another coordinate."""
		if not isinstance(other, Coordinate):
			raise TypeError("Can only calculate distance to another Coordinate")

		if self.is_2d and other.is_2d:
			return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
		else:
			# Convert both to 3D for distance calculation
			self_z = self.z if self.is_3d else 0
			other_z = other.z if other.is_3d else 0
			return math.sqrt(
				(self.x - other.x) ** 2
				+ (self.y - other.y) ** 2
				+ (self_z - other_z) ** 2
			)

	def midpoint_to(self, other: "Coordinate") -> "Coordinate":
		"""Calculate midpoint between this and another coordinate."""
		if not isinstance(other, Coordinate):
			raise TypeError("Can only calculate midpoint to another Coordinate")

		if self.is_2d and other.is_2d:
			return Coordinate((self.x + other.x) / 2, (self.y + other.y) / 2)
		else:
			# Convert both to 3D for midpoint calculation
			self_z = self.z if self.is_3d else 0
			other_z = other.z if other.is_3d else 0
			return Coordinate(
				(self.x + other.x) / 2, (self.y + other.y) / 2, (self_z + other_z) / 2
			)

	def translate(self, vector: "Vector") -> "Coordinate":
		"""Translate this coordinate by a vector."""
		from .types import Vector

		if not isinstance(vector, Vector):
			raise TypeError("Can only translate by a Vector")

		if self.is_2d and vector.is_2d:
			return Coordinate(self.x + vector.x, self.y + vector.y)
		else:
			# Convert both to 3D for translation
			self_z = self.z if self.is_3d else 0
			vector_z = vector.z if vector.is_3d else 0
			return Coordinate(self.x + vector.x, self.y + vector.y, self_z + vector_z)

	def vector_to(self, other: "Coordinate") -> "Vector":
		"""Create a vector from this coordinate to another coordinate."""
		from .types import Vector

		if not isinstance(other, Coordinate):
			raise TypeError("Can only create vector to another Coordinate")

		if self.is_2d and other.is_2d:
			return Vector(other.x - self.x, other.y - self.y)
		else:
			# Convert both to 3D for vector calculation
			self_z = self.z if self.is_3d else 0
			other_z = other.z if other.is_3d else 0
			return Vector(other.x - self.x, other.y - self.y, other_z - self_z)

	def rotate_around(self, center: "Coordinate", angle: float) -> "Coordinate":
		"""Rotate this coordinate around another coordinate by angle (in radians).
		Only works for 2D coordinates."""
		if not isinstance(center, Coordinate):
			raise TypeError("Center must be a Coordinate")

		if self.is_3d or center.is_3d:
			raise NotImplementedError("3D rotation not implemented")

		# Translate to origin
		dx = self.x - center.x
		dy = self.y - center.y

		# Rotate
		cos_a = math.cos(angle)
		sin_a = math.sin(angle)

		new_x = dx * cos_a - dy * sin_a
		new_y = dx * sin_a + dy * cos_a

		# Translate back
		return Coordinate(new_x + center.x, new_y + center.y)

	def to_2d(self) -> "Coordinate":
		"""Convert to 2D coordinate (drops Z component)."""
		return Coordinate(self.x, self.y)

	def to_3d(self, z: float = 0) -> "Coordinate":
		"""Convert to 3D coordinate (adds Z component if missing)."""
		if self.is_3d:
			return Coordinate(self.x, self.y, self.z)
		else:
			return Coordinate(self.x, self.y, z)

	def to_tuple(self) -> Union[Tuple[float, float], Tuple[float, float, float]]:
		"""Convert to tuple representation."""
		if self.is_2d:
			return (self.x, self.y)
		else:
			return (self.x, self.y, self.z)

	def to_dict(self) -> dict:
		"""Convert to dictionary representation."""
		if self.is_2d:
			return {"x": self.x, "y": self.y}
		else:
			return {"x": self.x, "y": self.y, "z": self.z}

	@classmethod
	def from_tuple(
		cls, data: Union[Tuple[float, float], Tuple[float, float, float]]
	) -> "Coordinate":
		"""Create coordinate from tuple."""
		if len(data) == 2:
			return cls(data[0], data[1])
		elif len(data) == 3:
			return cls(data[0], data[1], data[2])
		else:
			raise ValueError("Tuple must have 2 or 3 elements")

	@classmethod
	def from_dict(cls, data: dict) -> "Coordinate":
		"""Create coordinate from dictionary."""
		return cls(data["x"], data["y"], data.get("z"))

	@classmethod
	def origin_2d(cls) -> "Coordinate":
		"""Create a 2D origin coordinate (0, 0)."""
		return cls(0, 0)

	@classmethod
	def origin_3d(cls) -> "Coordinate":
		"""Create a 3D origin coordinate (0, 0, 0)."""
		return cls(0, 0, 0)

	# Mathematical operations with coordinates
	def __add__(self, other: Union["Coordinate", "Vector", float]) -> "Coordinate":
		"""Add coordinate/vector or scalar to this coordinate."""
		if isinstance(other, Coordinate):
			# Adding coordinates creates a new coordinate
			if self.is_2d and other.is_2d:
				return Coordinate(self.x + other.x, self.y + other.y)
			else:
				self_z = self.z if self.is_3d else 0
				other_z = other.z if other.is_3d else 0
				return Coordinate(self.x + other.x, self.y + other.y, self_z + other_z)
		elif hasattr(other, "x") and hasattr(other, "y"):  # Vector-like object
			return self.translate(other)
		elif isinstance(other, (int, float)):
			if self.is_2d:
				return Coordinate(self.x + other, self.y + other)
			else:
				return Coordinate(self.x + other, self.y + other, self.z + other)
		else:
			raise TypeError("Can only add Coordinate, Vector, or numeric value")

	def __radd__(self, other: Union[float, int]) -> "Coordinate":
		"""Right addition for scalars."""
		return self.__add__(other)

	def __sub__(
		self, other: Union["Coordinate", "Vector", float]
	) -> Union["Coordinate", "Vector"]:
		"""Subtract coordinate/vector or scalar from this coordinate."""
		if isinstance(other, Coordinate):
			# Subtracting coordinates creates a vector
			return self.vector_to(other).__neg__()  # Reverse direction
		elif hasattr(other, "x") and hasattr(other, "y"):  # Vector-like object
			# Subtracting vector from coordinate creates coordinate
			return self.translate(other.__neg__())
		elif isinstance(other, (int, float)):
			if self.is_2d:
				return Coordinate(self.x - other, self.y - other)
			else:
				return Coordinate(self.x - other, self.y - other, self.z - other)
		else:
			raise TypeError("Can only subtract Coordinate, Vector, or numeric value")

	def __rsub__(self, other: Union[float, int]) -> "Coordinate":
		"""Right subtraction for scalars."""
		if isinstance(other, (int, float)):
			if self.is_2d:
				return Coordinate(other - self.x, other - self.y)
			else:
				return Coordinate(other - self.x, other - self.y, other - self.z)
		else:
			raise TypeError("Can only subtract from numeric value")

	def __mul__(self, scalar: Union[float, int]) -> "Coordinate":
		"""Multiply coordinate by scalar (scaling from origin)."""
		if isinstance(scalar, (int, float)):
			if self.is_2d:
				return Coordinate(self.x * scalar, self.y * scalar)
			else:
				return Coordinate(self.x * scalar, self.y * scalar, self.z * scalar)
		else:
			raise TypeError("Can only multiply by numeric value")

	def __rmul__(self, scalar: Union[float, int]) -> "Coordinate":
		"""Right multiplication by scalar."""
		return self.__mul__(scalar)

	def __truediv__(self, scalar: Union[float, int]) -> "Coordinate":
		"""Divide coordinate by scalar."""
		if isinstance(scalar, (int, float)):
			if scalar == 0:
				raise ValueError("Cannot divide by zero")
			if self.is_2d:
				return Coordinate(self.x / scalar, self.y / scalar)
			else:
				return Coordinate(self.x / scalar, self.y / scalar, self.z / scalar)
		else:
			raise TypeError("Can only divide by numeric value")

	def __neg__(self) -> "Coordinate":
		"""Negate coordinate (reflection through origin)."""
		if self.is_2d:
			return Coordinate(-self.x, -self.y)
		else:
			return Coordinate(-self.x, -self.y, -self.z)

	# Comparison operations
	def __eq__(self, other) -> bool:
		"""Check equality with another coordinate."""
		if not isinstance(other, Coordinate):
			return False

		if self.is_2d and other.is_2d:
			return self.x == other.x and self.y == other.y
		elif self.is_3d and other.is_3d:
			return self.x == other.x and self.y == other.y and self.z == other.z
		else:
			return False

	def __ne__(self, other) -> bool:
		"""Check inequality with another coordinate."""
		return not self.__eq__(other)

	def is_close(self, other: "Coordinate", tolerance: float = 1e-9) -> bool:
		"""Check if coordinate is close to another within tolerance."""
		if not isinstance(other, Coordinate):
			return False

		return self.distance_to(other) <= tolerance

	# Container operations
	def __getitem__(self, index: int) -> float:
		"""Get component by index (0=x, 1=y, 2=z)."""
		if index == 0:
			return self.x
		elif index == 1:
			return self.y
		elif index == 2:
			if self.is_2d:
				raise IndexError("2D coordinate has no z component")
			return self.z
		else:
			raise IndexError("Coordinate index out of range")

	def __setitem__(self, index: int, value: float):
		"""Set component by index (0=x, 1=y, 2=z)."""
		if index == 0:
			self.x = float(value)
		elif index == 1:
			self.y = float(value)
		elif index == 2:
			if self.is_2d:
				raise IndexError("2D coordinate has no z component")
			self.z = float(value)
		else:
			raise IndexError("Coordinate index out of range")

	def __len__(self) -> int:
		"""Return dimension of coordinate (2 or 3)."""
		return 2 if self.is_2d else 3

	def __iter__(self) -> Iterator[float]:
		"""Iterate over components."""
		yield self.x
		yield self.y
		if self.is_3d:
			yield self.z

	# String representations
	def __str__(self) -> str:
		"""Simple string representation."""
		if self.is_2d:
			return f"Coord2D({self.x}, {self.y})"
		else:
			return f"Coord3D({self.x}, {self.y}, {self.z})"

	def __repr__(self) -> str:
		"""Detailed string representation."""
		if self.is_2d:
			return f"Coordinate({self.x}, {self.y})"
		else:
			return f"Coordinate({self.x}, {self.y}, {self.z})"

	# Hash support for use in sets and as dict keys
	def __hash__(self) -> int:
		"""Hash support for coordinates."""
		if self.is_2d:
			return hash((self.x, self.y))
		else:
			return hash((self.x, self.y, self.z))


class Arc:
	"""An arc segment defined by start point, end point, and arc angle."""

	def __init__(
		self, start_point: Coordinate, end_point: Coordinate, arc_angle: float
	):
		"""Initialize an arc with start point, end point, and arc angle.

		Args:
			start_point (`Coordinate`): Starting coordinate of the arc
			end_point (`Coordinate`): Ending coordinate of the arc
			arc_angle (`float`): Arc angle in radians (positive = counterclockwise)

		This corresponds with the internal Archicad parametrization.
		"""
		self.start_point = start_point
		self.end_point = end_point
		self.arc_angle = float(arc_angle)

	@property
	def chord_length(self) -> float:
		"""Calculate the chord length (straight line distance between endpoints)."""
		return self.start_point.distance_to(self.end_point)

	@property
	def radius(self) -> float:
		"""Calculate the radius of the arc."""
		if abs(self.arc_angle) < 1e-10:  # Nearly straight line
			return float("inf")

		chord = self.chord_length
		return chord / (2 * math.sin(abs(self.arc_angle) / 2))

	@property
	def length(self) -> float:
		"""Calculate the arc length."""
		if abs(self.arc_angle) < 1e-10:  # Nearly straight line
			return self.chord_length

		return self.radius * abs(self.arc_angle)

	@property
	def center(self) -> Coordinate:
		"""Calculate the center point of the arc."""
		if abs(self.arc_angle) < 1e-10:  # Nearly straight line
			return self.start_point.midpoint_to(self.end_point)

		# Midpoint of chord
		chord_mid = self.start_point.midpoint_to(self.end_point)

		# Vector from start to end
		chord_vector = self.start_point.vector_to(self.end_point)

		# Perpendicular vector (rotated 90 degrees)
		if chord_vector.is_2d:
			perp_vector = Vector(-chord_vector.y, chord_vector.x)
		else:
			# in 3D we need a reference plane - let's assume the XY plane
			perp_vector = Vector(-chord_vector.y, chord_vector.x, 0)

		# Distance from chord midpoint to arc center
		chord_half = self.chord_length / 2
		if abs(self.arc_angle) >= math.pi:
			# Large arc
			sagitta = self.radius - math.sqrt(self.radius**2 - chord_half**2)
		else:
			# Small arc
			sagitta = self.radius - math.sqrt(self.radius**2 - chord_half**2)

		# Determine direction based on arc angle sign
		if self.arc_angle < 0:
			sagitta = -sagitta

		# Normalize perpendicular vector and scale by sagitta
		perp_unit = perp_vector.normalize()
		offset_vector = perp_unit * sagitta

		return chord_mid.translate(offset_vector)

	def to_dict(self) -> dict:
		"""Convert to dictionary representation."""
		return {
			"startPoint": self.start_point.to_dict(),
			"endPoint": self.end_point.to_dict(),
			"arcAngle": self.arc_angle,
			"length": self.length,
			"radius": self.radius,
		}

	@classmethod
	def from_coordinates_and_angle(cls, start: dict, end: dict, angle: float) -> "Arc":
		"""Create arc from coordinate dictionaries and angle."""
		start_coord = Coordinate.from_dict(start)
		end_coord = Coordinate.from_dict(end)
		return cls(start_coord, end_coord, angle)

	def __str__(self) -> str:
		"""String representation of the arc."""
		return f"Arc(start={self.start_point}, end={self.end_point}, angle={self.arc_angle:.4f}rad, length={self.length:.4f})"

	def __repr__(self) -> str:
		"""Detailed string representation."""
		return self.__str__()


class Polyline:
	"""A 2D polyline class that handles coordinates and optional arc segments."""

	def __init__(
		self,
		coordinates: list[Union[Coordinate, dict, tuple]],
		arcs: list[dict] = None,
		is_closed: bool = False,
	):
		"""Initialize a polyline with coordinates and optional arcs.

		Args:
			coordinates: List of Coordinate objects, dictionaries, or tuples.
			arcs: Optional list of arc definitions with begIndex, endIndex, arcAngle.
			is_closed: If True, automatically closes the polyline by duplicating first point.
		"""
		self.coordinates = []
		self.arcs = arcs or []
		self.is_closed = is_closed

		# Convert coordinates to Coordinate objects
		for coord in coordinates:
			if isinstance(coord, Coordinate):
				self.coordinates.append(coord)
			elif isinstance(coord, dict):
				self.coordinates.append(Coordinate.from_dict(coord))
			elif isinstance(coord, (list, tuple)) and len(coord) >= 2:
				self.coordinates.append(Coordinate(coord[0], coord[1]))
			else:
				raise ValueError(f"Invalid coordinate format: {coord}")

		# Handle closed polyline
		if self.is_closed and len(self.coordinates) > 1:
			# Check if already closed (first and last points are the same)
			if not self.coordinates[0].is_close(self.coordinates[-1]):
				# Add first point as last point to close the polyline
				self.coordinates.append(
					Coordinate(self.coordinates[0].x, self.coordinates[0].y)
				)

		# Validate and process arcs
		self._validate_arcs()

	def _validate_arcs(self):
		"""Validate arc definitions and set implicit endIndex values."""
		if not self.arcs:
			return

		for i, arc in enumerate(self.arcs):
			# Validate required fields
			if "begIndex" not in arc:
				raise ValueError(f"Arc {i} missing 'begIndex'")
			if "arcAngle" not in arc:
				raise ValueError(f"Arc {i} missing 'arcAngle'")

			beg_index = arc["begIndex"]

			# Set implicit endIndex if not specified
			if "endIndex" not in arc:
				arc["endIndex"] = beg_index + 1

			end_index = arc["endIndex"]

			# Validate indices
			if beg_index < 0 or beg_index >= len(self.coordinates):
				raise ValueError(f"Arc {i} begIndex {beg_index} out of range")
			if end_index < 0 or end_index >= len(self.coordinates):
				raise ValueError(f"Arc {i} endIndex {end_index} out of range")
			if beg_index >= end_index:
				raise ValueError(f"Arc {i} begIndex must be less than endIndex")

	@property
	def length(self) -> float:
		"""Calculate the total length of the polyline."""
		if len(self.coordinates) < 2:
			return 0.0

		total_length = 0.0
		arc_lookup = {
			(arc["begIndex"], arc["endIndex"]): arc["arcAngle"] for arc in self.arcs
		}

		# Calculate length for each segment
		for i in range(len(self.coordinates) - 1):
			start_point = self.coordinates[i]
			end_point = self.coordinates[i + 1]

			# Check if this segment is an arc
			if (i, i + 1) in arc_lookup:
				# This is an arc segment
				arc_angle = arc_lookup[(i, i + 1)]
				arc = Arc(start_point, end_point, arc_angle)
				segment_length = arc.length
			else:
				# This is a straight segment
				segment_length = start_point.distance_to(end_point)

			total_length += segment_length

		return total_length

	@property
	def vertex_count(self) -> int:
		"""Get the number of vertices in the polyline."""
		return len(self.coordinates)

	@property
	def segment_count(self) -> int:
		"""Get the number of segments in the polyline."""
		return max(0, len(self.coordinates) - 1)

	def get_segment(self, index: int) -> Union[Coordinate, Arc]:
		"""Get a segment by index (returns either straight line endpoints or Arc object).

		Args:
			index: Segment index (0-based).

		Returns:
			Tuple of (start_coord, end_coord) for straight segments, or Arc object for arc segments.
		"""
		if index < 0 or index >= self.segment_count:
			raise IndexError(f"Segment index {index} out of range")

		start_point = self.coordinates[index]
		end_point = self.coordinates[index + 1]

		# Check if this segment is an arc
		arc_lookup = {
			(arc["begIndex"], arc["endIndex"]): arc["arcAngle"] for arc in self.arcs
		}

		if (index, index + 1) in arc_lookup:
			arc_angle = arc_lookup[(index, index + 1)]
			return Arc(start_point, end_point, arc_angle)
		else:
			return (start_point, end_point)

	def get_arc_segments(self) -> list[Arc]:
		"""Get all arc segments as Arc objects."""
		arc_segments = []
		for arc_def in self.arcs:
			start_point = self.coordinates[arc_def["begIndex"]]
			end_point = self.coordinates[arc_def["endIndex"]]
			arc_segments.append(Arc(start_point, end_point, arc_def["arcAngle"]))
		return arc_segments

	def get_straight_segments(self) -> list[tuple[Coordinate, Coordinate]]:
		"""Get all straight segments as coordinate pairs."""
		arc_lookup = {(arc["begIndex"], arc["endIndex"]) for arc in self.arcs}
		straight_segments = []

		for i in range(self.segment_count):
			if (i, i + 1) not in arc_lookup:
				straight_segments.append((self.coordinates[i], self.coordinates[i + 1]))

		return straight_segments

	def add_coordinate(
		self, coordinate: Union[Coordinate, dict, tuple], index: int = None
	):
		"""Add a coordinate at specified index (or at the end if index is None).

		Note: Adding coordinates may invalidate existing arc indices.
		"""
		if isinstance(coordinate, Coordinate):
			new_coord = coordinate
		elif isinstance(coordinate, dict):
			new_coord = Coordinate.from_dict(coordinate)
		elif isinstance(coordinate, (list, tuple)) and len(coordinate) >= 2:
			new_coord = Coordinate(coordinate[0], coordinate[1])
		else:
			raise ValueError(f"Invalid coordinate format: {coordinate}")

		if index is None:
			# Add at the end (but before the closing point if closed)
			if self.is_closed and len(self.coordinates) > 1:
				self.coordinates.insert(-1, new_coord)
			else:
				self.coordinates.append(new_coord)
		else:
			self.coordinates.insert(index, new_coord)

		# Note: This may invalidate arc indices...

	def add_arc(self, beg_index: int, end_index: int = None, arc_angle: float = 0.0):
		"""Add an arc definition to the polyline.

		Args:
			beg_index (`int`): The index of the node where the arc starts.
				Please remember that in Python indices start at 0 (zero)!
			end_index (`int`): Optional. Implicitely one node after 'beg_index'.
			arc_angle (`float`): Angle of the arc; if positive, the arc will be on the right-hand side
				of a hypothetical straight segment between the points.
		"""
		if end_index is None:
			end_index = beg_index + 1

		arc_def = {"begIndex": beg_index, "endIndex": end_index, "arcAngle": arc_angle}

		self.arcs.append(arc_def)
		self._validate_arcs()

	def close(self):
		"""Close the polyline by adding the first point as the last point."""
		if not self.is_closed and len(self.coordinates) > 1:
			if not self.coordinates[0].is_close(self.coordinates[-1]):
				self.coordinates.append(
					Coordinate(self.coordinates[0].x, self.coordinates[0].y)
				)
			self.is_closed = True

	def open(self):
		"""Open the polyline by removing the last point if it equals the first."""
		if self.is_closed and len(self.coordinates) > 2:
			if self.coordinates[0].is_close(self.coordinates[-1]):
				self.coordinates.pop()
			self.is_closed = False

	def reverse(self):
		"""Reverse the direction of the polyline."""
		self.coordinates.reverse()

		# Update arc indices and reverse arc angles
		max_index = len(self.coordinates) - 1
		for arc in self.arcs:
			old_beg = arc["begIndex"]
			old_end = arc["endIndex"]
			arc["begIndex"] = max_index - old_end
			arc["endIndex"] = max_index - old_beg
			arc["arcAngle"] = -arc["arcAngle"]  # Reverse arc direction

		# Sort arcs by begIndex to maintain order
		self.arcs.sort(key=lambda x: x["begIndex"])

	def to_dict(self) -> dict:
		"""Convert to dictionary representation matching Archicad format."""
		result = {"coordinates": [coord.to_dict() for coord in self.coordinates]}

		if self.arcs:
			result["arcs"] = self.arcs.copy()

		return result

	@classmethod
	def from_dict(cls, data: dict, is_closed: bool = False) -> "Polyline":
		"""Create polyline from dictionary (Archicad format)."""
		coordinates = data.get("coordinates", [])
		arcs = data.get("arcs", [])
		return cls(coordinates, arcs, is_closed)

	@classmethod
	def rectangle(
		cls, corner1: Union[Coordinate, tuple], corner2: Union[Coordinate, tuple]
	) -> "Polyline":
		"""Create a rectangular polyline from two opposite corners."""
		if isinstance(corner1, (list, tuple)):
			corner1 = Coordinate(corner1[0], corner1[1])
		if isinstance(corner2, (list, tuple)):
			corner2 = Coordinate(corner2[0], corner2[1])

		coordinates = [
			corner1,
			Coordinate(corner2.x, corner1.y),
			corner2,
			Coordinate(corner1.x, corner2.y),
		]

		return cls(coordinates, is_closed=True)

	@classmethod
	def circle_approximation(
		cls, center: Union[Coordinate, tuple], radius: float, segments: int = 16
	) -> "Polyline":
		"""Create a circular polyline approximation using line segments."""
		if isinstance(center, (list, tuple)):
			center = Coordinate(center[0], center[1])

		coordinates = []
		angle_step = 2 * math.pi / segments

		for i in range(segments):
			angle = i * angle_step
			x = center.x + radius * math.cos(angle)
			y = center.y + radius * math.sin(angle)
			coordinates.append(Coordinate(x, y))

		return cls(coordinates, is_closed=True)

	# Container operations
	def __len__(self) -> int:
		"""Return number of coordinates."""
		return len(self.coordinates)

	def __getitem__(self, index: int) -> Coordinate:
		"""Get coordinate by index."""
		return self.coordinates[index]

	def __setitem__(self, index: int, value: Union[Coordinate, dict, tuple]):
		"""Set coordinate by index."""
		if isinstance(value, Coordinate):
			self.coordinates[index] = value
		elif isinstance(value, dict):
			self.coordinates[index] = Coordinate.from_dict(value)
		elif isinstance(value, (list, tuple)) and len(value) >= 2:
			self.coordinates[index] = Coordinate(value[0], value[1])
		else:
			raise ValueError(f"Invalid coordinate format: {value}")

	def __iter__(self) -> Iterator[Coordinate]:
		"""Iterate over coordinates."""
		return iter(self.coordinates)

	def __contains__(self, coordinate: Coordinate) -> bool:
		"""Check if coordinate exists in polyline."""
		return any(coord.is_close(coordinate) for coord in self.coordinates)

	# String representations
	def __str__(self) -> str:
		"""Simple string representation."""
		closed_str = "closed with " if self.is_closed else ""
		arc_str = f", {len(self.arcs)} arcs" if self.arcs else ""
		return f"Polyline ({closed_str}{len(self.coordinates)} points{arc_str})"

	def __repr__(self) -> str:
		"""Detailed string representation."""
		return f"Polyline (coordinates={self.coordinates}, arcs={self.arcs}, is_closed={self.is_closed})"


class Color:
	"""A color class that handles various color formats and converts them to RGBA integers."""

	# Predefined color names
	COLORS = {
		"black": (0, 0, 0, 255),
		"white": (255, 255, 255, 255),
		"red": (255, 0, 0, 255),
		"green": (0, 128, 0, 255),
		"blue": (0, 0, 255, 255),
		"yellow": (255, 255, 0, 255),
		"cyan": (0, 255, 255, 255),
		"magenta": (255, 0, 255, 255),
		"orange": (255, 165, 0, 255),
		"purple": (128, 0, 128, 255),
		"pink": (255, 192, 203, 255),
		"brown": (165, 42, 42, 255),
		"gray": (128, 128, 128, 255),
		"grey": (128, 128, 128, 255),
		"lime": (0, 255, 0, 255),
		"navy": (0, 0, 128, 255),
		"olive": (128, 128, 0, 255),
		"silver": (192, 192, 192, 255),
		"teal": (0, 128, 128, 255),
		"maroon": (128, 0, 0, 255),
		"transparent": (0, 0, 0, 0),
	}

	def __init__(self, *args, **kwargs):
		"""Initialize a color from various formats.

		Args:
			Can be called in multiple ways:
			- Color("#FF0000") - 6-digit hex
			- Color("#FF0000FF") - 8-digit hex with alpha
			- Color("red") - named color
			- Color(255, 0, 0) - RGB integers (0-255)
			- Color(255, 0, 0, 128) - RGBA integers (0-255)
			- Color(r=1.0, g=0.0, b=0.0) - RGB floats (0.0-1.0)
			- Color(r=1.0, g=0.0, b=0.0, a=0.5) - RGBA floats (0.0-1.0)
		"""
		self.r: int = 0
		self.g: int = 0
		self.b: int = 0
		self.a: int = 255

		if len(args) == 1:
			arg = args[0]
			if isinstance(arg, str):
				if arg.startswith("#"):
					self._from_hex(arg)
				else:
					self._from_name(arg)
			elif isinstance(arg, (list, tuple)) and len(arg) in (3, 4):
				self._from_sequence(arg)
			else:
				raise ValueError(f"Invalid single argument: {arg}")
		elif len(args) == 3:
			# RGB integers
			self._from_rgb_int(*args)
		elif len(args) == 4:
			# RGBA integers
			self._from_rgba_int(*args)
		elif len(args) == 0 and kwargs:
			# Keyword arguments (floats or integers)
			self._from_kwargs(kwargs)
		else:
			raise ValueError(f"Invalid arguments: {args}, {kwargs}")

	def _from_hex(self, hex_string: str):
		"""Parse hex color string."""
		hex_string = hex_string.lstrip("#")

		if len(hex_string) == 6:
			# RGB hex
			self.r = int(hex_string[0:2], 16)
			self.g = int(hex_string[2:4], 16)
			self.b = int(hex_string[4:6], 16)
			self.a = 255
		elif len(hex_string) == 8:
			# RGBA hex
			self.r = int(hex_string[0:2], 16)
			self.g = int(hex_string[2:4], 16)
			self.b = int(hex_string[4:6], 16)
			self.a = int(hex_string[6:8], 16)
		else:
			raise ValueError(f"Invalid hex color: #{hex_string}")

	def _from_name(self, name: str):
		"""Parse named color."""
		name = name.lower()
		if name in self.COLORS:
			self.r, self.g, self.b, self.a = self.COLORS[name]
		else:
			raise ValueError(f"Unknown color name: {name}")

	def _from_sequence(self, seq):
		"""Parse from list or tuple."""
		if len(seq) == 3:
			# Check if values are floats (0-1) or integers (0-255)
			if all(
				isinstance(x, float) or (isinstance(x, (int, float)) and 0 <= x <= 1)
				for x in seq
			):
				self._from_rgb_float(*seq)
			else:
				self._from_rgb_int(*seq)
		elif len(seq) == 4:
			# Check if values are floats (0-1) or integers (0-255)
			if all(
				isinstance(x, float) or (isinstance(x, (int, float)) and 0 <= x <= 1)
				for x in seq
			):
				self._from_rgba_float(*seq)
			else:
				self._from_rgba_int(*seq)

	def _from_rgb_int(self, r: int, g: int, b: int):
		"""Parse from RGB integers (0-255)."""
		self.r = self._clamp_int(r)
		self.g = self._clamp_int(g)
		self.b = self._clamp_int(b)
		self.a = 255

	def _from_rgba_int(self, r: int, g: int, b: int, a: int):
		"""Parse from RGBA integers (0-255)."""
		self.r = self._clamp_int(r)
		self.g = self._clamp_int(g)
		self.b = self._clamp_int(b)
		self.a = self._clamp_int(a)

	def _from_rgb_float(self, r: float, g: float, b: float):
		"""Parse from RGB floats (0.0-1.0)."""
		self.r = self._float_to_int(r)
		self.g = self._float_to_int(g)
		self.b = self._float_to_int(b)
		self.a = 255

	def _from_rgba_float(self, r: float, g: float, b: float, a: float):
		"""Parse from RGBA floats (0.0-1.0)."""
		self.r = self._float_to_int(r)
		self.g = self._float_to_int(g)
		self.b = self._float_to_int(b)
		self.a = self._float_to_int(a)

	def _from_kwargs(self, kwargs: dict):
		"""Parse from keyword arguments."""
		r = kwargs.get("r", 0)
		g = kwargs.get("g", 0)
		b = kwargs.get("b", 0)
		a = kwargs.get(
			"a",
			1.0
			if any(isinstance(v, float) and 0 <= v <= 1 for v in kwargs.values())
			else 255,
		)

		# Determine if values are floats or integers
		if any(isinstance(v, float) and 0 <= v <= 1 for v in [r, g, b, a]):
			self._from_rgba_float(r, g, b, a)
		else:
			self._from_rgba_int(r, g, b, a)

	def _clamp_int(self, value: int) -> int:
		"""Clamp integer value to 0-255 range."""
		return max(0, min(255, int(value)))

	def _float_to_int(self, value: float) -> int:
		"""Convert float (0.0-1.0) to integer (0-255)."""
		return self._clamp_int(round(value * 255))

	@property
	def rgb(self) -> tuple[int, int, int]:
		"""Get RGB values as integers (0-255)."""
		return (self.r, self.g, self.b)

	@property
	def rgba(self) -> tuple[int, int, int, int]:
		"""Get RGBA values as integers (0-255)."""
		return (self.r, self.g, self.b, self.a)

	@property
	def rgb_float(self) -> tuple[float, float, float]:
		"""Get RGB values as floats (0.0-1.0)."""
		return (self.r / 255.0, self.g / 255.0, self.b / 255.0)

	@property
	def rgba_float(self) -> tuple[float, float, float, float]:
		"""Get RGBA values as floats (0.0-1.0)."""
		return (self.r / 255.0, self.g / 255.0, self.b / 255.0, self.a / 255.0)

	def to_hex(self, include_alpha: bool = False) -> str:
		"""Convert to hex string."""
		if include_alpha:
			return f"#{self.r:02X}{self.g:02X}{self.b:02X}{self.a:02X}"
		else:
			return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

	def to_list(self, include_alpha: bool = True) -> list[int]:
		"""Convert to list of integers."""
		if include_alpha:
			return [self.r, self.g, self.b, self.a]
		else:
			return [self.r, self.g, self.b]

	def to_dict(self, include_alpha: bool = True) -> dict:
		"""Convert to dictionary."""
		result = {"r": self.r, "g": self.g, "b": self.b}
		if include_alpha:
			result["a"] = self.a
		return result

	def with_alpha(self, alpha: Union[int, float]) -> "Color":
		"""Return a new color with different alpha value."""
		new_color = Color(self.r, self.g, self.b, self.a)
		if isinstance(alpha, float):
			new_color.a = new_color._float_to_int(alpha)
		else:
			new_color.a = new_color._clamp_int(alpha)
		return new_color

	def lighten(self, factor: float = 0.1) -> "Color":
		"""Return a lighter version of this color."""
		factor = max(0.0, min(1.0, factor))
		return Color(
			min(255, int(self.r + (255 - self.r) * factor)),
			min(255, int(self.g + (255 - self.g) * factor)),
			min(255, int(self.b + (255 - self.b) * factor)),
			self.a,
		)

	def darken(self, factor: float = 0.1) -> "Color":
		"""Return a darker version of this color."""
		factor = max(0.0, min(1.0, factor))
		return Color(
			int(self.r * (1 - factor)),
			int(self.g * (1 - factor)),
			int(self.b * (1 - factor)),
			self.a,
		)

	@classmethod
	def from_name(cls, name: str) -> "Color":
		"""Create color from name."""
		return cls(name)

	@classmethod
	def from_hex(cls, hex_string: str) -> "Color":
		"""Create color from hex string."""
		return cls(hex_string)

	@classmethod
	def from_rgb(cls, r: int, g: int, b: int) -> "Color":
		"""Create color from RGB integers."""
		return cls(r, g, b)

	@classmethod
	def from_rgba(cls, r: int, g: int, b: int, a: int) -> "Color":
		"""Create color from RGBA integers."""
		return cls(r, g, b, a)

	@classmethod
	def from_rgb_float(cls, r: float, g: float, b: float) -> "Color":
		"""Create color from RGB floats."""
		return cls(r=r, g=g, b=b)

	@classmethod
	def from_rgba_float(cls, r: float, g: float, b: float, a: float) -> "Color":
		"""Create color from RGBA floats."""
		return cls(r=r, g=g, b=b, a=a)

	@classmethod
	def random(cls) -> "Color":
		"""Create a random color from predefined colors (excluding transparent and grey)."""
		# Get all color names except 'transparent' and 'grey'
		available_colors = [
			name
			for name in cls.COLORS.keys()
			if name not in ["transparent", "grey", "gray", "silver", "white", "black"]
		]
		random_color_name = random.choice(available_colors)
		return cls(random_color_name)

	# Comparison operations
	def __eq__(self, other) -> bool:
		"""Check equality with another color."""
		if not isinstance(other, Color):
			return False
		return self.rgba == other.rgba

	def __ne__(self, other) -> bool:
		"""Check inequality with another color."""
		return not self.__eq__(other)

	# String representations
	def __str__(self) -> str:
		"""Simple string representation."""
		return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"

	def __repr__(self) -> str:
		"""Detailed string representation."""
		return f"Color({self.r}, {self.g}, {self.b}, {self.a})"

	# Hash support
	def __hash__(self) -> int:
		"""Hash support for colors."""
		return hash(self.rgba)

	# Container operations
	def __getitem__(self, index: int) -> int:
		"""Get component by index (0=r, 1=g, 2=b, 3=a)."""
		if index == 0:
			return self.r
		elif index == 1:
			return self.g
		elif index == 2:
			return self.b
		elif index == 3:
			return self.a
		else:
			raise IndexError("Color index out of range")

	def __setitem__(self, index: int, value: int):
		"""Set component by index (0=r, 1=g, 2=b, 3=a)."""
		value = self._clamp_int(value)
		if index == 0:
			self.r = value
		elif index == 1:
			self.g = value
		elif index == 2:
			self.b = value
		elif index == 3:
			self.a = value
		else:
			raise IndexError("Color index out of range")

	def __len__(self) -> int:
		"""Return number of components (always 4 for RGBA)."""
		return 4

	def __iter__(self) -> Iterator[int]:
		"""Iterate over RGBA components."""
		yield self.r
		yield self.g
		yield self.b
		yield self.a
