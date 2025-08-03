from typing import Union, Iterator, Tuple
import math


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
		from .vector import Vector

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
		from .vector import Vector

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
