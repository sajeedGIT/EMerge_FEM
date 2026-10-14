import emerge as em
import numpy as np
from emerge.plot import plot_sp, plot_ff, plot_ff_polar,smith

Wpatch = 32e-3
Lpatch = 28.5e-3
feed_distance = 6e-3

ro = 1e-3
ri = em.coax_rin(ro,eps_r=2.1)

print("Coax inner radius: ", ri)

Lfeed = 5e-3
width_pcb = 60e-3
length_pcb = 70e-3
th_pcb = 1.5e-3


model = em.Simulation("MSA_Coax")

pcb = em.geo.PCB(th_pcb, 1, material=em.lib.DIEL_FR4)
pcb.new(-Lpatch/2,0,Wpatch,(1,0),1).straight(Lpatch)

trace = pcb.compile_paths(True)

pcb.determine_bounds(15e-3, 15e-3, 15e-3, 15e-3)
diele = pcb.generate_pcb()
air = pcb.generate_air(20e-3)

coax_out = em.geo.Cylinder(ro,Lfeed,em.cs(origin=(-feed_distance,0,-Lfeed-th_pcb)),Nsections=15).set_material(em.lib.DIEL_TEFLON)
coax_in = em.geo.Cylinder(ri,Lfeed+th_pcb,em.cs(origin=(-feed_distance,0,-Lfeed-th_pcb)),Nsections=20).set_material(em.lib.COPPER).foreground()
model.commit_geometry()


model.mw.set_frequency_range(2.2e9, 2.6e9, 21)
model.mw.set_resolution(0.2)

model.mesher.set_boundary_size(trace,1e-3)
model.mesher.set_domain_size(coax_out, ri)

model.generate_mesh()
model.view(assigned_materials=True)
model.view(plot_mesh=True)

abc_boundary = air.boundary(exclude="bottom")
model.mw.bc.AbsorbingBoundary(abc_boundary)
model.mw.bc.ModalPort(coax_out.face('-z'),1)

data = model.mw.run_sweep()

g = data.scalar.grid
S11 = g.S(1,1)
freq = g.freq

plot_sp(freq, [S11], labels=["S11"], dblim=[-40,6])
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
plot_sp(fdense, [S11_fit], labels=["S11"])
smith(S11_fit,fdense)

ff_xz = data.field.find(freq=2.4e9).farfield_2d(em.ZAX, em.YAX, abc_boundary)
ff_yz = data.field.find(freq=2.4e9).farfield_2d(em.ZAX, em.XAX, abc_boundary)
plot_ff(ff_xz.ang * 180 / np.pi, [ff_xz.gain.norm, ff_yz.gain.norm], labels=['XZ Plane','YZ Plane'], dB=True, xlabel='Theta (deg)', ylabel="Gain [dBi]")
plot_ff_polar(ff_xz.ang, ff_xz.gain.norm, dB=True, dBfloor=-20)
plot_ff_polar(ff_yz.ang, ff_yz.gain.norm, dB=True, dBfloor=-20)

field = data.field.find(freq=2.4e9)
ff3d = field.farfield_3d(abc_boundary)
display = model.display
display.populate()
display.add_farfield3d(ff3d, 'gain.norm', 'abs', dB=True, dBfloor=-20, rmax=50e-3, opacity=0.5)
display.animate().add_field(field.grid(N=500_000).scalar('Ex','complex'), symmetrize=True, clim_crop_factor=0.5)
display.show()