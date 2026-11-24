
"""
50-ohm microstrip line on FR4 using EMerge 2.8

Substrate : h = 1.59 mm, er = 4.4, tan(delta) = 0.02
Copper    : 35 um
Frequency : 1-6 GHz
Animation : E-field at 3 GHz

Outputs:
    microstrip_S.png
    3D animated E-field visualization
"""

import numpy as np
from emerge.plot import plot_sp
import emerge as em

# ---------------------------------------------------------
# 1. Design parameters
# ---------------------------------------------------------
f1 = 1e9
f0 = 3e9
f2 = 5e9
mm = 1e-3
Z0_target = 50.0
er = 4.4
tand = 0.02

h_mm = 1.59
t_cu_mm = 0.035
sigma_cu = 5.8e7

L_mm = 60.0
# ---------------------------------------------------------
# 2. Calculate microstrip width
#    Hammerstad approximation
# ---------------------------------------------------------

def microstrip_width(Z0, er, h):
    A = (
        Z0 / 60 * np.sqrt((er + 1) / 2)
        + (er - 1) / (er + 1)
        * (0.23 + 0.11 / er)
    )

    wh = 8 * np.exp(A) / (np.exp(2 * A) - 2)

    if wh > 2:
        B = 377 * np.pi / (2 * Z0 * np.sqrt(er))

        wh = (2 / np.pi) * (
            B - 1 - np.log(2 * B - 1)
            + (er - 1) / (2 * er)
            * (np.log(B - 1) + 0.39 - 0.61 / er)
        )

    return wh * h


W_mm = microstrip_width(Z0_target, er, h_mm)

eeff = (
    (er + 1) / 2
    + (er - 1) / 2
    / np.sqrt(1 + 12 * h_mm / W_mm)
)

print(f"Trace width = {W_mm:.3f} mm")
print(f"Effective permittivity = {eeff:.3f}")

# ---------------------------------------------------------
# 3. Create simulation and PCB
# ---------------------------------------------------------

model = em.Simulation("Microstrip_FR4")

pcb = em.geo.PCB(h_mm, unit=mm, material=em.lib.DIEL_FR4, trace_material=em.lib.PEC)
pcb.new(0, 0, W_mm, (1, 0), 1)[1].straight(L_mm )[2]
trace = pcb.compile_paths(True)
pcb.determine_bounds(leftmargin=0, rightmargin=0, topmargin=25, bottommargin=25)



diel = pcb.generate_pcb(merge=True)
air = pcb.generate_air(5)

model.view()
P1 = pcb.modal_port(1,1,height=5, width=W_mm+5)
P2 = pcb.modal_port(2,2,height=5, width=W_mm+5)


model.mw.set_resolution(0.2)

model.mw.set_frequency_range(f1, f2, 21)

# Set the overall mesh resolution as a fraction of the wavelength.

model.generate_mesh()
model.view(plot_mesh=True)



model.adaptive_mesh_refinement(frequency=3e9)
data = model.mw.run_sweep()

S11 = data.scalar.grid.S(1, 1)
S21 = data.scalar.grid.S(2, 1)
freq = data.scalar.grid.freq
freq_dense = data.scalar.grid.dense_f(2001)
S11_fit = data.scalar.grid.model_S(1,1,freq_dense)
S21_fit = data.scalar.grid.model_S(2,1,freq_dense)

plot_sp(freq_dense, [S11_fit, S21_fit], labels=['S11', 'S21'],dblim=[-40, 3])
field = data.field.find(freq=f0)
F = field.grid(N=20000).vector(field='E',metric='complex')

model.display.add_object(diel)
model.display.add_object(trace)
model.display.cbar("E").animate().add_field(F,vector_type='vector')
#model.display.cbar("Eqs").animate().add_cloud(F.x, F.y, F.z, Eanim, symmetrize=True)
model.display.show()