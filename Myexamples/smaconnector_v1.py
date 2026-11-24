import emerge as em
import numpy as np
from emerge.plot import plot_sp

mm = 1e-3
um = 1e-6

f_start, f_stop, f_center, N_freq = 1.0e9, 2.0e9, 1.5e9, 21

sim = em.Simulation("SMACONNECTOR")
sim.mw.set_frequency_range(f_start, f_stop, N_freq)

# ---------------- Geometry ----------------
pcb = em.geo.Box(50*mm, 50*mm, 1.59*mm,
                 (-25*mm, 0, -1.59*mm)).set_material(em.lib.DIEL_FR4)

gnd = em.geo.Box(50*mm, 50*mm, 35*um,
                 (-25*mm, 0, -1.59*mm - 35*um)).set_material(em.lib.COPPER)

ms = em.geo.Box(3*mm, 48*mm, 35*um,
                (-1.5*mm, 0, 0)).set_material(em.lib.COPPER)

# FIX: air box must enclose PCB, ground and the full SMA bodies
# x: -35..35, y: -30..80, z: -20..30
air = em.geo.Box(70*mm, 110*mm, 50*mm,
                 (-35*mm, -30*mm, -20*mm)).set_material(em.lib.AIR).background()

# ---------------- SMA connectors ----------------
port1 = em.macro.SMAConnector(
    1.59*mm,
    (-em.YAX).construct_cs(0, 0, 0),
    15

)

port2 = em.macro.SMAConnector(
    1.59*mm,
    (-em.YAX).construct_cs(0, 50*mm, 0).rotate(em.ZAX, angle=180),
    15
)

sim.commit_geometry()
# sim.view()   # enable once to confirm both connectors touch the strip ends
#              # (y=0 and y=50 mm) and point outward

# ---------------- Boundary conditions ----------------
sim.mw.bc.ModalPort(port1.port_face, 1, modetype="TEM")
sim.mw.bc.ModalPort(port2.port_face, 2, modetype="TEM")

# FIX: second-order ABC for lower reflections
sim.mw.bc.AbsorbingBoundary(air.boundary(), order=2)

# ---------------- Mesh ----------------
sim.mw.set_resolution(0.2)      # finer mesh (smaller = finer)
sim.generate_mesh()
# sim.view(plot_mesh=True)

sim.adaptive_mesh_refinement(frequency=f_center)

# ---------------- Solve ----------------
data = sim.mw.run_sweep()

freqs = np.asarray(data.scalar.grid.freq)
S11 = np.asarray(data.scalar.grid.S(1, 1))
S21 = np.asarray(data.scalar.grid.S(2, 1))

S11_dB = 20*np.log10(np.maximum(np.abs(S11), 1e-15))
S21_dB = 20*np.log10(np.maximum(np.abs(S21), 1e-15))

print("\nFrequency (GHz)    S11 (dB)    S21 (dB)")
print("-"*48)
for f, s11, s21 in zip(freqs, S11_dB, S21_dB):
    print(f"{f/1e9:10.4f}       {s11:8.3f}     {s21:8.3f}")

plot_sp(freqs, [S11, S21], dblim=[-60, 3], labels=["S11", "S21"])

# ---------------- Field plot ----------------
field = data.field.find(freq=f_center)
sim.display.populate(opacity=0.6)
sim.display.animate().add_field(
    field.grid(N=100_000, z_range=(-1.59*mm, 0)).scalar("Ez", "complex"),
    symmetrize=True
)
sim.display.show()