import numpy as np
from scipy.integrate import ode
import spiceypy as spice
import spice_tools as s
import planet_data as pd
import frames as ft


class OrbitalState:
    def __init__(self, koe, user_args = {}):

        #Default Arguments
        self.args = {
            'perturbations' :
                {
                'j2' : False,
                'solar' : False,
                'lunar' : False
                },
            'centralBody' : pd.Earth,
            'degrees' : True,
            'Mass': 0.1, #kg
            'Asrp' : 10, #m^2
            'Cr': 1.4, #

            'startDate' : '2020-01-01', #J2000
            'tSpan' : 86400, # One Day
            'dt' : 60.0, # Every minute
        }
        self.koe = koe
        self.r0, self.v0 = ft.koe2rv(self.koe, self.args['centralBody'])
        self.step = 0

        # Update default with passed args
        self.update_args(user_args)

    # Update args
    def update_args(self, user_args):
        for key in self.args:
            if user_args.get(key) is not None:
                self.args[key] = user_args[key]

        # Propagate Setup
        self.step_n = int(self.args['tSpan'] / self.args['dt'])
        self.t_steps = np.zeros((self.step_n, 1))
        self.state = np.zeros((self.step_n, 6))

        # Convert to Epoch Time
        self.et0 = spice.utc2et(self.args['startDate'])
        self.args['tSpan'] = np.linspace(self.et0, self.et0 + self.args['tSpan'], self.step_n)

        # Get Central Body's location with respect to the sun for solar radiation pressure calculations
        self.solor = s.get_ephemeris_states('EARTH', self.args['tSpan'], 'J2000', 'SUN')

        # Get Central Body's location with respect to the moon for solar radiation pressure calculations
        self.lunar = s.get_ephemeris_states('MOON', self.args['tSpan'], 'J2000', 'EARTH')

        # Orbit information
        self.info = self.koe + [self.args['Mass']] + [self.args['Asrp']] + [self.args['Cr']]

    # KOE with respect to time
    def koe_propagation(self):
        self.koe_t = np.zeros((self.step_n, 6))
        cb = self.args['centralBody']

        for step in range(self.step_n):
            if self.args['degrees']:
                self.koe_t[step, :] = ft.rv2koe(self.state[step, :3], self.state[step, 3:6], cb['mu'], True)
            else:
                self.koe_t[step, :] = ft.rv2koe(self.state[step, :3], self.state[step, 3:6], cb['mu'])

    # Get LatLongs for ground map plotting
    def latlongs(self):
        self.latlong, self.r_ecef = ft.ecef2latlong(self.state[:, :3], self.et0 + self.args['tSpan'])

    # Differential Equation Governing Dynamics
    def two_body(self, t, s, mu):
        # unpack the state vector
        rx, ry, rz, vx, vy, vz = s
        r = np.array([rx, ry, rz])

        # Newtons Law of Gravitation
        normal_r = np.linalg.norm(r)
        a = -r * mu / normal_r ** 3

        # J2 Perturbation
        if self.args['perturbations']['j2']:
            z2 = r[2] ** 2
            r2 = normal_r ** 2
            tx = r[0] / normal_r * (5 * z2 / r2 - 1)
            ty = r[1] / normal_r * (5 * z2 / r2 - 1)
            tz = r[2] / normal_r * (5 * z2 / r2 - 3)
            j2 = (1.5 * self.args['centralBody']['J2'] * self.args['centralBody']['mu'] *
                  self.args['centralBody']['radius'] ** 2 / normal_r ** 4 * np.array([tx, ty, tz]))

            a += j2

        # Solar radiation pressure
        if self.args['perturbations']['solar']:
            # Vector from sun to satellite
            r_sun_sat = self.solor[self.step, :3] + r

            a += (1 + self.args['Cr'])*pd.Sun['G1']*self.args['Asrp']/self.args['Mass']/np.linalg.norm(r_sun_sat)**3*r_sun_sat

        # Solar radiation pressure
        if self.args['perturbations']['lunar']:
            # vector from earth to moon
            r_moon_earth = self.lunar[self.step, :3]

            # vector from satellite to moon
            r_moon_sat = r_moon_earth - r

            a += pd.Moon['mu'] * (r_moon_sat / np.linalg.norm(r_moon_sat) ** 3 - r_moon_earth / np.linalg.norm(r_moon_earth) ** 3)

        return [vx, vy, vz, a[0], a[1], a[2]]

    # Propagate the orbit through time, Defines orbital state
    def propagate_orbit(self):

        # Set up state vector
        state0 = np.concatenate((self.r0, self.v0), axis=None)
        self.state[0] = state0  #set initial conditions

        self.step = 1  # set starting step

        # set up ODE solver
        solver = ode(self.two_body)
        solver.set_integrator('dopri5')
        solver.set_initial_value(state0, 0)
        solver.set_f_params(self.args['centralBody']['mu'])

        try:
            while solver.successful() and self.step < self.step_n:
                solver.integrate(solver.t + self.args['dt'])
                self.t_steps[self.step] = solver.t
                self.state[self.step] = solver.y
                self.step += 1
        except Exception as e:
            print(f" error: {e}")
