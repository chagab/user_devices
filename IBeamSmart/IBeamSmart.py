import serial
import re


class IBeamSmart:

    def __init__(self, USB_port):
        connection_parameters = {
            # connection parameters for the IBeamSmart (taken from the manual)
            # manuals recommand Direct connection via COMx with "115200,8,N,1"
            # and serial interface handshake “none“
            'port': USB_port,
            'baudrate': 115200,
            'bytesize':  serial.EIGHTBITS,
            'parity': serial.PARITY_NONE,
            'stopbits': serial.STOPBITS_ONE,
            'rtscts': False,
            'xonxoff': False
        }
        # first establish connection
        print(f'Initiating connection to laser on {USB_port}')
        self.ser = serial.Serial(**connection_parameters)
        print('Connection successful')
        self.set_power(1)

    def __del__(self):
        # close the serial connection before the object gets deleted
        self.set_power(0)
        self.off()
        if self.ser.is_open:
            self.ser.close()

    def send_bytes_command(self, bytes_command: bytes) -> None:
        number_of_bytes_to_write = len(bytes_command)
        number_of_bytes_written = self.ser.write(bytes_command)
        self.ser.readline()
        success = number_of_bytes_to_write == number_of_bytes_written
        assert success

    def send_str_command(self, command: str) -> None:
        bytes_command = f'{command}\r\n'.encode()
        self.send_bytes_command(bytes_command)

    def on(self) -> None:
        self.send_str_command('la on')
        print(f'status: {self.get_laser_status()}')
        print(f'power: {self.get_power()} mW')

    def off(self) -> None:
        self.send_str_command('la off')
        print(f'status: {self.get_laser_status()}')

    def set_power(self, pow: float) -> None:
        """Set the power of the laser in mW on a given channel"""
        self.send_str_command(f'ch 1 pow {pow}')
        self.send_str_command(f'ch 2 pow {pow}')
        print(f'power: {self.get_power()} mW')

    def get_power(self) -> int:
        """Return the power of the laser in mW"""
        self.send_str_command('sh pow')
        response = self.ser.readline().decode('unicode_escape')
        # a regular expression is used to find all the digit in the response
        # from the response format, we know there is only one match
        # output the power in uW, we convert it to mW
        pow_mW = int(re.findall(r'\d+', response)[0]) / 1e3
        return pow_mW

    def get_laser_status(self) -> str:
        self.send_str_command('sta la')
        response = self.ser.readline().decode('unicode_escape')[:-2]
        return response
