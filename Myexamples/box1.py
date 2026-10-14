import emerge as em

sim=em.Simulation('MyFirstModel')
#box=em.geo.Box(1,1,1).set_material(em.lib.PEC)
#box=em.geo.Box(1,1,1).set_material(em.lib.DIEL_FR4)
#box=em.geo.Box(1,1,1).set_material(em.lib.COPPER)
coax = em.geo.CoaxCylinder(1,0.95,3).set_material(em.lib.COPPER)
coax = em.geo.CoaxCylinder(0.1,0,3).set_material(em.lib.COPPER)
coax = em.geo.CoaxCylinder(0.95,0.1,3).set_material(em.lib.DIEL_FR4)
sim.view()