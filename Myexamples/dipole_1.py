import numpy as np
import emerge as em
from emerge.plot import plot, plot_ff, plot_ff_polar, plot_sp, plot_vswr


air_box_height = 200e-3
air_box_width = 150e-3
air_box_breadth = 150e-3

dipole_height = 143e-3
dipole_radius = 1e-3

cut_port_length = 1e-3
cut_port_radius = 1e-3

port_length = 1e-3
port_width = 2e-3

model = em.Simulation("Dipole")
air_box = em.geo.Sphere(radius=100e-3)
#air_box = em.geo.Box(width=air_box_width,depth=air_box_breadth,height=air_box_height,alignment=em.CENTER,name="AirBox")
dipole = em.geo.Cylinder(radius=dipole_radius,height=dipole_height,cs=em.cs(origin=(0,0,-dipole_height/2)), name="Dipole")
port_cut = em.geo.Cylinder(radius=cut_port_radius,height=cut_port_length,cs=em.cs(origin=(0,0,-cut_port_length/2)))
dipole = em.geo.subtract(dipole,port_cut)

port = em.geo.Plate((0,-1e-3,-0.5e-3),(0,2e-3,0),(0,0,1e-3), name="port")

dipole.set_material(material=em.lib.COPPER)
model.view()
model.commit_geometry()
model.mw.set_frequency_range(0.8e9,1.2e9,21)
model.mw.set_resolution(0.2)
model.generate_mesh()
model.view(plot_mesh=True)

boundary_selection = air_box.boundary()
abc = model.mw.bc.AbsorbingBoundary(boundary_selection)
port = model.mw.bc.LumpedPort(face=port,port_number=1,width=port_width,height=port_length,direction=(0,0,1))

data = model.mw.run_sweep()
g = data.scalar.grid
freq = g.freq
S11 = g.S(1,1)

freq_dense = g.dense_f(2001)
S11_fit = g.model_S(1,1,freq_dense)
Z = 50*(1 + S11_fit)/(1-S11_fit)

plot_sp(freq_dense,[S11_fit],labels="S11", dblim=[-40, 5])
plot_vswr(freq_dense,[S11_fit],labels="VSWR", swrlim=[1,5])
plot(freq_dense,[Z], labels="Z")

ff_xz = data.field.find(freq=1e9).farfield_2d(em.ZAX,em.YAX,boundary_selection)
ff_yz = data.field.find(freq=1e9).farfield_2d(em.ZAX,em.XAX,boundary_selection)
ff_xy = data.field.find(freq=1e9).farfield_2d(em.XAX,em.ZAX,boundary_selection)
plot_ff_polar(ff_xz.ang,ff_xz.gain.norm, dB=True)
plot_ff_polar(ff_yz.ang,ff_yz.gain.norm,dB=True)
plot_ff_polar(ff_xy.ang,ff_xy.gain.norm,dB=True,rlim=(0,1.44))

model.display.add_object(air_box)
model.display.add_object(dipole)

ff3d = data.field.find(freq=1e9).farfield_3d(boundary_selection)
model.display.add_farfield3d(ff3d,dB=True,rmax=75e-3, offset=(0,0,0), opacity=0.5)
model.display.show()