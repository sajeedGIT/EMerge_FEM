#slot antenna 
import emerge as em
import numpy as np
from emerge.plot import plot_sp, smith, plot_ff, plot_ff_polar, plot_vswr, plot

mm = 0.001  # meters per millimeter
GHz = 1e9

f1 = 3.1*GHz  # start frequency
f2 = 3.50*GHz  # stop frequency
f0 = 3.3*GHz  # center frequency

L_slot_1 = 2.75*mm
L_slot_2 = 9*mm
L_slot_3 = 7*mm
L_slot_4 = 8.5*mm
L_slot_5 = 3*mm
L_slot_6 = 8.65*mm
W_slot = 1*mm
F_width = 2*mm
F_length = 18*mm

SUB_width = 20*mm
SUB_length = 20*mm
SUB_height = 0.8*mm
CU_th = 35e-6
Rair = 15*mm
model = em.Simulation("Dual Polarized Slot Antenna")

dielectric = em.geo.Box(SUB_width, SUB_length, SUB_height, position=(-SUB_width / 2, -SUB_length / 2, 0))
dielectric.set_material(em.lib.DIEL_FR4)
ground = em.geo.XYPlate(SUB_width,SUB_length,position=(-SUB_width/2,-SUB_length/2,0))
ground.set_material(em.lib.PEC)
MSA = em.geo.XYPlate(F_width,F_length,position=(-F_width/2,-SUB_length/2,SUB_height))
MSA.set_material(em.lib.PEC)
slot1 = em.geo.XYPlate(W_slot,L_slot_1,position=(-F_width/2,-SUB_length/2,0))
slot2 = em.geo.XYPlate(L_slot_2,W_slot,position=(-F_width/2,-SUB_length/2+L_slot_1,0))
slot3 = em.geo.XYPlate(-L_slot_3,W_slot,position=(-F_width/2,-SUB_length/2+L_slot_1,0))
ground = em.geo.subtract(ground,slot1)
ground = em.geo.subtract(ground,slot2)
ground = em.geo.subtract(ground,slot3)

port = em.geo.Plate(
    np.array([-F_width / 2, -SUB_length/2+ F_length, 0]),  # lower port corner
    np.array([F_width, 0, 0]),  # width vector along X
    np.array([0, 0, SUB_height])  # height vector along Z
)

air = em.geo.Box(30*mm, 30*mm, 15*mm, position=(-30*mm/2,-30*mm/2,-15*mm/2))
model.view()

model.commit_geometry()

model.mw.set_resolution(0.2)
model.mw.set_frequency_range(f1,f2,21)

model.generate_mesh()
model.view(plot_mesh=True)

abc_boundary = air.boundary()
model.mw.bc.AbsorbingBoundary(abc_boundary)
model.mw.bc.LumpedPort(port, 1, width=F_width, height=SUB_height, direction=(0,0,1), Z0=50.0)

model.adaptive_mesh_refinement(frequency=f0)
data = model.mw.run_sweep()

g = data.scalar.grid
f = g.freq

S11 = g.S(1, 1)
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
ZL = 50 * (1 + S11_fit) / (1 - S11_fit)
plot_sp(fdense, [S11_fit], labels=["S11 Fit"], dblim=[-40, 6])
plot_vswr(fdense, [S11_fit], labels=["VSWR"], swrlim=[1, 4])


# Ensure frequency is real
freq = np.real(fdense)

# Convert S11 magnitude to dB
S11_dB = 20 * np.log10(np.maximum(np.abs(S11_fit), 1e-15))

# Combine frequency and S11 in dB
results = np.column_stack((freq, S11_dB))

# Save as CSV
np.savetxt(
    "S11.csv",
    results,
    delimiter=",",
    header="Frequency_Hz,S11_dB",
    comments="",
    fmt="%.8e"
)