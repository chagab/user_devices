from blacs.tab_base_classes import Worker
from labscript_utils import properties
from user_devices.MeadowlarkSLM.MeadowlarkSLM import MeadowlarkSLM
# import h5py


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

    def load_image(self, image_path):
        self.slm.load_image(image_path)
        self.slm.reset_slm()
        self.slm.write_image()
