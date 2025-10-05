from .types import Coordinate, Arc  # noqa: F401


def polygon_centroid(coordinates: list[Coordinate]) -> Coordinate:
	"""Calculate the centroid (center of mass) of a polygon given as a list of Coordinate objects.

	Uses the standard polygon centroid formula which accounts for the area distribution.
	For simple geometric center (average of vertices), use `polygon_geometric_center()` instead.

	Args:
		coordinates: List of Coordinate objects defining the polygon vertices.
		             The polygon is automatically closed if needed.

	Returns:
		Coordinate: The centroid point of the polygon

	Raises:
		ValueError: If less than 3 coordinates are provided
		ValueError: If all coordinates are collinear (zero area)
	"""
	if len(coordinates) < 3:
		raise ValueError("Polygon must have at least 3 vertices")

	# Ensure all coordinates are 2D for area calculation
	coords_2d = [coord.to_2d() for coord in coordinates]

	# Close the polygon if it's not already closed
	if not coords_2d[0].is_close(coords_2d[-1]):
		coords_2d.append(coords_2d[0])

	# Calculate area and centroid using the shoelace formula
	area = 0.0
	centroid_x = 0.0
	centroid_y = 0.0

	for i in range(len(coords_2d) - 1):
		x_i, y_i = coords_2d[i].x, coords_2d[i].y
		x_j, y_j = coords_2d[i + 1].x, coords_2d[i + 1].y

		# Shoelace formula components
		cross_product = x_i * y_j - x_j * y_i
		area += cross_product
		centroid_x += (x_i + x_j) * cross_product
		centroid_y += (y_i + y_j) * cross_product

	area = area / 2.0

	if abs(area) < 1e-10:
		raise ValueError("Polygon has zero area (vertices are collinear)")

	centroid_x = centroid_x / (6.0 * area)
	centroid_y = centroid_y / (6.0 * area)

	# Determine if result should be 2D or 3D based on input
	has_3d = any(coord.is_3d for coord in coordinates)
	if has_3d:
		# Calculate average Z coordinate for 3D result
		z_sum = sum(coord.z or 0 for coord in coordinates)
		avg_z = z_sum / len(coordinates)
		return Coordinate(centroid_x, centroid_y, avg_z)
	else:
		return Coordinate(centroid_x, centroid_y)


def polygon_geometric_center(coordinates: list[Coordinate]) -> Coordinate:
	"""Calculate the geometric center (average position) of polygon vertices.

	This is the simple average of all vertex positions, which may not be
	the same as the area-weighted centroid for irregular polygons.

	Args:
		coordinates: List of Coordinate objects defining the polygon vertices

	Returns:
		Coordinate: The geometric center point

	Raises:
		ValueError: If no coordinates are provided
	"""
	if not coordinates:
		raise ValueError("At least one coordinate is required")

	# Calculate average position
	x_sum = sum(coord.x for coord in coordinates)
	y_sum = sum(coord.y for coord in coordinates)

	avg_x = x_sum / len(coordinates)
	avg_y = y_sum / len(coordinates)

	# Handle 3D coordinates
	has_3d = any(coord.is_3d for coord in coordinates)
	if has_3d:
		z_sum = sum(coord.z or 0 for coord in coordinates)
		avg_z = z_sum / len(coordinates)
		return Coordinate(avg_x, avg_y, avg_z)
	else:
		return Coordinate(avg_x, avg_y)
