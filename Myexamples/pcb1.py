import emerge as em
import numpy as np
from emerge.plot import plot_sp,plot,plot_vswr,plot_ff_polar,plot_ff

model = em.Simulation("pcb")

pcb = em.geo.PCB(1.6e-3, material=em.lib.DIEL_FR4)

pcb.new(-5e-3,0,3e-3,(1,0),1).straight(10e-3)

trace = pcb.compile_paths()
pcb.determine_bounds(3e-3,3e-3,3e-3)
pcb.generate_air(10e-3)
pcb.generate_pcb()

model.view()

