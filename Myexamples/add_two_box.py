import emerge as em

simulation = em.Simulation('MyFirstModel')
box1 = em.geo.Box(1, 1, 1)
box2 = em.geo.Box(1, 1, 1, position=(0.5, 0.5, 0.5))    # Position the second box next to the first
#my_union = em.geo.add(box1, box2)  # Create a union of the two boxes
#my_subtraction = em.geo.subtract(box1, box2)  # Subtract box2 from box1
#my_intersection = em.geo.intersect(box1, box2)  # Create an intersection of the two boxes
my_unification = em.geo.unite(box1, box2)  # Unify the two boxes into a single geometry
view = simulation.view()