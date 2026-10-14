
import emerge as em

mm = 0.001  # Define a millimeter

wg_width = 22.86 * mm  # Width of WR90 waveguide
wg_height = 10.16 * mm  # Height of WR90 waveguide
wg_length = 50 * mm  # Arbitrary length

my_model = em.Simulation('MyFirstModel')

box = em.geo.Box(wg_width, wg_length, wg_height)

my_model.commit_geometry()

my_model.view()

my_model.mw.set_frequency_range(13.5e9, 15e9, 21)

my_model.generate_mesh()

my_model.view(plot_mesh=True)

port1 = my_model.mw.bc.RectangularWaveguide(box.front, 1)
port2 = my_model.mw.bc.RectangularWaveguide(box.back, 2)
fdata = my_model.mw.run_sweep()

freqs = fdata.scalar.grid.freq

from emerge.plot import plot_sp

S11 = fdata.scalar.grid.S(1, 1)
S21 = fdata.scalar.grid.S(2, 1)
plot_sp(freqs, [S11, S21], labels=['S11', 'S21'], dblim=[-60, 3])

field = fdata.field.find(freq=14e9)
display = my_model.display
display.populate()
#display.animate().add_field(field.grid(N=20000).scalar('Ez','complex'),symmetrize=False)
display.cbar('Evec').animate().add_field(field.grid(N=50000).vector('E', 'complex'))
display.show()