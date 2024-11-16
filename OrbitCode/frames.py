import numpy as np
import spiceypy as spice
import planet_data as pd

# x-axis rotation
def xr(a):
    a = np.deg2rad(a)
    return np.array([
        [1, 0, 0],
        [0, np.cos(a), np.sin(a)],
        [0, np.sin(a), -np.cos(a)]])

# y axis-rotation
def yr(a):
    a = np.deg2rad(a)
    return np.array([
        [np.cos(a), 0, np.sin(a)],
        [0, 1, 0],
        [-np.sin(a), 0, np.cos(a)]])

# z axis-rotation
def zr(a):
    a = np.deg2rad(a)
    return np.array([
        [np.cos(a), -np.sin(a), 0],
        [np.sin(a), np.cos(a), 0],
        [0, 0, 1]])

# Get scale of 3d projection
def get_scale(ax):
    # Get current axis limits
    x_lim = ax.get_xlim()
    y_lim = ax.get_ylim()
    z_lim = ax.get_zlim()

    # Compute scaling factors based on axis limits
    scale_x = (x_lim[1] - x_lim[0]) / 2.0
    scale_y = (y_lim[1] - y_lim[0]) / 2.0
    scale_z = (z_lim[1] - z_lim[0]) / 2.0

    return np.array([scale_x, scale_y, scale_z])

# Plot the reference frames
def plot_frame(ax, reference_frames):
    # Axis Plotting
    origin = 0.0
    Identity = np.identity(3)

    scaled_identity = Identity * get_scale(ax)

    # Use quiver to plot the scaled unit vectors
    ax.quiver(origin, origin, origin,
              scaled_identity[:, 0], scaled_identity[:, 1], scaled_identity[:, 2],
              color='b')

    ax.text(scaled_identity[0, 0], scaled_identity[1, 0], scaled_identity[2, 0], 'X', color='b')
    ax.text(scaled_identity[0, 1], scaled_identity[1, 1], scaled_identity[2, 1], 'Y', color='b')
    ax.text(scaled_identity[0, 2], scaled_identity[1, 2], scaled_identity[2, 2], 'Z', color='b')

    for reference in reference_frames:
        reference *= get_scale(ax)
        ax.quiver(origin, origin, origin,
                  reference[0, :], reference[1, :], reference[2, :],
                  color='w')

        ax.text(reference[0, 0], reference[1, 0], reference[2, 0], 'X', color='w')
        ax.text(reference[0, 1], reference[1, 1], reference[2, 1], 'Y', color='w')
        ax.text(reference[0, 2], reference[1, 2], reference[2, 2], 'Z', color='w')


def eci2ecef(r_states, tspan, frame='J2000'):
    # Preallocate arrays
    steps = r_states.shape[0]
    rotation_m = np.zeros((steps, 3, 3))
    nr_states = np.zeros(r_states.shape)

    for step in range(steps):
        rotation_m[step, :, :] = spice.pxform(frame, 'ITRF93', tspan[step])
        #Preform matrix multiplication to apply rotation matrix
        nr_states[step, :] = np.dot(rotation_m[step, :, :], r_states[step, :])

    return nr_states

### Coordinate Conversions
def ecef2latlong(r_states, tspan, frame='J2000'):
    steps = r_states.shape[0]
    latlongs = np.zeros((steps, 3))
    r_ecef_states = eci2ecef(r_states, tspan, frame)

    for step in range(steps):
        r_normal, long, lat = spice.reclat(r_ecef_states[step, :])
        latlongs[step, :] = [np.rad2deg(lat), np.rad2deg(long), r_normal]

    return latlongs, r_ecef_states

def eci2perifocal(an, aop, i):
    i_vec = np.array([
        np.cos(an) * np.cos(aop) - np.sin(an) * np.sin(aop) * np.cos(i),
        -np.cos(an) * np.sin(aop) - np.sin(an) * np.cos(aop) * np.cos(i),
        np.sin(an) * np.sin(i)
    ])
    j_vec = np.array([
        np.sin(an) * np.cos(aop) + np.cos(an) * np.sin(aop) * np.cos(i),
        -np.sin(an) * np.sin(aop) + np.cos(an) * np.cos(aop) * np.cos(i),
        -np.cos(an) * np.sin(i)
    ])
    k_vec = np.array([
        np.sin(i) * np.sin(aop),
        np.sin(i) * np.cos(aop),
        np.cos(i)
    ])

    return np.array([i_vec, j_vec, k_vec])

def latlong2ecef(r_states):
    steps = r_states.shape[0]
    r_ecef_states = np.zeros((steps, 3))

    for step in range(steps):
        radius = r_states[step, 2]
        lat = np.deg2rad(r_states[step, 0])    # Latitude in radians
        lon = np.deg2rad(r_states[step, 1])    # Longitude in radians
        x, y, z = spice.latrec(radius, lon, lat)
        r_ecef_states[step, :] = [x, y, z]

    return r_ecef_states

def ecef2eci(r_states, time, frame='ITRF93'):
    # r_states is an array of shape (N, 3)
    # time is a scalar representing the time at which to perform the transformation

    # Get the rotation matrix from ECEF to ECI at the given time
    rotation_m = spice.pxform(frame, 'J2000', time)
    # Apply rotation to all positions
    nr_states = np.dot(r_states, rotation_m.T)
    return nr_states

# Position and velocity to KOE
def rv2koe(r, v, mu, degrees=False):
    normal_r = np.linalg.norm(r)
    normal_v = np.linalg.norm(v)

    # Angular momentum vector and its norm
    h = np.cross(r, v)
    normal_h = np.linalg.norm(h)

    # Inclination
    i = np.arccos(h[2] / normal_h)

    # Eccentricity vector and its norm
    e = ((normal_v ** 2 - mu / normal_r) * r - np.dot(r, v) * v) / mu
    normal_e = np.linalg.norm(e)

    # Ascending Node vector and its norm
    N = np.cross([0, 0, 1], h)
    normal_N = np.linalg.norm(N)

    # Ascending Node (Right Ascension of the Ascending Node, RAAN)
    if normal_N != 0:
        an = np.arccos(N[0] / normal_N)
        if N[1] < 0:
            an = 2 * np.pi - an
    else:
        an = 0  # Edge case for equatorial orbit

    # Argument of Perigee
    if normal_N != 0 and normal_e != 0:
        aop = np.arccos(np.dot(N, e) / (normal_N * normal_e))
        if np.dot(N, e) < 0:
            aop = 2 * np.pi - aop
    else:
        aop = 0  # Edge case for circular or equatorial orbit

    # True Anomaly
    if normal_e != 0:
        ta = np.arccos(np.dot(e, r) / (normal_e * normal_r))
        if np.dot(r, v) < 0:
            ta = 2 * np.pi - ta
    else:
        ta = 0  # Edge case for circular orbit

    # Semi-Major Axis using the vis-viva equation
    a = 1 / ((2 / normal_r) - (normal_v ** 2 / mu))

    # Convert angles to degrees if requested
    if degrees:
        return [a, normal_e, np.rad2deg(i), np.rad2deg(ta), np.rad2deg(aop), np.rad2deg(an)]
    else:
        return [a, normal_e, i, ta, aop, an]

# Koe to position and velocity
def koe2rv(koe, cb=pd.Earth):
    mu = cb['mu']
    a, e, i, an, aop, ta = koe

    # Convert angles from degrees to radians
    i = np.radians(i)
    an = np.radians(an)
    aop = np.radians(aop)
    ta = np.radians(ta)

    # Compute radius in the perifocal frame
    p = a * (1 - e ** 2)
    r_normal = p / (1 + e * np.cos(ta))

    # Position in perifocal coordinates
    r_perifocal = r_normal * np.array([np.cos(ta), np.sin(ta), 0])

    # Velocity in perifocal coordinates
    v_perifocal = np.sqrt(mu / p) * np.array([-np.sin(ta), e + np.cos(ta), 0])

    # Coordinate transformation matrix from perifocal to ECI
    perifocal2eci = np.transpose(eci2perifocal(an, aop, i))

    # Position and velocity in ECI frame
    r0 = np.dot(perifocal2eci, r_perifocal)
    v0 = np.dot(perifocal2eci, v_perifocal)

    return r0, v0
