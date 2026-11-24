import emerge as em
from emerge.plot import plot_sp, plot_vswr,plot

model = em.Simulation("Rectangular Waveguide")

a= 22.86e-3 # width of the rectangular wavguide
b= 10.16e-3 # height of the rectangular waveguide
l= 50.00e-3 # length
f1= 8e9
f2= 12e9
f0= 10e9

box = em.geo.Box(a, l, b)
model.commit_geometry()
model.mw.set_frequency_range(f1, f2, 21)
model.generate_mesh()   
model.view()

port1 = model.mw.bc.ModalPort(box.front, 1, modetype='TE')
port2 = model.mw.bc.ModalPort(box.back, 2, modetype='TE')

data = model.mw.run_sweep()

freqs = data.scalar.grid.freq
S11 = data.scalar.grid.S(1, 1)
S21 = data.scalar.grid.S(2, 1)
beta = data.scalar.grid.beta

plot_sp(freqs,[S11,S21], labels=["S11","S21"], dblim=[-80,3])
plot(freqs,beta)

field = data.field.find(freq=f0)
display = model.display
display.populate()
display.cbar('Hmag').animate().add_field(field.grid(N=20000).scalar('Hmag','complex'),symmetrize=False)
display.show()
