import emerge as em
import numpy as np
from emerge.plot import plot_sp, smith, plot_ff, plot_ff_polar, plot

air_box_height = 200e-3
air_box_width = 150e-3
air_box_depth = 150e-3

antenna_length = 143e-3
antenna_radius = 1e-3

port_width = 2e-3
port_length = 1e-3

cut_port_length = 1e-3
cut_port_radius = 1e-3

model = em.Simulation("DipoleAntenna")

air_box = em.geo.Box(width=air_box_width, height=air_box_height, depth=air_box_depth, alignment=em.CENTER,  name="AirBox")
dipole = em.geo.Cylinder(radius=antenna_radius, height=antenna_length, cs=em.cs(origin=(0,0,-antenna_length/2)), name="Dipole")
port_cut = em.geo.Cylinder(radius=cut_port_radius, height=cut_port_length, cs=em.cs(origin=(0,0,-cut_port_length/2)), name="PortCut")
dipole = em.geo.subtract(dipole, port_cut)

port = em.geo.Plate((-1e-3,0,-0.5e-3),(2e-3,0,0),(0,0,1e-3), name="Port")
dipole.set_material(em.lib.PEC)
model.view()
#model.view(use_gmsh=True)
model.commit_geometry()
model.mw.set_frequency_range(0.8e9,1.2e9,21)

model.mw.set_resolution(0.2)
model.generate_mesh()
model.view(plot_mesh=True)

boundary_selection = air_box.boundary()
abc = model.mw.bc.AbsorbingBoundary(boundary_selection)
port = model.mw.bc.LumpedPort(port, 1, width=port_width, height=port_length, direction=(0,0,1),Z0=50.0)

data = model.mw.run_sweep()

g= data.scalar.grid
f = g.freq

S11 = g.S(1, 1)
#S11dB = 20 * np.log10(np.abs(S11))


plot_sp(f, [S11], labels=["S11"], dblim=[-40, 6])
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
ZL = 50 * (1 + S11_fit) / (1 - S11_fit)
plot_sp(fdense, [S11_fit], labels=["S11 Fit"], dblim=[-40, 6])
plot(fdense,[ZL],labels=["ZL"])
# # Add geometry for context
model.display.add_object(dipole)
model.display.add_object(air_box)
#
# # Compute full 3D far-field (at the same frequency) and display
ff3d = data.field.find(freq=1.0e9).farfield_3d(boundary_selection)
model.display.add_farfield3d(ff3d, dB='True', rmax=150e-3 / 2, offset=(0, 0, 0))
#
# # Show interactive 3D scene
model.display.show()

ff_xz = data.field.find(freq=1.0e9).farfield_2d(em.ZAX, em.YAX, boundary_selection)
ff_yz = data.field.find(freq=1.0e9).farfield_2d(em.ZAX, em.XAX, boundary_selection)
ff_xy = data.field.find(freq=1.0e9).farfield_2d(em.XAX, em.ZAX, boundary_selection)
plot_ff(ff_xz.ang * 180 / np.pi, [ff_xz.gain.norm, ff_yz.gain.norm], labels=['XZ Plane','YZ Plane'], dB=True, xlabel='Theta (deg)', ylabel="Gain [dBi]")
plot_ff_polar(ff_xz.ang, ff_yz.gain.norm, dB=True, dBfloor=-20)
plot_ff_polar(ff_xy.ang, ff_xy.gain.norm, dB=True, dBfloor=-20)