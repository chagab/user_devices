from labscript import Device, set_passed_properties
from numpy import dtype


class LatticeGen(Device):
    """A labscript_device for IBeamSmart laser from Toptica using a
    serial interface.
        - connection_table_properties (set once)
        - termination: character signalling end of response

    device_properties (set per shot):
        - timeout: in seconds for response to queries over visa interface
        - 
    """

    description = 'A GUI to generate lattice HEX mask for the SLM'

    @set_passed_properties(
        property_names={
            'connection_table_properties': [],
            'device_properties': []
        }
    )
    def __init__(self, name, addr, **kwargs):
        Device.__init__(
            self, name=name, parent_device=None, connection=addr, **kwargs
        )
        self.name = name
        self.BLACS_connection = addr
        self.start_commands = {}
        self.stop_commands = {}
    
    def dict_to_hdf5_group(self, group, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                subgroup = group.create_group(key)
                self.dict_to_hdf5_group(subgroup, value)
            else:
                if isinstance(value, list):
                    value = tuple(value)
                group.attrs[key] = value
    
    def add_start_command(self, command):
        """Add a serial command that should be send at the start of the experiment"""
        if not isinstance(command, dict):
            raise TypeError("command must be a dict")
        for command, argument in command.items():
            self.start_commands[command] = argument
    
    def add_stop_command(self, command):
        """Add an instruction that should be done at the end of the experiment"""
        if not isinstance(command, dict):
            raise TypeError("command must be a dict")
        for command, argument in command.items():
            self.stop_commands[command] = argument

    def generate_code(self, hdf5_file):
        group = self.init_device_group(hdf5_file)
        start_group = group.create_group('START_COMMANDS')
        stop_group = group.create_group('STOP_COMMANDS')
        if len(self.start_commands) > 0:
            self.dict_to_hdf5_group(start_group, self.start_commands)
        else:
            print("No start commands")
        if len(self.stop_commands) > 0:
            self.dict_to_hdf5_group(stop_group, self.stop_commands)
        else:
            print("No stop commands")

    def generate_pattern(self, mode, params):
        assert mode in ["square", "hex", "ronchi"]
        self.add_start_command({
            'generate_pattern': {
                'mode' : mode,
                'params' : params
            }
        })
