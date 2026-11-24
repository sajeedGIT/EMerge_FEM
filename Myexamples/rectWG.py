import emerge as em
from emerge.plot import plot_sp, plot

model = em.Simulation("rectWG")

a = 22.86e-3
b = 10.16e-3
l = 100e-3

f1 = 20e9
f2 = 21e9
fo = 20.5e9

RCT = em.geo.Box(a, l, b)
model.commit_geometry()
model.view()
model.mw.set_frequency_range(f1, f2, 21)
model.generate_mesh()

model.view(plot_mesh=True)

port1 = model.mw.bc.RectangularWaveguide(RCT.front,2,mode=(3,0),mode_type="TE")
port2 = model.mw.bc.RectangularWaveguide(RCT.back,1,mode=(3,0),mode_type="TE")

model.adaptive_mesh_refinement(frequency=fo)
data = model.mw.run_sweep()

S11 = data.scalar.grid.S(1, 1)
S21 = data.scalar.grid.S(2, 1)

plot_sp(data.scalar.grid.freq, [S11, S21], labels=['S11', 'S21'], dblim=[-80, 3])
beta = data.scalar.grid.beta

plot(data.scalar.grid.freq, [beta])

field = data.field.find(freq=fo)
display = model.display
display.populate()
display.cbar('Emag').animate().add_field(field.grid(N=20000).scalar('Emag','complex'),symmetrize=False)
display.show()