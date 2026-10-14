## -------------------------------------------------------------------------
# Cylindrical Waveguide Simulation using EMerge
#
# This script models a circular metallic waveguide and performs:
#   • Electromagnetic analysis of the dominant TE11 mode
#   • S-parameter extraction (S11 and S21)
#   • Broadband frequency sweep
#   • Electric field visualization inside the waveguide
#
# Waveguide Parameters:
#   Radius (a)          : 8.74 mm
#   Length (l)          : 100 mm
#   Dominant Mode       : TE11
#   Cut-off Frequency   : fc ≈ 10.057 GHz
#
# Simulation Frequency Range:
#   11.60 GHz – 15.90 GHz
#   (Operating above cut-off frequency to ensure wave propagation)
#
# Expected Results:
#   • Low reflection coefficient (S11 << 0 dB)
#   • Near-unity transmission (S21 ≈ 0 dB)
#   • Proper TE11 field distribution inside the circular waveguide
#
# Implemented by:
# Dr. Sajeed S. Mulla
# Associate Professor,
# Department of Electronics and Telecommunication Engineering,
# Dnyanshree Institute of Engineering and Technology, Satara,
# Maharashtra, India.
# -------------------------------------------------------------------------
import emerge as em
from emerge.plot import plot_sp,plot

model = em.Simulation('Cylindrical Waveguide')

mm = 1e-3
a = 8.74*mm # Radious of the wave guide
l=100*mm # length of the waveguide
cyl = em.geo.Cylinder(radius=a,height=l,Nsections=20)
model.commit_geometry()
model.view()

model.mw.set_frequency_range(11.60e9,15.90e9,21)
model.generate_mesh()
model.view(plot_mesh=True)

port1 = model.mw.bc.ModalPort(cyl.front,1,modetype='TE',number_of_modes=1)
port2 = model.mw.bc.ModalPort(cyl.back,2,modetype='TE',number_of_modes=1)

data = model.mw.run_sweep()
grid = data.scalar.grid

S11 = grid.S(1,1)
S21 = grid.S(2,1)
freq = grid.freq

freq_dense = grid.dense_f(2001)
S11_fit = grid.model_S(1,1,freq=freq_dense)
S21_fit = grid.model_S(2,1,freq=freq_dense)
plot_sp(freq_dense,[S11_fit,S21_fit],labels=['S11','S21'],dblim=[-80,6])
beta = grid.beta[:,0]
plot(freq/1e9, beta, xlabel='Frequency (GHz)', ylabel='β(rad/m)')
field = data.field.find(freq=12e9)
F = field.grid(N=20000)
E = F.scalar(field='Emag',metric='complex')

display = model.display
display.populate()
display.cbar('E').animate().add_field(E,symmetrize=False)
display.show()


