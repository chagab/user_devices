from labscript import Device, set_passed_properties
import h5py
import numpy as np

class LLSLaserArray(Device):
    """A labscript_device for LLS Laser Array
    serial interface.
        - connection_table_properties (set once)
        - termination: character signalling end of response

    device_properties (set per shot):
        - timeout: in seconds for response to queries over visa interface
    """

    description = 'LLS Laser Array'

    @set_passed_properties(
        property_names={
            'connection_table_properties': ['USB_ports'],
            'device_properties': []
        }
    )
    def __init__(self, name, addr, USB_ports, **kwargs):
        Device.__init__(
            self, name=name, parent_device=None, connection=addr, **kwargs
        )
        self.name = name
        self.BLACS_connection = addr
        self.USB_ports = USB_ports
        self.start_commands = {
            '403nm': [],
            '444nm': [],
            '488nm': [],
            '514nm': [],
            '560nm': [],
            '607nm': [],
            '642nm': []
        }
        self.stop_commands = {
            '403nm': [],
            '444nm': [],
            '488nm': [],
            '514nm': [],
            '560nm': [],
            '607nm': [],
            '642nm': []
        }

    def add_start_command(self, wavelenght, command):
        """Add a serial command that should be send at the start of the experiment"""
        if not isinstance(command, bytes):
            raise TypeError("command must be a bytestring")
        self.start_commands[f'{wavelenght}nm'].append(command)

    def add_stop_command(self, wavelenght, command):
        """Add a serial command that should be send at the end of the experiment"""
        if not isinstance(command, bytes):
            raise TypeError("command must be a bytestring")
        self.stop_commands[f'{wavelenght}nm'].append(command)
    
    def init(self, wavelenght, power: float) -> None:
        if int(wavelenght) in [403, 444]:
            self.add_start_command(wavelenght, b"la on\r\n")
            self.add_start_command(wavelenght, f'ch 1 pow {power}\r\n'.encode())
            self.add_start_command(wavelenght, f'ch 2 pow {power}\r\n'.encode())
        elif int(wavelenght) in [488, 514, 560, 607, 642]:
            pass # TODO : implement the function for the MPB lasers as well
        else:
            print("Error with the wavelength")

    def terminate(self, wavelenght) -> None:
        if int(wavelenght) in [403, 444]:
            self.add_stop_command(wavelenght, b'ch 1 pow 0\r\n')
            self.add_stop_command(wavelenght, b'ch 2 pow 0\r\n')
            self.add_stop_command(wavelenght, b'la off\r\n')
        elif int(wavelenght) in [488, 514, 560, 607, 642]:
            pass # TODO : implement the function for the MPB lasers as well
        else:
            print("Error with the wavelength")

    def generate_code(self, hdf5_file):
        # Convert the lists of commands into numpy arrays and save them to the shot file
        # as HDF5 datasets within our device's group:
        group = self.init_device_group(hdf5_file)
        start_group = group.create_group('START_COMMANDS')
        stop_group = group.create_group('STOP_COMMANDS')
        self.dict_to_hdf5_group(start_group, self.start_commands)
        self.dict_to_hdf5_group(stop_group, self.stop_commands)

    def dict_to_hdf5_group(self, group, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                subgroup = group.create_group(key)
                self.dict_to_hdf5_group(subgroup, value)
            else:
                if isinstance(value, list):
                    value = tuple(value)
                group.attrs[key] = value