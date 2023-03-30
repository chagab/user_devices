
from labscript import Device, set_passed_properties
import h5py
import numpy as np


class MPBCFiberLaser(Device):
    """A labscript_device for MPBCFiberLaser laser from Toptica using a
    serial interface.
        - connection_table_properties (set once)
        - termination: character signalling end of response

    device_properties (set per shot):
        - timeout: in seconds for response to queries over visa interface
        - 
    """

    description = 'Fiber laser from MPB'

    @set_passed_properties(
        property_names={
            'connection_table_properties': ['USB_port'],
            'device_properties': []
        }
    )
    def __init__(self, name, addr, USB_port, **kwargs):
        Device.__init__(
            self, name=name, parent_device=None, connection=addr, **kwargs
        )
        self.name = name
        self.BLACS_connection = addr
        self.USB_port = USB_port
        self.start_commands = []
        self.stop_commands = []

    def add_start_command(self, command):
        """Add a serial command that should be send at the start of the experiment"""
        if not isinstance(command, bytes):
            raise TypeError("command must be a bytestring")
        self.start_commands.append(command)

    def add_stop_command(self, command):
        """Add a serial command that should be send at the end of the experiment"""
        if not isinstance(command, bytes):
            raise TypeError("command must be a bytestring")
        self.stop_commands.append(command)

    def init(self, power: float) -> None:
        self.add_start_command(b"setLDenable 1\r\n")
        self.add_start_command(f'Setpower 0 {power}\r\n'.encode())

    def terminate(self) -> None:
        self.add_stop_command(b'Setpower 0 0\r\n')
        self.add_stop_command(b'setLDenable 0\r\n')

    def generate_code(self, hdf5_file):
        # Convert the lists of commands into numpy arrays and save them to the shot file
        # as HDF5 datasets within our device's group:
        vlenbytes = h5py.special_dtype(vlen=bytes)
        start_commands = np.array(self.start_commands, dtype=vlenbytes)
        stop_commands = np.array(self.stop_commands, dtype=vlenbytes)
        group = self.init_device_group(hdf5_file)
        if self.start_commands:
            group.create_dataset('START_COMMANDS', data=start_commands)
        if self.stop_commands:
            group.create_dataset('STOP_COMMANDS', data=stop_commands)
