import h5py
import numpy as np


def dict_to_hdf5_group(group, dictionary):
    for key, value in dictionary.items():
        if isinstance(value, dict):
            subgroup = group.create_group(key)
            dict_to_hdf5_group(subgroup, value)
        else:
            if isinstance(value, list):
                value = tuple(value)
            group.attrs[key] = value


def hdf5_group_to_dict(group):
    result = {}
    for key, value in group.attrs.items():
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        result[key] = value
    for key, value in group.items():
        if isinstance(value, h5py.Group):
            result[key] = hdf5_group_to_dict(value)
        else:
            result[key] = list(value) if isinstance(
                value, h5py.Dataset) and len(value.shape) == 1 else value[()]
    return result


# Create an HDF5 file
filename = "my_file.hdf5"
hdf5_file = h5py.File(filename, mode='w')

# Create a dictionary to convert to HDF5 group
START_COMMANDS = {
    'function1': {
        'arg1': 1,
        'arg2': 2
    },
    'function2': {
        'arg1': 4,
        'arg2': 'Hello',
        'arg3': [1, 2, 3, 4]
    }
}

STOP_COMMANDS = {
    'function1': {
        'arg1': 1,
        'arg2': 2
    },
    'function2': {
        'arg1': 4,
        'arg2': 'Hello',
        'arg3': [1, 2, 3, 4]
    },
    'function3': {
        'arg1': True,
        'arg2': np.arange(10),
        'arg1': ['hello', 'goodbye']
    }
}

# Convert dictionary to HDF5 group
start_group = hdf5_file.create_group("START_COMMANDS")
dict_to_hdf5_group(start_group, START_COMMANDS)

stop_group = hdf5_file.create_group("STOP_COMMANDS")
dict_to_hdf5_group(stop_group, STOP_COMMANDS)

START_COMMANDS_retrieved = hdf5_group_to_dict(start_group)
STOP_COMMANDS_retrieved = hdf5_group_to_dict(stop_group)

# Close the HDF5 file
hdf5_file.close()

print(START_COMMANDS)
print(START_COMMANDS_retrieved)

print(STOP_COMMANDS)
print(STOP_COMMANDS_retrieved)
