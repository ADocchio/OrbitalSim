import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
import frames as ft
import planet_data as pd

# Plots a central body in a 3d plot
def plot_central_body(ax, user_args = {}):
    args = {
        'centralBody' : pd.Earth,
        'tSpan' : [631108869.1839073],
        'map' : True
    }

    for key in args:
        if user_args.get(key) is not None:
            args[key] = user_args[key]

    # Central Body Creation
    theta = np.linspace(0, 2 * np.pi, 100)
    phi = np.linspace(0, np.pi, 100)
    radius = args['centralBody']['radius']

    x = radius * np.outer(np.cos(theta), np.sin(phi))
    y = radius * np.outer(np.sin(theta), np.sin(phi))
    z = radius * np.outer(np.ones(np.size(theta)), np.cos(phi))

    ax.plot_surface(x, y, z, rstride=5, cstride=5, cmap="cool", alpha=0.5, zorder=0)
    plt.style.use('dark_background')

    # Plot coastlines on body
    if args['map']:
        coastline_latlong = np.genfromtxt('Spice/coastlines.csv', delimiter=',')
        coastline_latlong = coastline_latlong[:, [1, 0]]  # Now columns are [Latitude, Longitude]
        n = len(coastline_latlong)
        states = np.full(n, args['centralBody']['radius'])

        # Create r_states with columns [Latitude, Longitude, Radius]
        r_states = np.column_stack((coastline_latlong[:, 0], coastline_latlong[:, 1], states))
        ecef_states = ft.latlong2ecef(r_states)

        # Use the appropriate time
        current_time = args['tSpan'][0]  # Or another time if desired
        eci = ft.ecef2eci(ecef_states, current_time)

        # Plot the coastline points
        coastlines = ax.plot(eci[:, 0], eci[:, 1], eci[:, 2], 'ko', markersize=0.3, zorder=10,  alpha=0.5)

        return coastlines

# Returns a groundtrack plot of a list of orbits
def plot_groundtracks(orbits, reSimulate = False, args = {}):
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot()

    ax.set_title('Ground Tracks')
    ax.set_xlabel('Longitude [Deg]')
    ax.set_ylabel('Latitude [Deg]')

    tracks = []
    for key in orbits:
        if reSimulate:
            orbits[key].update_args(args)
            orbits[key].propagate_orbit() # Simulate new parameters
            orbits[key].latlongs() # Simulate tracks
        tracks.append(orbits[key].latlong)
    tracks = np.array(tracks)

    # [point, [log, lat]]
    coastline_latlong = np.genfromtxt('Spice/coastlines.csv', delimiter=',')
    ax.plot(coastline_latlong[:, 0], coastline_latlong[:, 1], 'mo', markersize=0.3)

    for track, key in zip(tracks, orbits.keys()):
        path, = ax.plot(track[:, 1], track[:, 0], 'o', markersize=0.5)
        path.set_label(key)
    ax.legend()

    return fig

# Returns a plot of a list of orbits
def plot_orbits(orbits, reSimulate = False, args = {}):
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Set Graph Parameters
    ax.set_xlabel('X [km]')
    ax.set_ylabel('Y [km]')
    ax.set_zlabel('Z [km]')
    ax.set_aspect('equal')
    ax.set_title('Orbital Trajectory\'s')

    #Plot Earth
    plot_central_body(ax)

    #Propgate Orbits
    trajectory = []
    for key in orbits:
        if reSimulate:
            orbits[key].update_args(args)
            orbits[key].propagate_orbit() # simulate new parameters
        trajectory.append(orbits[key].state)
    trajectory = np.array(trajectory)

    if len(orbits) >= 1:
        # Find max value of positions
        max_val = np.max(np.abs(trajectory[:,:,:3]))
        ax.set_xlim(-max_val, max_val)
        ax.set_ylim(-max_val, max_val)
        ax.set_zlim(-max_val, max_val)


        for key, traj in zip(orbits.keys(), trajectory):
            traj, = ax.plot(traj[:,0], traj[:,1], traj[:,2], lw=2, zorder=100)
            traj.set_label(key)
        ax.legend()

    return fig

# Returns the KOE over time for a orbit
def plot_vars(orbit, reSimulate = False, args = {}, title='Kepler\'s Elements'):
    fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(10, 5))
    fig.suptitle(title)
    width = 0.8
    size_font = 5
    for ax in axs.flat:
        ax.tick_params(axis='both', which='major', labelsize=5)
        ax.set_ylabel('', fontsize=size_font)
        ax.set_xlabel('', fontsize=size_font)
        ax.set_title('', fontsize=size_font)

    # [a, normal_e, i, ta, aop, an]
    orbit.t_steps /= 3600 # per hour

    if reSimulate:
        orbit.koe_propagation()

    # plot true anomaly
    axs[0, 0].plot(orbit.t_steps, orbit.koe_t[:, 3], lw=width)
    axs[0, 0].grid(True)
    axs[0, 0].set_title('True Anomaly vs Time')
    axs[0, 0].set_ylabel('Angle (Deg)')

    # plot semi major
    axs[1, 2].plot(orbit.t_steps, orbit.koe_t[:, 0], lw=width)
    axs[1, 2].grid(True)
    axs[1, 2].set_title('Semi-Major Axis vs Time')
    axs[1, 2].set_ylabel('Semi-Major Axis (KM)')

    # plot eccentricity
    axs[0, 1].plot(orbit.t_steps, orbit.koe_t[:, 1], lw=width)
    axs[0, 1].grid(True)
    axs[0, 1].set_title('Eccentricity vs Time')

    # plot argument of periapsis
    axs[0, 2].plot(orbit.t_steps, orbit.koe_t[:, 4], lw=width)
    axs[0, 2].grid(True)
    axs[0, 2].set_title('Argument of Periapsis vs Time')

    # plot inclination
    axs[1, 1].plot(orbit.t_steps, orbit.koe_t[:, 2], lw=width)
    axs[1, 1].grid(True)
    axs[1, 1].set_title('Inclination vs Time')

    # plot Ascending Node
    axs[1, 0].plot(orbit.t_steps, orbit.koe_t[:, 5], lw=width)
    axs[1, 0].grid(True)
    axs[1, 0].set_title('Ascending Node vs Time')
    axs[1, 0].set_ylabel('Angle (Deg)')

    return fig

# Return the orbital state space plot of an orbit
def plot_state_space(orbit, reSimulate = False, args=None):
    if args is None:
        args = {}
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(10, 6))
    fig.suptitle('Orbital State Space')

    if reSimulate:
        orbit.propagate_orbit()

    # Plot angular Momentum vs Time
    angular_momentum = np.cross(orbit.state[:, :3], orbit.state[:, 3:6], axis=1)
    axs[0].plot(orbit.t_steps, np.round(np.linalg.norm(angular_momentum, axis=1)))
    axs[0].grid(True)
    axs[0].set_title('Angular Momentum[km^2/s] vs Time')
    axs[0].set_xlabel('Time [sec]')

    # Plot position vs Time
    axs[1].plot(orbit.t_steps, orbit.state[:, 0], label='x')
    axs[1].plot(orbit.t_steps, orbit.state[:, 1], label='y')
    axs[1].plot(orbit.t_steps, orbit.state[:, 2], label='z')
    axs[1].grid(True)
    axs[1].set_title('Position[km] vs Time')
    axs[1].set_xlabel('Time [sec]')
    axs[1].legend()

    # Plot velocity vs Time
    axs[2].plot(orbit.t_steps, orbit.state[:, 3], label='vx')
    axs[2].plot(orbit.t_steps, orbit.state[:, 4], label='vy')
    axs[2].plot(orbit.t_steps, orbit.state[:, 5], label='vz')
    axs[2].grid(True)
    axs[2].set_title('Velocity[Km/2] vs Time')
    axs[2].set_xlabel('Time [sec]')
    axs[2].legend()

    fig.tight_layout()
    return fig

# Animate coastlines based on time
def animate_coastlines(orbit):
    coastline_latlong = np.genfromtxt('Spice/coastlines.csv', delimiter=',')
    coastline_latlong = coastline_latlong[:, [1, 0]]  # Columns are [Latitude, Longitude]
    n_points = len(coastline_latlong)
    states = np.full(n_points, pd.Earth['radius'])

    # Convert lat-long to ecef coordinates
    r_states = np.column_stack((coastline_latlong[:, 0], coastline_latlong[:, 1], states))
    ecef_states = ft.latlong2ecef(r_states)

    # Initialize eci array with correct shape: (step_n, n_points, 3)
    eci = np.zeros((orbit.step_n, n_points, 3))

    # Calculate time steps for each frame
    timesteps = np.linspace(orbit.args['tSpan'][0], orbit.args['tSpan'][-1], orbit.step_n)

    # Convert ecef to eci for each timestep
    for i, t in enumerate(timesteps):
        eci[i] = ft.ecef2eci(ecef_states, orbit.et0 + t)

    return eci


# Animate Orbits and Coastlines
def animate_Orbits(orbits, reSimulate=False, args={}):
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Set Graph Parameters
    ax.set_xlabel('X [km]')
    ax.set_ylabel('Y [km]')
    ax.set_zlabel('Z [km]')
    ax.set_aspect('equal')
    ax.set_title('Orbital Trajectories')

    # Propagate Orbits and setup trajectories
    trajectory = []
    for key in orbits:
        if reSimulate:
            orbits[key].update_args(args)
            orbits[key].propagate_orbit()
        trajectory.append(orbits[key].state)
    trajectory = np.array(trajectory)

    if len(orbits) >= 1:
        # Find max value of positions
        max_val = np.max(np.abs(trajectory[:,:,:3]))
        ax.set_xlim(-max_val, max_val)
        ax.set_ylim(-max_val, max_val)
        ax.set_zlim(-max_val, max_val)

        # Plot Earth without coastlines initially
        plot_central_body(ax, {'map': False})

        # Setup coastline data at initial time
        first_key = next(iter(orbits))
        refOrbit = orbits[first_key]

        eci = animate_coastlines(refOrbit)

        # Setup lines for orbits
        coastlines, = ax.plot(eci[0, :, 0], eci[0, :, 1], eci[0, :, 2], 'ko',markersize=0.3, zorder=-10, alpha=0.5)
        lines = [ax.plot([], [], [], lw=2, zorder=10)[0] for _ in range(len(orbits))]
        title = ax.set_title("Time: 0 s")

        def init():
            for line in lines:
                line.set_data([], [])
                line.set_3d_properties([])
            return lines + [coastlines]

        def animate(i):
            #Update orbit trajectories
            for key, traj, line in zip(orbits.keys(), trajectory, lines):
                x, y, z = traj[:i, 0], traj[:i, 1], traj[:i, 2]
                line.set_data(x, y)
                line.set_3d_properties(z)
                line.set_label(key)
                ax.legend()
                ax.set_title("Time: " + str(refOrbit.args['dt'] * i))

            # Update coastlines to simulate Earth's rotation
            coastlines.set_data(eci[i, :, 0], eci[i, :, 1])
            coastlines.set_3d_properties(eci[i, :, 2])

            # Update title
            current_time = refOrbit.args['dt'] * i
            print(current_time / 86400)
            ax.set_title(current_time)

            return lines + [coastlines]

        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=refOrbit.step_n, interval=50, blit=True)
        return anim, fig

def animate_groundtracks(orbits, reSimulate=False, args=None):
    if args is None:
        args = {}
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot()

    ax.set_title('Ground Tracks')
    ax.set_xlabel('Longitude [Deg]')
    ax.set_ylabel('Latitude [Deg]')

    first_key = next(iter(orbits))
    refOrbit = orbits[first_key]

    tracks = []
    for key in orbits:
        if reSimulate:
            orbits[key].update_args(args)
            orbits[key].propagate_orbit()  # Simulate new parameters
            orbits[key].latlongs()  # Simulate tracks
        tracks.append(orbits[key].latlong)
    tracks = np.array(tracks)

    # [point, [log, lat]]
    coastline_latlong = np.genfromtxt('Spice/coastlines.csv', delimiter=',')
    ax.plot(coastline_latlong[:, 0], coastline_latlong[:, 1], 'mo', markersize=0.3)

    # Setup lines for orbits
    lines = [ax.plot([], [], 'o', markersize=0.5)[0] for _ in range(len(orbits))]

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def animate(i):
        # Update groundtracks
        for track, key, line in zip(tracks, orbits.keys(), lines):
            x, y = track[:i, 1], track[:i, 0]
            line.set_data(x, y)
            line.set_label(key)
            ax.legend()
        return lines

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=refOrbit.step_n, interval=50, blit=True)
    return  anim, fig