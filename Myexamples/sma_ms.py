import emerge as em
import numpy as np
from emerge.plot import plot_sp
mm = 0.001

sim = em.Simulation("SMACONNECTOR")

# air above the board only, so it does not overlap the PCB
air = em.geo.Box(50*mm, 50*mm, 6.0*1.59*mm, (-25*mm, 0, 0)).set_material(em.lib.AIR)
pcb = em.geo.Box(50*mm, 50*mm, 1.59*mm, (-25*mm, 0, -1.59*mm)).set_material(em.lib.DIEL_FR4)
gnd = em.geo.XYPlate(50*mm, 50*mm, (-25*mm, 0, -1.59*mm)).set_material(em.lib.COPPER)
ms  = em.geo.XYPlate(3*mm, 50*mm, (-1.5*mm, 0, 0)).set_material(em.lib.COPPER)

# FIX 1: give the connector length in metres, consistent with the rest
port1 = em.macro.SMAConnector(1.59*mm, (-em.YAX).construct_cs(0, 0, 0), 15)
port2 = em.macro.SMAConnector(1.59*mm, (em.YAX).construct_cs(0, 50*mm, 0), 15)

sim.commit_geometry()
sim.view()

sim.mw.bc.ModalPort(port1.port_face, 1, modetype="TEM")
sim.mw.bc.ModalPort(port2.port_face, 2, modetype="TEM")

# FIX 2: open boundary on the air box (adapt the face selection to your API)
sim.mw.bc.AbsorbingBoundary(air.boundary(exclude=[pcb, gnd]))

sim.mw.set_frequency_range(800e6, 1e9, 21)
# FIX 4: refine before meshing (name from memory)
sim.mw.set_resolution(0.2)
sim.generate_mesh()
sim.view(plot_mesh=True)

sim.adaptive_mesh_refinement(frequency=900e6)
data = sim.mw.run_sweep()

S11 = data.scalar.grid.S(1, 1)
S21 = data.scalar.grid.S(2, 1)
freqs = data.scalar.grid.freq
plot_sp(freqs, [S11, S21], dblim=[-80, 3], labels=["S11", "S21"])