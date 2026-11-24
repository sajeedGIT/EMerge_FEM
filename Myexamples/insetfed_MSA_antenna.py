import emerge as em
from emerge.plot import plot_sp, plot_ff,plot_ff_polar,plot_vswr,smith
import numpy as np



model = em.Simulation("Inset Fed Patch Antenna")

mm = 1e-3

patch_Width = 32 * mm
patch_Length = 29.2 * mm
sub_width = 60 * mm
sub_length = 70 * mm
sub_thickness = 1.59 * mm
feed_width = 3 * mm
feed_length = 15 * mm
inset_gap = 1 * mm
inset_distance = 10 * mm

f1 = 2.2e9
f2 = 2.6e9
f0 = (f1 + f2) / 2
n_points = 21
pcb = em.geo.PCB(
    thickness=sub_thickness,
    unit=1.0,
    material=em.lib.DIEL_FR4,

)
pcb.new(-feed_length, 0, feed_width, (1,0), 1)['port'].straight(feed_length)
patch_poly = em.geo.XYPolygon(
    xs = [0, inset_distance, inset_distance, 0, 0, patch_Length, patch_Length, 0, 0, inset_distance,
           inset_distance, 0],
    ys = [feed_width/2, feed_width/2, feed_width/2+inset_gap, feed_width/2+inset_gap,patch_Width/2, 
          patch_Width/2, -patch_Width/2, -patch_Width/2, -feed_width/2-inset_gap, -feed_width/2-inset_gap,
           -feed_width/2, -feed_width/2]).geo(em.GCS).set_material(em.lib.COPPER)

pcb.set_bounds(-sub_width / 2, -sub_length / 2, sub_width, sub_length/2)
trace = pcb.compile_paths(True)
diel = pcb.generate_pcb()
air = pcb.generate_air(20*mm)
lumped_port_face = pcb.lumped_port('port', port_number=1)
model.commit_geometry()


model.mw.set_frequency_range(f1, f2, n_points)
model.mw.set_resolution(0.2)

model.generate_mesh()
model.view(assigned_materials=True)
model.view(plot_mesh=True)


abc_boundary = air.boundary(exclude='bottom')
model.mw.bc.AbsorbingBoundary(abc_boundary)
model.adaptive_mesh_refinement(frequency=f0)
data = model.mw.run_sweep()

g = data.scalar.grid
f = g.freq
S11 = g.S(1, 1)
plot_sp(f, [S11], labels=["S11"], dblim=[-40, 6])
smith(S11, f)
# supersample with Vector Fitting for smoother curves
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
plot_sp(fdense, [S11_fit], labels=["S11"])

############################################################
#              POST-PROCESSING: FAR-FIELD (ANTENNAS)         #
############################################################

ff_xz = data.field.find(freq=f0).farfield_2d(em.ZAX, em.YAX, abc_boundary)
ff_yz = data.field.find(freq=f0).farfield_2d(em.ZAX, em.XAX, abc_boundary)
plot_ff(ff_xz.ang * 180 / np.pi, [ff_xz.gain.norm, ff_yz.gain.norm], labels=['XZ Plane','YZ Plane'], dB=True, ylabel="Gain [dBi]")
plot_ff_polar(ff_xz.ang, ff_yz.gain.norm, dB=True, dBfloor=-20)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=f0)
ff3d = field.farfield_3d(abc_boundary)
display = model.display
display.populate()
display.add_farfield3d(ff3d, 'gain.norm', 'abs', dB=True, dBfloor=-20, rmax=50*mm, opacity=0.5)
display.animate().add_field(field.grid(N=500_000).scalar('Ex','complex'), symmetrize=True, clim_crop_factor=0.5)
display.show()