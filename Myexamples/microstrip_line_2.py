# =============================================================================
# EMerge Simulation Template: Microstrip tapered lines
#
# Copyright (C) 2026 Andrés Martínez Mera
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# =============================================================================

# -----------------------------------------------------------------------------
# Microstrip Impedance Taper (50 to 15 Ohm)
#
# Compares different ways of gradually widening a transmission line to
# transform its impedance from 50 to 15 ohm, instead of stepping it in one
# abrupt jump. Four taper shapes are precomputed and selectable: exponential,
# triangular, linear, and Klopfenstein (the smoothest, lowest-ripple option
# from classic microwave filter theory). Built on a 0.508 mm RO4003C
# substrate, centered at 1.5 GHz and swept from 100 MHz to 5 GHz.
# -----------------------------------------------------------------------------
from emerge_config import config

config.set_acc_threads(4)

import emerge as em
from emerge.plot import plot_sp
import numpy as np

# ---------------------------------------------------------------------------
# TAPER SELECTION
# ---------------------------------------------------------------------------
"""
    Set TAPER_TYPE variable according to the desired impedance profile:
        - exponential
        - triangular
        - klopfenstein
        - linear
        - all: Simulate all profiles on a row
    See [1], section 5.8 for reference.
    [1] D. M. Pozar, "Microwave Engineering," 4th ed., Wiley, 2012
"""
# The following profiles can be automatically generated with python scripts.
# Check the /advanced/ directory for the full scripts!


############################################################
#                     UNITS & CONSTANTS                    #
############################################################

# EMerge works in SI units internally, so it's convenient to define a few
# unit helpers at the top of the script.
mm = 0.001      # meters per millimeter
mil = 0.0254 * mm
inch = 25.4 * mm

MHz = 1e6
GHz = 1e9

C0 = 299792458
Z0 = 376.73031366857
PI = np.pi
EPS0 = 8.854187818814e-12
MU0 = 1/(C0*C0*EPS0)

############################################################
#                    DESIGN PARAMETERS                     #
############################################################
f0 = 1500 * MHz        # [Hz] Center frequency
lambda_ = C0/ (np.sqrt(3.55)*f0)
Z1 = 50.0              # [Ohm] source impedance
Z2 = 15.0              # [Ohm] load impedance (matches the Chebyshev example)

th   = 1.59           # [mm] substrate thickness
Lfeed  = 5             # [mm] straight Z1 / Z2 feed lines at each end
Ltaper = 1e3*lambda_   # [mm] taper length
N_seg  = 60            # number of straight segments approximating the taper

Hair = 5              # [mm] air box height

############################################################
#                     FREQUENCY SWEEP                      #
############################################################

f_start = 100 * MHz
f_stop  = 5000 * MHz
n_points = 20

# ---------------------------------------------------------------------------
# Build the impedance / width profile for the chosen taper
# ---------------------------------------------------------------------------


# Widths for the clean uniform feed lines at each end
W_feed_in  = 10


############################################################
#                      SIMULATION SETUP                    #
############################################################

model = em.Simulation("microstrip_line")
model.check_version("3.0.0")

############################################################
#                          GEOMETRY                        #
############################################################

pcb = em.geo.PCB(th, unit=mm, material=em.lib.DIEL_FR4, trace_material=em.lib.PEC)

# ---------------------------------------------------------------------------
# Layout: feed(Z1) -> N_seg tapered segments -> feed(Z2)
# ---------------------------------------------------------------------------
pcb_margin = 25  # Space at both sides of the copper traces

path = pcb.new(0, 0, W_feed_in, (1, 0), 1)[1].straight(70)[2]


# --- Compile traces ------------------------------------------------------
stripline = pcb.compile_paths(True)

# ---------------------------------------------------------------------------
# Bounding box, dielectric and air
# ---------------------------------------------------------------------------
pcb.determine_bounds(topmargin=pcb_margin, bottommargin=pcb_margin, leftmargin=0, rightmargin=0)
diel = pcb.generate_pcb(merge=True)
air  = pcb.generate_air(Hair)

# ---------------------------------------------------------------------------
# Modal ports
# ---------------------------------------------------------------------------
p1 = pcb.modal_port(1, 1, height=Hair, width=15) # Input
p2 = pcb.modal_port(2, 2, height=Hair, width=15) # Output

############################################################
#                   SOLVER / MESH SETTINGS                 #
############################################################
model.mw.set_resolution(0.2)
model.mw.set_frequency_range(f_start, f_stop, n_points)

############################################################
#                      COMMIT GEOMETRY                     #
############################################################
model.commit_geometry()

############################################################
#               GENERATE, REFINE & VIEW MESH               #
############################################################

model.generate_mesh()

model.view()

############################################################
#                   BOUNDARY CONDITIONS                    #
############################################################

# Automatically assigned

############################################################
#                      RUN SIMULATION                      #
############################################################
model.adaptive_mesh_refinement(frequency=f0)
data = model.mw.run_sweep()

############################################################
#                   EXTRACT S-PARAMETERS                   #
############################################################
grid = data.scalar.grid
f    = grid.freq

S11 = grid.S(1, 1)
S21 = grid.S(2, 1)

plot_sp(f, [S11,S21], labels=['S11','S21'])

############################################################
#                VECTOR FITTING (supersampled plot)        #
############################################################

f_fit = np.linspace(f_start, f_stop, 2001)
f_MHz = f_fit / 1e6    # Used for displaying the graphs
S11_fit = grid.model_S(1, 1, f_fit)
S21_fit = grid.model_S(2, 1, f_fit)

plot_sp(f_fit, [S11_fit,S21_fit], labels=['S11','S21'])

############################################################
#                    3D FIELD VISUALIZATION                #
############################################################

field = data.field.find(freq=f0)
model.display.add_object(diel)
model.display.add_object(stripline)
model.display.animate().add_field(
    field.grid(N=100_000, z_range=(-th * mm, th*mm)).scalar('Ez', 'complex'),
    symmetrize=True,
)
model.display.show()