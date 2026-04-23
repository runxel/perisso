import math
from typing import Union

from .ptypes import Coordinate, Polyline, Polygon


def polygon_centroid(shape: Union[Polyline, Polygon]) -> Coordinate:
	"""Calculate the area-weighted centroid of a Polyline or Polygon.

	Uses the shoelace formula on the outline vertices and adds circular-segment
	corrections for any arc edges, so curved outlines yield the correct center
	of mass (not just the polygon-of-vertices approximation).

	For a Polygon, only the outline is used — holes are ignored.
	A Polyline is treated as closed: if the last vertex does not match the
	first, it is closed implicitly.

	Arc convention follows Archicad: ``arcAngle > 0`` bulges to the right of
	the direction ``begIndex -> endIndex``; ``arcAngle < 0`` to the left.

	Args:
		shape: A Polyline or Polygon describing the boundary.

	Returns:
		Coordinate: The area-weighted centroid.

	Raises:
		TypeError: If ``shape`` is not a Polyline or Polygon.
		ValueError: If the outline has fewer than 3 vertices or zero net area.
	"""
	if isinstance(shape, Polygon):
		outline = shape.outline
	elif isinstance(shape, Polyline):
		outline = shape
	else:
		raise TypeError(
			f"polygon_centroid requires a Polyline or Polygon, got {type(shape).__name__}"
		)

	source_coords = outline.coordinates
	if len(source_coords) < 3:
		raise ValueError("Polygon must have at least 3 vertices")

	# Work in 2D and ensure the ring is closed for the shoelace loop.
	coords = [c.to_2d() for c in source_coords]
	if not coords[0].is_close(coords[-1]):
		coords.append(coords[0])

	# Shoelace area and first moments over the chord polygon.
	# area2 = 2A;  mom_x_raw = 6*A*Cx;  mom_y_raw = 6*A*Cy.
	area2 = 0.0
	mom_x_raw = 0.0
	mom_y_raw = 0.0
	for i in range(len(coords) - 1):
		xi, yi = coords[i].x, coords[i].y
		xj, yj = coords[i + 1].x, coords[i + 1].y
		cross = xi * yj - xj * yi
		area2 += cross
		mom_x_raw += (xi + xj) * cross
		mom_y_raw += (yi + yj) * cross

	area = area2 / 2.0
	mom_x = mom_x_raw / 6.0
	mom_y = mom_y_raw / 6.0

	# Arc corrections: each arc replaces a chord with a circular arc, so we
	# add the signed circular-segment area and its first-moment contribution.
	for arc_def in outline.arcs:
		theta = float(arc_def["arcAngle"])
		if abs(theta) < 1e-12:
			continue

		a = coords[arc_def["begIndex"]]
		b = coords[arc_def["endIndex"]]
		dx, dy = b.x - a.x, b.y - a.y
		chord = math.hypot(dx, dy)
		if chord < 1e-12:
			continue

		abs_theta = abs(theta)
		half = abs_theta / 2.0
		sin_half = math.sin(half)
		if sin_half < 1e-12:
			continue

		r = chord / (2.0 * sin_half)
		seg_area_mag = r * r * (abs_theta - math.sin(abs_theta)) / 2.0

		# Centroid of the segment: along the perpendicular bisector of the
		# chord, offset from the chord midpoint toward the arc side.
		denom = abs_theta - math.sin(abs_theta)
		d_from_center = (4.0 * r * sin_half ** 3) / (3.0 * denom)
		h_bar = d_from_center - r * math.cos(half)  # signed correctly for |theta| <> pi

		# Right-hand perpendicular unit vector of beg->end.
		rpx, rpy = dy / chord, -dx / chord
		sign = 1.0 if theta > 0 else -1.0
		nx, ny = sign * rpx, sign * rpy

		mid_x = (a.x + b.x) / 2.0
		mid_y = (a.y + b.y) / 2.0
		seg_cx = mid_x + nx * h_bar
		seg_cy = mid_y + ny * h_bar

		seg_area_signed = sign * seg_area_mag
		area += seg_area_signed
		mom_x += seg_area_signed * seg_cx
		mom_y += seg_area_signed * seg_cy

	if abs(area) < 1e-10:
		raise ValueError("Polygon has zero area (vertices are collinear)")

	cx = mom_x / area
	cy = mom_y / area

	# Preserve 3D if the input was 3D.
	zs = [c.z for c in source_coords if c.is_3d]
	if zs:
		return Coordinate(cx, cy, sum(zs) / len(zs))
	return Coordinate(cx, cy)


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


def detect_circle(
	shape: Polyline,
	tolerance: float = 0.01,
) -> tuple[bool, Coordinate | None, float | None]:
	"""Detect whether a Polyline approximates a circle.

	DWG imports often represent circles as many-vertex polylines instead of
	true arcs. This checks the shape by taking the area-weighted centroid
	as the candidate center and measuring how uniform the vertex distances
	to that center are. If the worst-case relative deviation stays within
	``tolerance``, the shape is classified as a circle.

	Args:
		shape: The Polyline to test.
		tolerance: Maximum allowed relative deviation of any vertex radius
			from the mean radius, i.e. ``max(|r_i - r_mean|) / r_mean``.
			Defaults to 0.01 (1%).

	Returns:
		Tuple ``(is_circle, center, radius)``. If no circle is detected,
		``center`` and ``radius`` are ``None``.

	Raises:
		TypeError: If ``shape`` is not a Polyline.
	"""
	if not isinstance(shape, Polyline):
		raise TypeError(
			f"detect_circle requires a Polyline, got {type(shape).__name__}"
		)

	coords = shape.coordinates
	# Drop an explicit closing duplicate so it doesn't skew the mean radius.
	if len(coords) >= 2 and coords[0].is_close(coords[-1]):
		coords = coords[:-1]

	if len(coords) < 3:
		return (False, None, None)

	try:
		center = polygon_centroid(shape)
	except ValueError:
		return (False, None, None)

	center_2d = center.to_2d()
	radii = [c.to_2d().distance_to(center_2d) for c in coords]
	mean_radius = sum(radii) / len(radii)

	if mean_radius <= 0.0:
		return (False, None, None)

	max_dev = max(abs(r - mean_radius) for r in radii)
	if max_dev / mean_radius > tolerance:
		return (False, None, None)

	return (True, center, mean_radius)
