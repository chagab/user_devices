import serial
import re


class MPBCFiberLaser:

    def __init__(self, USB_port):
        connection_parameters = {
            # connection parameters for the MPBCFiberLaser (taken from the manual)
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
        print('Initiating connection to laser on ' + USB_port)
        self.ser = serial.Serial(**connection_parameters)
        print('Connection successful')
        self.set_power(1)

    def __del__(self):
        # clsoe the serial connection before the object gets deleted
        self.set_power(0)
        self.off()
        if self.ser.is_open:
            self.ser.close()

    def on(self) -> None:
        self.ser.write(b'setLDenable 1 \r')
        print('status: ' + self.get_laser_status())
        print('power: {} mW'.format(self.get_power()))

    def off(self) -> None:
        self.ser.write(b'setLDenable 0 \r')
        print('status: ' + self.get_laser_status())

    def set_power(self, pow: float) -> None:
        """Set laser output power setpoint in mW"""
        self.ser.write('Setpower 0 {}\r'.format(pow).encode())
        print('power: {} mW'.format(self.get_power()))

    def get_power(self) -> int:
        """Return monitored laser output power in mW"""
        self.ser.write(b'Power 0\r')
        response = self.ser.readline().decode('unicode_escape')
        # a regular expression is used to find all the digit in the response
        # from the response format, we know there is only one match
        # output the power in uW, we convert it to mW
        pow_mW = float(re.findall(r'\d+', response)[0])
        return pow_mW

    def get_laser_status(self) -> str:
        self.ser.write(b'getLDenable\r')
        response = self.ser.readline().decode('unicode_escape')
        if response == 0:
            return "OFF"
        elif response == 1:
            return "ON"
        else:
            return "ERROR LASER STATUS"
