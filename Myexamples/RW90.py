import emerge as em
import numpy as np
from emerge.plot import plot_sp

mm = 1e-3
a = 22.86*mm
b = 10.16*mm
l = 100*mm

model = em.Simulation('RW90')

box = em.geo.Box(a,l,b)

model.commit_geometry()
model.view()

model.mw.set_frequency_range(8e9,15e9,21)
model.generate_mesh()
model.view(plot_mesh=True)

port1 = model.mw.bc.ModalPort(box.front,1,modetype='TE',number_of_modes=1)
port1 = model.mw.bc.ModalPort(box.back,2,modetype='TE',number_of_modes=1)

data = model.mw.run_sweep()
grid = data.scalar.grid
S11 = grid.S(1,1)
S21 = grid.S(1,1)
fdense = grid.dense_f(2001)
S11_fit = grid.model_S(1,1,freq=fdense)
S21_fit = grid.model_S(2,1,freq=fdense)
plot_sp(fdense,[S11_fit,S21_fit],labels=['S11','S21'], dblim=[-80, 6])

field = data.field.find(freq=10e9)
F = field.grid(N=20000)
Eanim = F.Ex**2 + F.Ey**2 + F.Ez**2
display = model.display
display.populate()
display.cbar('Eqs').animate().add_cloud(F.x, F.y, F.z, Eanim, symmetrize=True)
display.show()