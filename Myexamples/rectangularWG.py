import emerge as em
import numpy as np
from emerge.plot import plot_sp,plot

mm = 1e-3
a = 22.86*mm
b = 10.16*mm
l = 100*mm
r = 23.83*mm
#model = em.Simulation('Rectangular Waveguide')
model = em.Simulation("Circular Waveguide")

#box = em.geo.Box(a,l,b)
cyl = em.geo.Cylinder(r,l)
model.commit_geometry()
model.view()

model.mw.set_frequency_range(8.5e9,11.5e9,21)
model.generate_mesh()
model.view(plot_mesh=True)

port1 = model.mw.bc.ModalPort(cyl.front,1,modetype="TE",number_of_modes=1)
port2 = model.mw.bc.ModalPort(cyl.back,2,modetype="TE",number_of_modes=1)


data = model.mw.run_sweep()
grid = data.scalar.grid

S11 = grid.S(1,1)
S21 = grid.S(2,1)
beta = grid.beta
freq = grid.freq

plot_sp(freq,[S11,S21],labels=["S11","S21"],dblim=[-60,4])

field = data.field.find(freq=10e9)
plot(freq/1e9, beta, xlabel='Frequency (GHz)', ylabel='β(rad/m)')
field = data.field.find(freq=12e9)
F = field.grid(N=20000)
E = F.scalar(field='Emag',metric='complex')

display = model.display
display.populate()
display.cbar('E').animate().add_field(E,symmetrize=False)
display.show()