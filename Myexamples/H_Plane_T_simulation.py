# H-plane T-junction simulation using Emerge
#Implemented by: Dr. Sajeed S. Mulla, Associate Professor, 
# Department of Electronics and Teleommunication Engineering, 
# Dnyanshree Institute of Technology Satara, Maharashtra, India.
import emerge as em

mm = 0.001  # Define a millimeter

wg_width = 22.86 * mm  # Width of WR90 waveguide
wg_height = 10.16 * mm  # Height of WR90 waveguide
wg_length = 100 * mm  # Arbitrary length

my_model = em.Simulation('MyFirstModel')

box1 = em.geo.Box(wg_width, wg_length, wg_height)
box2 = em.geo.Box(wg_length, wg_width, wg_height, position=(wg_width,3*wg_length/8, 0)) #H arm of the H-plane T-junction
box = em.geo.unite(box1, box2)
my_model.commit_geometry()

my_model.view(face_labels=True)

my_model.mw.set_frequency_range(8e9, 10e9, 21)

my_model.generate_mesh()

my_model.view(plot_mesh=True)

port1 = my_model.mw.bc.RectangularWaveguide(box.face('+x'), 1)
port2 = my_model.mw.bc.RectangularWaveguide(box.face('-y'), 2)
port3 = my_model.mw.bc.RectangularWaveguide(box.face('+y'), 3)

fdata = my_model.mw.run_sweep()

freqs = fdata.scalar.grid.freq
S11 = fdata.scalar.grid.S(1, 1)
S21 = fdata.scalar.grid.S(2, 1)
S31 = fdata.scalar.grid.S(3, 1)

from emerge.plot import plot_sp

plot_sp(freqs, [S11, S21, S31], labels=['S11', 'S21', 'S31'], dblim=[-60, 3])

field = fdata.field.find(freq=9e9)
my_model.display.populate()
efield = my_model.display.animate().add_field(field.grid(N=20000).scalar('Ez','complex'),symmetrize=True)
my_model.display.show()
