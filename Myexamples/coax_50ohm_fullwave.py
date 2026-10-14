import emerge as em
import numpy as np

# ============================================================
# Full-wave simulation of a 50-ohm coaxial cable
# Dimensions are in meters.
# ============================================================
# -----------------------------
# Parameters
# -----------------------------
a = 1.0e-3          # Inner conductor radius = 1 mm
b = 2.301e-3        # Outer conductor inner radius = 2.301 mm
t = 0.5e-3          # Outer conductor thickness = 0.5 mm
L = 20e-3           # Cable length = 20 mm

# Air dielectric
er = 1.0

# Theoretical impedance for an air-filled coax:
# Z0 = 60 ln(b/a)
Z0 = 60.0 * np.log(b / a)

print("=" * 55)
print("50-ohm COAXIAL CABLE - FULL WAVE SIMULATION")
print("=" * 55)
print(f"Inner radius       : {a*1e3:.3f} mm")
print(f"Outer inner radius : {b*1e3:.3f} mm")
print(f"Cable length       : {L*1e3:.3f} mm")
print(f"Theoretical Z0     : {Z0:.3f} ohm")
print("=" * 55)

# -----------------------------
# Create simulation
# -----------------------------
sim = em.Simulation("Coax_50Ohm_FullWave")
# -----------------------------
# Geometry
# -----------------------------
# Inner PEC conductor
inner = em.geo.Cylinder(a,L,Nsections=15).set_material(em.lib.PEC)
# Outer PEC conductor
outer = em.geo.CoaxCylinder(b + t,b,L,Nsections=15).set_material(em.lib.PEC)
dielectric = em.geo.CoaxCylinder(b,a,L,Nsections=15).set_material(em.lib.AIR)
# Commit geometry
sim.commit_geometry()
sim.view()
# -----------------------------
# Mesh
# -----------------------------
sim.mw.set_frequency(800e6)
sim.generate_mesh()
# -----------------------------
# Display geometry
# -----------------------------
sim.view(plot_mesh=True)

#Select the input and output ports for the coaxial cable simulation.
port1 = sim.mw.bc.CoaxPort(dielectric.front,1,rad_in_out=(a,b),cs=em.GCS) 
port2 = sim.mw.bc.CoaxPort(dielectric.back,2,rad_in_out=(a,b),cs=em.GCS) 

# Then run the microwave solver and obtain MWField.
fdata = sim.mw.run_sweep()
freqs = fdata.scalar.grid.freq

# Electric field 
field = fdata.field.find(freq=800e6)
sim.display.populate(opacity=0.2)
efield = sim.display.animate().add_field(field.grid(N=20000).scalar('Ex','complex'),symmetrize=True)
sim.display.show()
# ============================================================