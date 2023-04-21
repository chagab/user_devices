from blacs.tab_base_classes import Worker
from labscript_utils import properties
from user_devices.MeadowlarkSLM.MeadowlarkSLM import MeadowlarkSLM
import labscript_utils.h5_lock
import h5py
import os


class MeadowlarkSLMWorker(Worker):

    def init(self):
        """This method initialises communications with the device. Not to be
        confused with the standard python class __init__ method."""
        self.slm = MeadowlarkSLM()

    def program_manual(self, values):
        """This method allows for user control of the device via the BLACS_tab,
        setting outputs to the values set in the BLACS_tab widgets."""
        pass

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
        
        for command, argument in start_commands_dict.items():
            print(argument)
            if argument is '':
                print('argument is none')
                getattr(self, command)()
            else:
                print('argument is not none')
                getattr(self, command)(**argument)
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
            
        for command, argument in stop_commands_dict.items():
            print(f'sending command: {command}')
            if argument is '':
                getattr(self, command)()
            else: 
                getattr(self, command)(**argument)
        return True
    
    def abort_buffered(self):
        # Called when a shot is aborted. We may or may not want to run
        # transition_to_manual in this case. If not, then this method should do whatever
        # else it needs to, and then return True. It should make sure to clear any state
        # were storing about this shot (e.g. it should set self.shot_file = None)
        return self.transition_to_manual()

    def abort_transition_to_buffered(self):
        # Called when a shot is aborted. We may or may not want to run
        # transition_to_manual in this case. If not, then this method should do whatever
        # else it needs to, and then return True. It should make sure to clear any state
        # were storing about this shot (e.g. it should set self.shot_file = None)
        return self.transition_to_manual()
    
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

    def load_image(self, image_path=None):
        if image_path is None:
            shot_dir = os.path.split(self.shot_file)[0]
            ext = ".bmp"
            # Get a list of all the .bmp files in the current shot directory 
            file_list = [f for f in os.listdir(shot_dir) if f.endswith(ext)]
            # Sort the file list by creation date
            file_list.sort(key=lambda x: os.stat(os.path.join(shot_dir, x)).st_ctime)
            image_path = shot_dir + file_list[0]
        self.slm.load_image(image_path)
        self.slm.reset_slm()
        self.slm.write_image()
