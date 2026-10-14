import emerge as em
import numpy as np

model = em.Simulation('Microstrip with Via')

PCB = em.geo.PCBNew(1.6e-3, 1.0, material=em.lib.DIEL_FR4, trace_material=em.lib.PEC, trace_thickness=35e-6, thick_traces=True )

#PCB.new(0, 0, 3.0e-3, (1, 0), 1)[1].straight(10e-3,3e-3).turn(90,corner_type='champher').straight(8e-3,1e-3)
PCB.new(0, 0, 3.0e-3, (1, 0), 1)[1].straight(10e-3).turn(90).straight(8e-3,1e-3)

PCB.add_vias((0,0),radius=1e-3,segments=8,layer1=0,layer2=1)

PCB.compile_paths(True)

PCB.determine_bounds(15e-3, 15e-3, 15e-3, 15e-3)
PCB.generate_vias(True)
PCB.generate_pcb()

model.commit_geometry()
model.view()