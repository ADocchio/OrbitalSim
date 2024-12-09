The Orbit Simulation program is a Python-based application designed to simulate 
and visualize orbital trajectories. Users can create orbits using Keplerian elements 
and customize simulations with various perturbations, including J2 effects, 
solar radiation pressure, and gravitational forces from additional celestial bodies. 
The program features interactive 3D trajectory plots, 2D ground tracks, 
state-space graphs, and real-time animations.


Prerequisites:
- Python 3.7 or higher
- Spice Kernal de430.bsp
- numpy
- matplotlib
- spicepy
- PyQt5
  
Install the necessary libraries using pip:
// pip install matplotlib numpy spiceypy PyQt5

SPICE Kernels
Download de430.bsp from the NASA SPICE Kernel Repository
  -https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/
  
Place the de430.bsp file in the Spice folder within the project directory.
