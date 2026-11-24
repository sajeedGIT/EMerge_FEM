import emerge as em
from emerge.plot import plot_sp,plot

WG = em.Simulation("Rectangular Waveguide")

a = 22.86e-3 # width of the rectangular wavguide
b = 10.16e-3 # height of the rectangular waveguide
l = 100.00e-3 # length

def cutoff_frequency(a,b,mode=(1,0)):
    m,n = mode
    return (3e8/2)*((m/a)**2+(n/b)**2)**0.5

m=0
n=1
fc = cutoff_frequency(a,b,mode=(m,n))
f1 = fc*1.1
f2 = fc*1.5
f0 = f2*0.5
RECT = em.geo.Box(a, l, b)


WG.commit_geometry()
WG.mw.set_frequency_range(f1, f2, 21)
WG.generate_mesh()
WG.view(plot_mesh=True)

port1 = WG.mw.bc.RectangularWaveguide(RECT.front,1,mode=(m,n),mode_type="TE")
port2 = WG.mw.bc.RectangularWaveguide(RECT.back,2,mode=(m,n),mode_type="TE")

data = WG.mw.run_sweep()

freqs = data.scalar.grid.freq
S11 = data.scalar.grid.S(1, 1)
S21 = data.scalar.grid.S(2, 1)
beta = data.scalar.grid.beta

plot_sp(freqs,[S11,S21], labels=["S11","S21"], dblim=[-70,3],xunit="GHz",filename="Rect_S11")
plot(freqs,beta)


field = data.field.find(freq=f0).grid(N=20000).scalar("Ex","complex")
display = WG.display
display.populate()
display.cbar('E').animate().add_field(field,symmetrize=True)
display.show()