import emerge as em
from emerge.plot import plot_sp

"""PCB Vias

This demonstration shows how to add vias with the PCB router. Make sure to go through the other
PCB related demos (demo1 and demo3) to get more information on the PCBLayouter.

Notice that the results of this simulation are not supposed to be good. Its more about the geometry than the S-parameters.

"""

mm = 0.001  # Define a millimeter
th = 1.0  # mm

model = em.Simulation("StriplineWithVias")
model.check_version("3.0.0")  # Checks version compatibility.

# As usual we start by creating our layouter
pcb = em.geo.PCB(
    th, mm, em.GCS, layers=3, material=em.lib.DIEL_RO4350B, trace_material=em.lib.PEC
)

# Here we define a simple stripline path that makes a knick turn and a via jump to a new layer.
# None of the transmission lines are conciously matched in any way, this is just about the routing

# The .via(...) method allows one to add a via geometry to the PCBLayouter that can be extracted later
# A user may decide whether to proceed or not beyond the via. More information can be found in the
# docstring of the method. The vias can be created later.
w0 = pcb.calc.z0(50, 1, 0) * 0.9
w1 = pcb.calc.z0(50, 2, 0)
pcb.new(0, 0, w0, (1, 0), 1)["p1"].straight(10)\
    .turn(90,corner_type="champher")\
    .straight(10)\
    .turn(-90, corner_type="champher")\
    .straight(5)\
    .via(2, 0.2, True, width=w1)\
    .straight(8)\
    .via(1, 0.2, width=w0)\
    .straight(5)\
    .turn(-90, corner_type="champher")\
    .straight(10)\
    .turn(90)\
    .straight(10)["p2"]

# Notice the champher corner type. This champher minimizes reflections when going around the corner.

# As usual we compile the traces as a merger of polygons
trace = pcb.compile_paths(True)

# Now that we have via's defined, we can do the same with vias. I set Merge to True so that I get back
# One GeoObject.
vias = pcb.generate_vias(True)

# Here I use lumped ports instead of wave ports. I use the references made earlier to generate the port.
# By default, all lumped port sheets will be shorted to z=-thickness. You can change this as an optional
# argument.
lp1 = pcb.lumped_port(pcb["p1"], 1)
lp2 = pcb.lumped_port(pcb["p2"], 2)

# Because lumped ports don't stop at the edge of our domain, we make sure to add some margins everywhere.
pcb.determine_bounds(5, 5, 5, 5)

# Finally we can generate the PCB volumes. Because the trace start halfway through the PCB we turn
# on the split-z function which cuts the PCB in multiple layers. This improves meshing around the striplines.
diel = pcb.generate_pcb(True, merge=True)

# We also define the air-box with 3mm thickness
air = pcb.generate_air(3.0)

# Finish modelling by calling commit_geometry
model.commit_geometry()

model.view()
