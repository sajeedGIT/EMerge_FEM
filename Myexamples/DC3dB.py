from emerge_config import config
from emerge.plot import plot_sp, plot
import emerge as em
import numpy as np

config.set_acc_threads(4)

f1 = 1e9
f0 = 3e9
f2 = 5e9
nf = 21
Z0 = 50
c = 0.5
Z0e = Z0*((1+c)/(1-c))**0.5
Z0o = Z0*((1-c)/(1+c))**0.5

w0 = 0.98e-3
w1 = 0.58e-3

Lf = 10e-3
Lq = 14e-3
gap = 0.1e-3

margin = 5e-3

y0 = Lf + w1 + gap/2
th = 0.508e-3
th_cu = 35e-6

model = em.Simulation("Directional_Coupler")

pcb = em.geo.PCB(th, 1.0, trace_material=em.lib.PEC,material=em.lib.DIEL_FR4,trace_thickness=th_cu,thick_traces=True)
pcb.new(0, y0, w0, (0,-1), 1)[1].straight(Lf)\
    .move(dx=w0/2, dy=-w1/2, direction=(1,0), width=w1).straight(Lq)\
    .move(dx=w0/2, dy=w1/2, direction=(0,1), width=w0).straight(Lf, w0)[3]
pcb.new(0, -y0, w0, (0,1), 1)[2].straight(Lf)\
    .move(dx=w0/2, dy=w1/2, direction=(1,0), width=w1).straight(Lq)\
    .move(dx=w0/2, dy=-w1/2, direction=(0,-1), width=w0).straight(Lf, w0)[4]
trace = pcb.compile_paths(True)

pcb.determine_bounds(margin, margin, margin, margin)
p1 = pcb.lumped_port(1, 1)
p2 = pcb.lumped_port(2, 2)
p3 = pcb.lumped_port(3, 3)
p4 = pcb.lumped_port(4, 4)

le = pcb.lumped_elements
diel = pcb.generate_pcb()
air = pcb.generate_air(5e-3)

model.view()

model.commit_geometry()
model.mw.set_frequency_range(f1, f2, nf)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.2)
model.mesher.set_boundary_size(trace, 0.5e-3)
model.mesher.set_trace_refinement(trace.face('-z'), qualtity_factor=1.5)
model.generate_mesh()
model.view(plot_mesh=True)

data = model.mw.run_sweep(frequency_groups=4)

g = data.scalar.grid
f = data.scalar.grid.freq
S11 = g.S(1,1)
S21 = g.S(2,1)
S31 = g.S(3,1)
S41 = g.S(4,1)

plot_sp(f, [S11, S21, S31, S41], labels=["S11", "S21","S31","S41"], dblim=[-40, 6])

ratio_3 = np.abs(S31)
ratio_2 = np.abs(S21)

plot(f, [ratio_3, ratio_2], labels=['Amplitude 3','Amplitude 2'], xlabel='Frequency (GHz)',ylabel='Coupling Ratio', ylim=[0,1])

field = data.field.find(freq=f0)
field.set_excitations(1,0,0,0)
display = model.display
display.populate()
display.animate().add_field(field.grid(N=200_000).scalar('Ez','complex'), symmetrize=True, clim_crop_factor=0.25)
display.show()