# Gravitational constant in km^3 kg^-1 s^-2
G = 6.67430e-20  # in km^3 kg^-1 s^-2

# Planetary data for the Solar System
Sun = {
    'name': 'Sun',
    'mass': 1.9885e30,  # in kg
    'radius': 696340.0,  # in kilometers
    'distance_from_sun': 0.0,  # in kilometers (Sun is at the center)
    'orbital_period': 0.0,  # in seconds (Sun does not orbit itself)
    'mu': G * 1.9885e30,  # gravitational parameter in km^3/s^2
    'J2': 0.0, # J2 value (Sun is nearly a perfect sphere)
    'G1': 1.0e8 # in kg-km^3/s^2-m^2
}

Mercury = {
    'name': 'Mercury',
    'mass': 3.301e23,  # in kg
    'radius': 2439.7,  # in kilometers
    'distance_from_sun': 57.91e6,  # in kilometers
    'orbital_period': 88 * 24 * 3600,  # in seconds (88 Earth days)
    'mu': G * 3.301e23,  # gravitational parameter in km^3/s^2
    'J2': 6.0e-6  # J2 value
}

Venus = {
    'name': 'Venus',
    'mass': 4.867e24,  # in kg
    'radius': 6051.8,  # in kilometers
    'distance_from_sun': 108.2e6,  # in kilometers
    'orbital_period': 225 * 24 * 3600,  # in seconds (225 Earth days)
    'mu': G * 4.867e24,  # gravitational parameter in km^3/s^2
    'J2': 4.458e-6  # J2 value
}

Earth = {
    'name': 'Earth',
    'mass': 5.972e24,  # in kg
    'radius': 6371.0,  # in kilometers
    'distance_from_sun': 149.6e6,  # in kilometers
    'orbital_period': 365.25 * 24 * 3600,  # in seconds (1 Earth year)
    'mu': G * 5.972e24,  # gravitational parameter in km^3/s^2
    'J2': 1.08263e-3  # J2 value
}


Moon = {
    'name': 'Moon',
    'mass': 7.34767309e22,  # in kg
    'radius': 1737.4,  # in kilometers
    'distance_from_earth': 384400.0,  # in kilometers (mean distance to Earth)
    'orbital_period': 27.321661 * 86400,  # in seconds (sidereal period in days -> seconds)
    'mu': G * 7.34767309e22 * 1e-9,  # gravitational parameter in km^3/s^2
    'J2': 0.0002027,  # J2 value for the Moon
    'G1': 0.0  # Higher-order gravitational moments are negligible for most Moon applications
}

Mars = {
    'name': 'Mars',
    'mass': 6.417e23,  # in kg
    'radius': 3389.5,  # in kilometers
    'distance_from_sun': 227.9e6,  # in kilometers
    'orbital_period': 687 * 24 * 3600,  # in seconds (687 Earth days)
    'mu': G * 6.417e23,  # gravitational parameter in km^3/s^2
    'J2': 1.96045e-3  # J2 value
}

Jupiter = {
    'name': 'Jupiter',
    'mass': 1.898e27,  # in kg
    'radius': 69911,  # in kilometers
    'distance_from_sun': 778.5e6,  # in kilometers
    'orbital_period': 4333 * 24 * 3600,  # in seconds (4333 Earth days)
    'mu': G * 1.898e27,  # gravitational parameter in km^3/s^2
    'J2': 1.4736e-2  # J2 value
}

Saturn = {
    'name': 'Saturn',
    'mass': 5.683e26,  # in kg
    'radius': 58232,  # in kilometers
    'distance_from_sun': 1.434e9,  # in kilometers
    'orbital_period': 10759 * 24 * 3600,  # in seconds (10759 Earth days)
    'mu': G * 5.683e26,  # gravitational parameter in km^3/s^2
    'J2': 1.6298e-2  # J2 value
}

Uranus = {
    'name': 'Uranus',
    'mass': 8.681e25,  # in kg
    'radius': 25362,  # in kilometers
    'distance_from_sun': 2.871e9,  # in kilometers
    'orbital_period': 30687 * 24 * 3600,  # in seconds (30687 Earth days)
    'mu': G * 8.681e25,  # gravitational parameter in km^3/s^2
    'J2': 3.34343e-3  # J2 value
}

Neptune = {
    'name': 'Neptune',
    'mass': 1.024e26,  # in kg
    'radius': 24622,  # in kilometers
    'distance_from_sun': 4.495e9,  # in kilometers
    'orbital_period': 60190 * 24 * 3600,  # in seconds (60190 Earth days)
    'mu': G * 1.024e26,  # gravitational parameter in km^3/s^2
    'J2': 3.411e-3  # J2 value
}

Pluto = {
    'name': 'Pluto',
    'mass': 1.303e22,  # in kg
    'radius': 1188.3,  # in kilometers
    'distance_from_sun': 5.906e9,  # in kilometers
    'orbital_period': 90560 * 24 * 3600,  # in seconds (90560 Earth days)
    'mu': G * 1.303e22,  # gravitational parameter in km^3/s^2
    'J2': None  # J2 is not applicable for Pluto
}
