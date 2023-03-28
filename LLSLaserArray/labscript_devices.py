from labscript import Device, set_passed_properties


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
            'device_properties': ['power_boundaries']
        }
    )
    def __init__(self, name, addr, USB_ports, power_boundaries, **kwargs):
        Device.__init__(
            self, name=name, parent_device=None, connection=addr, **kwargs
        )
        self.name = name
        self.BLACS_connection = addr
        self.USB_ports = USB_ports
        self.power_boundaries = power_boundaries

    def generate_code(self, hdf5_file):
        Device.generate_code(self, hdf5_file)
