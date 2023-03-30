from blacs.tab_base_classes import Worker
# This needs to be imported to use h5py
import labscript_utils.h5_lock
import h5py


class MPBCFiberLasertWorker(Worker):

    def init(self):
        """This method initialises communications with the device. Not to be
        confused with the standard python class __init__ method."""
        global MPBCFiberLaser
        from .MPBCFiberLaser import MPBCFiberLaser
        self.MPBCFiberLaser = MPBCFiberLaser(self.USB_port)
        # Each shot, we will remember the shot file for the duration of that shot
        self.shot_file = None

    def program_manual(self, values):
        """This method allows for user control of the device via the BLACS_tab,
        setting outputs to the values set in the BLACS_tab widgets."""
        if values['ON']:
            self.MPBCFiberLaser.on()
        else:
            self.MPBCFiberLaser.off()

        self.MPBCFiberLaser.set_power(values['Power'])

    def check_remote_values(self):
        """This method reads the current settings of the device, updating the
        BLACS_tab widgets to reflect these values."""
        current_settings = {
            'Power': self.MPBCFiberLaser.get_power(),
            'ON': self.MPBCFiberLaser.get_laser_status() == 'ON'
        }
        return current_settings

    def transition_to_buffered(self, device_name, h5_file, front_panel_values, refresh):
        """This method transitions the device to buffered shot mode, reading the
        shot h5 file and taking the saved instructions from
        labscript_device.generate_code and sending the appropriate commands to
        the hardware."""
        print(front_panel_values)
        self.shot_file = h5_file  # We'll need this in transition_to_manual
        with h5py.File(self.shot_file, 'r') as hdf5_file:
            group = hdf5_file[f'devices/{self.device_name}']
            if 'START_COMMANDS' in group:
                start_commands = group['START_COMMANDS'][:]
            else:
                start_commands = None
        # It is polite to close the shot file (by exiting the 'with' block) before
        # communicating with the hardware, because other processes cannot open the file
        # whilst we still have it open
        for command in start_commands:
            print(f'sending command: {command}')
            self.MPBCFiberLaser.send_bytes_command(command)
        return {}

    def transition_to_manual(self):
        """This method transitions the device from buffered to manual mode. It
        does any necessary configuration to take the device out of buffered mode
        and is used to read any measurements and save them to the shot h5 file
        as results."""
        with h5py.File(self.shot_file, 'r') as hdf5_file:
            group = hdf5_file[f'devices/{self.device_name}']
            if 'STOP_COMMANDS' in group:
                stop_commands = group['STOP_COMMANDS'][:]
            else:
                stop_commands = None
        # It is polite to close the shot file (by exiting the 'with' block) before
        # communicating with the hardware, because other processes cannot open the file
        # whilst we still have it open
        for command in stop_commands:
            print(f'sending command: {command}')
            self.MPBCFiberLaser.send_bytes_command(command)
        return True

    def shutdown(self):
        # Called when BLACS closes
        del self.MPBCFiberLaser

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
        return True  # Indicates success
