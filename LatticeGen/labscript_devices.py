from labscript import Device, set_passed_properties


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
        self.start_commands = []
    
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
        if not isinstance(command, bytes):
            raise TypeError("command must be a bytestring")
        self.start_commands.append(command)
    

    def test(self, arg):
        self.add_start_command({
            'test': arg
        })

    def generate_code(self, hdf5_file):
        group = self.init_device_group(hdf5_file)
        if len(self.start_commands) > 0:
            self.dict_to_hdf5_group(group, self.start_commands)
        else:
            print("No start commands")
