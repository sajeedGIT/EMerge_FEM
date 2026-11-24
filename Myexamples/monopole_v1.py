import emerge as em
import numpy as np
from emerge.plot import plot, plot_ff, plot_ff_polar, plot_sp, plot_vswr



monopole_height = 74e-3
monopole_radius = 1e-3

port_length = 0.5e-3
port_radius = 1e-3
port_width = 2e-3

model = em.Simulation("Monopole",loglevel='DEBUG')


air_sphere = em.geo.HalfSphere(radius=110e-3,direction=(0,0,1))

gnd = em.geo.Box(150e-3,150e-3,35e-6, (-75e-3,-75e-3,-35e-6))
monopole = em.geo.Cylinder(radius=monopole_radius,height=monopole_height,cs=em.cs(origin=(0,0,port_length)), name="monopole")
port = em.geo.Cylinder(monopole_radius,1e-3)
monopole.set_material(material=em.lib.COPPER)

gnd.set_material(material=em.lib.PEC)
model.view()

model.commit_geometry()
model.mw.set_frequency_range(0.8e9,1.2e9,21)
model.mw.set_resolution(0.2)

model.generate_mesh()
model.view(plot_mesh=True)

boundary_selection = air_sphere.boundary()
abc = model.mw.bc.AbsorbingBoundary(boundary_selection)

port = model.mw.bc.LumpedPort(port.shell, 1, 2*3.14*monopole_radius, 1e-3, em.ZAX, Z0=36.5) 
model.adaptive_mesh_refinement(frequency=1e9)
data = model.mw.run_sweep()
g = data.scalar.grid
S11 = g.S(1,1)
freq_dense = g.dense_f(2001)
S11_fit = g.model_S(1,1,freq_dense) 
Zin = 50*(1 + S11_fit)/(1-S11_fit)
plot_sp(freq_dense,[S11_fit],labels="S11", dblim=[-40, 5])
plot_vswr(freq_dense,[S11_fit],labels="VSWR", swrlim=[1,5])
plot(freq_dense,[Zin], labels="Z")

ff_xz = data.field.find(freq=1e9).farfield_2d(em.ZAX,em.YAX,boundary_selection)
ff_yz = data.field.find(freq=1e9).farfield_2d(em.ZAX,em.XAX,boundary_selection)
ff_xy = data.field.find(freq=1e9).farfield_2d(em.XAX,em.ZAX,boundary_selection)
plot_ff_polar(ff_xz.ang,ff_xz.gain.norm, dB=True)
plot_ff_polar(ff_yz.ang,ff_yz.gain.norm,dB=True)
plot_ff_polar(ff_xy.ang,ff_xy.gain.norm,dB=True)

model.display.add_object(air_sphere)
model.display.add_object(monopole)

ff3d = data.field.find(freq=1e9).farfield_3d(boundary_selection)
model.display.add_farfield3d(ff3d,dB=True,rmax=70e-3, offset=(0,0,0), opacity=0.5)
model.display.show()

