from blacs.tab_base_classes import Worker
from user_devices.IBeamSmart.IBeamSmart import IBeamSmart
from user_devices.MPBCFiberLaser.MPBCFiberLaser import MPBCFiberLaser


class LLSLaserArrayWorker(Worker):

    def init(self):
        """This method initialises communications with the device. Not to be
        confused with the standard python class __init__ method."""
        self.lasers = {}
        for wavelength, COMport in self.USB_ports.items():
            try:
                if wavelength == '403nm' or wavelength == '444nm':
                    self.lasers[wavelength] = IBeamSmart(COMport)
                else:
                    self.lasers[wavelength] = MPBCFiberLaser(COMport)
            except:
                print(f"Laser {wavelength} could not be created on {COMport}")
                self.lasers[wavelength] = None

    def program_manual(self, values):
        """This method allows for user control of the device via the BLACS_tab,
        setting outputs to the values set in the BLACS_tab widgets."""
        for wavelength, _ in self.USB_ports.items():
            if self.lasers[wavelength] != None:
                if values[f'ON {wavelength}'] == True:
                    self.lasers[wavelength].on()
                    print(f'Laser {wavelength} is ON')
                if values[f'ON {wavelength}'] == False:
                    self.lasers[wavelength].off()
                    print(f'Laser {wavelength} is OFF')
                power = values[f'Power {wavelength}']
                self.lasers[wavelength].set_power(power)
                print(f'Laser {wavelength} power is {power}')
            else:
                print(f'Laser {wavelength} is not connected')
        print()

    def check_remote_values(self):
        """This method reads the current settings of the device, updating the
        BLACS_tab widgets to reflect these values."""
        pass

    def transition_to_buffered(self, device_name, h5file, front_panel_values, refresh):
        """This method transitions the device to buffered shot mode, reading the
        shot h5 file and taking the saved instructions from
        labscript_device.generate_code and sending the appropriate commands to
        the hardware."""
        return {}

    def transition_to_manual(self):
        """This method transitions the device from buffered to manual mode. It
        does any necessary configuration to take the device out of buffered mode
        and is used to read any measurements and save them to the shot h5 file
        as results."""
        return True
