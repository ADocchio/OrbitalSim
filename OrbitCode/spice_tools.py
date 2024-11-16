import spiceypy as spice
import numpy as np

# Fetches Objects from SPK files to be used in program
def get_objects(filename, display=False):
    objects = spice.spkobj(filename)  # Get objects from the SPK file
    ids, names, tcs_sec, tcs_cal = [], [], [], []

    if display:
        print('nObjects in %s:' % filename)

    for obj_id in objects:  #for each object read from the spice file
        ids.append(obj_id)  #append its id

        # Get the coverage window for this object
        coverages = spice.spkcov(filename, obj_id)

        if len(coverages) == 0:
            print(f"No coverage for object with id {obj_id}")
            continue  # Skip if there is no coverage

        # Iterate over the coverage intervals
        for i in range(0, len(coverages), 2):  #make sure to go up by 2 indexes every time
            start_time = coverages[i]
            end_time = coverages[i + 1]

            # Append time intervals in seconds since J2000
            tcs_sec.append((start_time, end_time))

            # Convert time intervals to human-readable form
            tc_cal_start = spice.timout(start_time, 'YYYY MON DD HR:MN:SC.### (TDB) ::TDB')
            tc_cal_end = spice.timout(end_time, 'YYYY MON DD HR:MN:SC.### (TDB) ::TDB')
            tcs_cal.append((tc_cal_start, tc_cal_end))

            # Get name of the body
            try:
                names.append(id2body(obj_id))
            except:
                names.append('Unknown Name')

            # Print out to console if display is enabled
            if display:
                print(f'id: {obj_id}\tname: {names[-1]}\t\tcc: {tc_cal_start} --> {tc_cal_end}')

    return ids, names, tcs_sec, tcs_cal


# Returns name of body given a SPICE ID
def id2body(id_):
    return spice.bodc2n(id_)


# Creates an array of times given time coverages
def tc2array(tcs, steps):
    arr = np.zeros((steps, 1))
    arr[:, 0] = np.linspace(tcs[0], tcs[1], steps)
    return arr


# Return State vector of an ephemeris (body) in relation to another
def get_ephemeris_states(target, times, frame, observer):
    return np.array(spice.spkezr(target, times, frame, 'NONE', observer)[0])
