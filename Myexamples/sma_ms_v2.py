import emerge as em
import numpy as np
from emerge.plot import plot_sp
mm = 0.001

m = 2*mm
sim = em.Simulation("SMACONNECTOR" )
air = em.geo.Box(50*mm,50*mm,6*1.59*mm,(-25*mm,0,-1.59*mm)).set_material(em.lib.AIR)
pcb = em.geo.Box(50*mm, 50*mm, 1.59*mm,(-25*mm,0, -1.59*mm)).set_material(em.lib.DIEL_FR4)
gnd = em.geo.Box(50*mm, 50*mm, 35e-6, (-25*mm,0, -(1.59*mm+35e-6))).set_material(em.lib.COPPER)
ms = em.geo.Box(3*mm,50*mm-2*m,35e-6, (-1.5*mm,m,0)).set_material(em.lib.COPPER)
port1 = em.macro.SMAConnector(1.59*mm,(-em.YAX).construct_cs(0,0,0),15)
port2 = em.macro.SMAConnector(1.59*mm,(-em.YAX).construct_cs(0,50*mm,0).rotate((em.ZAX), angle=180),15)
sim.commit_geometry()
sim.view()

sim.mw.bc.ModalPort(port1.port_face, 1,modetype="TEM")
sim.mw.bc.ModalPort(port2.port_face, 2,modetype="TEM")

sim.mw.set_frequency_range(1e9,2e9,21)
sim.generate_mesh()
sim.view(plot_mesh=True)

sim.adaptive_mesh_refinement(frequency=1.5e9)
data = sim.mw.run_sweep()

S11 = data.scalar.grid.S(1,1)
S21 = data.scalar.grid.S(2,1)
freqs = data.scalar.grid.freq

plot_sp(freqs,[S11,S21], dblim=[-90,3],labels=["S11","S21"])

field = data.field.find(freq=900e6)
display = sim.display
display.populate()
sim.display.animate().add_field(
    field.grid(N=100_000, z_range=(-1.59 * mm, 0)).scalar('Ez', 'complex'),
    symmetrize=True,
)
sim.display.show()