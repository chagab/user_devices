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

    def generate_code(self, hdf5_file):
        Device.generate_code(self, hdf5_file)
