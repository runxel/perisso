# Implementation of special classes for moving and placing elements
from perisso import Vector, Coordinate


# Create vectors
vect_2d = Vector(1, 2)
vect_3d = Vector(1, 2, 3.4)


# Create coordinates
p1 = Coordinate(1, 2.2)  # 2D point
p2 = Coordinate(3, 4, 5)  # 3D point

# Spatial operations
dist = p1.distance_to(p2)  # Distance between points
mid = p1.midpoint_to(p2)  # Midpoint

# Vector operations
vec = p1.vector_to(p2)  # Vector from p1 to p2
p3 = p1.translate(vec)  # Move p1 by vector

# Coordinate arithmetic
p4 = p1 + Vector(5, 5)  # Translate by vector
vec2 = p2 - p1  # Vector between coordinates
