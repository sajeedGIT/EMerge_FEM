import emerge as em
from emerge.plot import plot_sp, plot_vswr, plot
import numpy as np

model  = em.Simulation ("rectangular waveguide")

a = 22.86e-3 # width of the rectangular wavguide
b = 10.16e-3 # height of the rectangular waveguide
l = 50.00e-3 # length

box = em.geo.Box(a,l,b)
model.commit_geometry()
model.mw.set_frequency_range(8e9 , 12e9 , 21)
model.generate_mesh()
model.view(plot_mesh = True)

port1 = model.mw.bc.ModalPort(box.front,1,modetype='TE')
port1 = model.mw.bc.ModalPort(box.back,2,modetype='TE')

model.adaptive_mesh_refinement(frequency=10e9)
data = model.mw.run_sweep()

freqs = data.scalar.grid.freq
S11 = data.scalar.grid.S(1, 1)
S21 = data.scalar.grid.S(2, 1)
beta = data.scalar.grid.beta

plot_sp(freqs, [S11, S21], labels=['S11', 'S21'], dblim=[-80,3])
plot(freqs, beta)

field = data.field.find(freq=9e9)
display = model.display
display.populate()
display.cbar('Emag').animate().add_field(field.grid(N=20000).scalar('Emag','complex'),symmetrize=False)
display.show()