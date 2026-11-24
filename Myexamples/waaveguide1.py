import emerge as em
from emerge.plot import plot_sp, plot_vswr,plot

model = em.Simulation("Rectangular Waveguide")

a = 22.86e-3 # width of the rectangular wavguide
b = 10.16e-3 # height of the rectangular waveguide
l = 50.00e-3 # length

f1 = 4e9
f2 = 12e9
f0 = 10e9

WG = em.geo.Box(a, l, b)
model.commit_geometry()
model.mw.set_frequency_range(f1, f2, 21)
model.generate_mesh()
model.view(face_labels=True, plot_mesh=True)

port1 = model.mw.bc.ModalPort(WG.front, 2, modetype='TE')
port2 = model.mw.bc.ModalPort(WG.back, 1, modetype='TE')

model.adaptive_mesh_refinement(frequency=f0)

data = model.mw.run_sweep()

freqs = data.scalar.grid.freq
S11 = data.scalar.grid.S(1, 1)
S21 = data.scalar.grid.S(2, 1)
beta = data.scalar.grid.beta

plot_sp(freqs, [S11, S21], labels=['S11', 'S21'], dblim=[-80, 3])
plot(freqs,beta)

field = data.field.find(freq=9e9)
display = model.display
display.populate()
display.cbar('Emag').animate().add_field(field.grid(N=20000).scalar('Emag','complex'),symmetrize=False)
display.show()
