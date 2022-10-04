# To show index of mesh.points
# [Draft.make_text([f"{point.Index + 1}"], placement=point.Vector) for point in mesh.Points]

# To show index of mesh.Facets
# [Draft.make_text([f"{face.Index + 1}"], placement=face.InCircle[0]) for face in mesh.Facets]

# To show all Boundaries
# [Draft.make_text([f"{face.Index + 1}"], placement=face.InCircle[0]) for face in mesh.Facets if 4294967295 in face.NeighbourIndices]

# To get label of selection
# [element.Label for element in Gui.Selection.getCompleteSelection()]

EPSILON_0 = 8.8541878176e-12

MAP_INDICES = {
    1: 2,
    2: 3,
    3: 1
}
