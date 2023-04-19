from blacs.tab_base_classes import Worker
from user_devices.IBeamSmart.IBeamSmart import IBeamSmart
from user_devices.MPBCFiberLaser.MPBCFiberLaser import MPBCFiberLaser
import labscript_utils.h5_lock
import h5py

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

    def transition_to_buffered(self, device_name, h5_file, front_panel_values, refresh):
        """This method transitions the device to buffered shot mode, reading the
        shot h5 file and taking the saved instructions from
        labscript_device.generate_code and sending the appropriate commands to
        the hardware."""
        self.shot_file = h5_file  # We'll need this in transition_to_manual
        with h5py.File(self.shot_file, 'r') as hdf5_file:
            group = hdf5_file[f'devices/{self.device_name}']
            if 'START_COMMANDS' in group:
                start_commands = group['START_COMMANDS']
                start_commands_dict = self.hdf5_group_to_dict(start_commands)
            else:
                start_commands = None
                start_commands_dict = None
        
        for wavelength, commands in start_commands_dict.items():
            for command in commands:
                print(f'sending command: {command} to laser {wavelength}')
                self.lasers[wavelength].send_str_command(command)
        return {}

    def transition_to_manual(self):
        """This method transitions the device from buffered to manual mode. It
        does any necessary configuration to take the device out of buffered mode
        and is used to read any measurements and save them to the shot h5 file
        as results."""
        with h5py.File(self.shot_file, 'r') as hdf5_file:
            group = hdf5_file[f'devices/{self.device_name}']
            if 'STOP_COMMANDS' in group:
                stop_commands = group['STOP_COMMANDS']
                stop_commands_dict = self.hdf5_group_to_dict(stop_commands)
            else:
                stop_commands = None
                stop_commands_dict = None 
            
        for wavelength, commands in stop_commands_dict.items():
            for command in commands:
                print(f'sending command: {command} to laser {wavelength}')
                self.lasers[wavelength].send_str_command(command)
        return True
    

    def abort_buffered(self):
        # Called when a shot is aborted. We may or may not want to run
        # transition_to_manual in this case. If not, then this method should do whatever
        # else it needs to, and then return True. It should make sure to clear any state
        # were storing about this shot (e.g. it should set self.shot_file = None)
        return self.transition_to_manual()
    
    def abort_transition_to_buffered(self):
        # This is called if transition_to_buffered fails with an exception or returns
        # False.
        # Forget the shot file:
        self.shot_file = None
        print("transition_to_buffered failed")
        return True  # Indicates success

    def hdf5_group_to_dict(self, group):
        """Helper functions that convert a hdf5 group to a dict which keys are 
        functions to excute and values the corresponding arguments."""
        result = {}
        for key, value in group.attrs.items():
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            result[key] = value
        for key, value in group.items():
            if isinstance(value, h5py.Group):
                result[key] = self.hdf5_group_to_dict(value)
            else:
                result[key] = list(value) if \
                isinstance(value, h5py.Dataset) and len(value.shape) == 1 else value[()]
        return result