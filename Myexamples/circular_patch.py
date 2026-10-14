import emerge as em
import numpy as np
from emerge.plot import plot, plot_sp,plot_ff,plot_ff_polar,plot_vswr,smith

Rpatch = 16.8e-3
Lfeed = 5e-3
pcb_th = 1.5e-3
Feed_distance=6e-3
ro = 1e-3
ri = em.coax_rin(ro, eps_r=2.1) # Teflon
f0=2.4e9
f1=2.2e9
f2=2.6e9

model = em.Simulation('circular_patch')

pcb = em.geo.PCB(1.5e-3,1.0, material=em.lib.DIEL_FR4)
th = np.linspace(0,2*np.pi, 31)[:-1]
pcb.add_poly(Rpatch*np.cos(th),Rpatch*np.sin(th),layer=1)

trace = pcb.compile_paths()
pcb.determine_bounds(15e-3,15e-3,15e-3,15e-3)
diel = pcb.generate_pcb()
air = pcb.generate_air(20e-3)

# Coax Feed
coax_out_1 = em.geo.Cylinder(ro, Lfeed, em.cs(origin=(-Feed_distance, 0, -pcb_th-Lfeed)), Nsections=15).set_material(em.lib.DIEL_TEFLON)
coax_in_1 = em.geo.Cylinder(ri, Lfeed+pcb_th, em.cs(origin=(-Feed_distance, 0, -pcb_th-Lfeed)), Nsections=12).set_material(em.lib.COPPER).foreground()
coax_out_2 = em.geo.Cylinder(ro, Lfeed, em.cs(origin=(0,-Feed_distance, -pcb_th-Lfeed)), Nsections=15).set_material(em.lib.DIEL_TEFLON)
coax_in_2 = em.geo.Cylinder(ri, Lfeed+pcb_th, em.cs(origin=(0, -Feed_distance, -pcb_th-Lfeed)), Nsections=12).set_material(em.lib.COPPER).foreground()

model.commit_geometry()

model.mw.set_frequency_range(f1,f2,21)
model.mw.set_resolution(0.2)

model.mesher.set_boundary_size(trace, 1e-3)
model.mesher.set_domain_size(coax_out_1, ri)
model.mesher.set_domain_size(coax_out_2, ri)

model.generate_mesh()
model.view(assigned_materials=True)
model.view(plot_mesh=True)

abc_boundary = air.boundary(exclude='bottom')
model.mw.bc.AbsorbingBoundary(abc_boundary)

model.mw.bc.ModalPort(coax_out_1.face('-z'),1)
model.mw.bc.ModalPort(coax_out_2.face('-z'),2)

data = model.mw.run_sweep()

g = data.scalar.grid
S11 = g.S(1,1)
f = g.freq
f_dense = g.dense_f(2001)
S11_fit = g.model_S(1,1,f_dense)
plot_sp(f_dense,[S11_fit],labels=['S11'],dblim=[-40,6])
plot_vswr(f_dense,[S11_fit],labels=['VSWR'],swrlim=[1,5])
smith(S11_fit,f_dense)

############################################################
#              POST-PROCESSING: FAR-FIELD (ANTENNAS)         #
############################################################
field = data.field.find(freq=f0)
# We will excite 90 degrees out of phase

field.set_excitations(1.0, 1.0*1j)

ff_xz = field.farfield_2d(em.ZAX, em.YAX, abc_boundary)
ff_yz = field.farfield_2d(em.ZAX, em.XAX, abc_boundary)

plot_ff(ff_xz.ang * 180 / np.pi, [ff_xz.gain.lhcp, 
                                  ff_yz.gain.lhcp,
                                  ff_xz.gain.rhcp, 
                                  ff_yz.gain.rhcp], 
        labels=['XZ Plane LHCP','YZ Plane LHCP', 'XZ Plane RHCP','YZ Plane RHCP'], dB=True, xlabel='Theta (deg)', ylabel="Gain Circular polarized [dBi]")
plot_ff_polar(ff_xz.ang, ff_yz.gain.norm, dB=True, dBfloor=-20)
plot_ff(ff_xz.ang*180/np.pi, [ff_xz.AR], labels=['Axial Ratio'],dB=True,xlabel='Theta(deg)', ylabel='AR[dB]',ylim=(0,6))

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################


ff3d = field.farfield_3d(abc_boundary)
display = model.display
display.populate()
display.add_farfield3d(ff3d, 'gain.norm', 'abs', dB=True, dBfloor=-20, rmax=50e-3, opacity=0.5)
display.animate().add_field(field.grid(N=500_000).scalar('Ex','complex'), symmetrize=True, clim_crop_factor=0.5)
display.show()

