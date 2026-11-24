import emerge as em
from emerge.plot import plot_sp, plot


model = em.Simulation("RW90")

mm = 1e-3
GHz = 1e9
a = 22.86*mm
b = 10.16*mm
l = 50*mm

f1 = 8*GHz
f0 = 10*GHz
f2= 12*GHz

RWG = em.geo.Box(a,l,b)
model.commit_geometry()
model.view()

model.mw.set_frequency_range(f1,f2,21)
model.generate_mesh()
model.view(plot_mesh=True)

port1 = model.mw.bc.RectangularWaveguide(RWG.front,1,mode=(1,0),mode_type="TE")
port2 = model.mw.bc.RectangularWaveguide(RWG.back,2,mode=(1,0),mode_type="TE")

data = model.mw.run_sweep()

freq = data.scalar.grid.freq
S11 = data.scalar.grid.S(1,1)
S21 = data.scalar.grid.S(2,1)
beta = data.scalar.grid.beta

plot_sp(freq, [S11, S21], dblim=[-70,3],labels=["S11","S21"])
plot(freq, beta)

field = data.field.find(freq=f0).grid(N=2000).vector('E','complex')
display = model.display
display.populate()
display.cbar('E').animate().add_field(field,symmetrize=False)
display.show()


