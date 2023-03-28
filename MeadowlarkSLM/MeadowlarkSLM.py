import numpy as np
import ctypes
from time import sleep
from matplotlib import image


class MeadowlarkSLM:

    def __init__(self):
        # MAKE SURE THE WINDOW SHOWS UP IN THE WRITE PLACE FOR THE DPI SETTINGS
        # Query DPI Awareness (Windows 10 and 8)
        awareness = ctypes.c_int()
        errorCode = ctypes.windll.shcore.GetProcessDpiAwareness(
            0, ctypes.byref(awareness))

        # Set DPI Awareness  (Windows 10 and 8)
        errorCode = ctypes.windll.shcore.SetProcessDpiAwareness(2)
        # the argument is the awareness level, which can be 0, 1 or 2:
        # for 1-to-1 pixel control I seem to need it to be non-zero (I'm using level 2)

        # Set DPI Awareness  (Windows 7 and Vista)
        success = ctypes.windll.user32.SetProcessDPIAware()
        # behaviour on later OSes is undefined, although when I run it on my Windows 10 machine,
        # it seems to work with effects identical to SetProcessDpiAwareness(1)

        # Load the DLL
        # Blink_C_wrapper.dll, HdmiDisplay.dll, ImageGen.dll, freeglut.dll and glew64.dll
        # should all be located in the same directory as the program referencing the
        # library
        ctypes.cdll.LoadLibrary(
            "C:\\Program Files\\Meadowlark Optics\\Blink 1920 HDMI\\SDK\\Blink_C_wrapper")
        self.slm_lib = ctypes.CDLL("Blink_C_wrapper")

        # indicate that our images are RGB
        RGB = ctypes.c_uint(1)
        self.is_eight_bit_image = ctypes.c_uint(1)

        # Call the constructor
        self.slm_lib.Create_SDK()
        print("Blink SDK was successfully constructed")

        self.height = ctypes.c_uint(self.slm_lib.Get_Height())
        self.width = ctypes.c_uint(self.slm_lib.Get_Width())
        depth = ctypes.c_uint(self.slm_lib.Get_Depth())
        self.bytpesPerPixel = 4  # RGBA
        self.WFC = np.empty(
            [self.width.value*self.height.value*self.bytpesPerPixel], np.uint8, 'C')

        # ***you should replace linear.LUT with your custom LUT file***
        # but for now open a generic LUT that linearly maps input graylevels to output voltages
        # ***Using linear.LUT does NOT give a linear phase response***
        success = 0
        if self.height.value == 1152:
            lut_path = "C:\\Program Files\\Meadowlark Optics\\Blink 1920 HDMI\\LUT Files\\1920x1152_linearVoltage.lut"
        if (self.height.value == 1200) and (depth.value == 8):
            lut_path = "C:\\Program Files\\Meadowlark Optics\\Blink 1920 HDMI\\LUT Files\\19x12_8bit_linearVoltage.lut"
        if (self.height.value == 1200) and (depth.value == 10):
            lut_path = "C:\\Program Files\\Meadowlark Optics\\Blink 1920 HDMI\\LUT Files\\19x12_10bit_linearVoltage.lut"
        success = self.slm_lib.Load_lut(lut_path)
        if success > 0:
            print("LoadLUT Successful")
        else:
            print("LoadLUT Failed")

    def __del__(self):
        self.slm_lib.Delete_SDK()

    def load_image(self, image_path):
        image_full = image.imread(image_path)
        shape = image_full.shape
        self.image_to_load = np.zeros([shape[0], shape[1]])
        if len(shape) == 3:
            for i in range(shape[2]):
                self.image_to_load += image_full[:, :, i]
            self.image_to_load /= shape[2]
        self.image_to_load = self.image_to_load.astype(np.uint8).flatten('C')

    def write_image(self):
        success = self.slm_lib.Write_image(
            self.image_to_load.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)),
            self.is_eight_bit_image
        )
        if success == 1:
            print("Succes writting the image")
        elif success == 0:
            print("Failure writting the image")
        else:
            print("Error writting the image")

    def reset_slm(self):
        self.slm_lib.Write_image(
            self.WFC.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)),
            self.is_eight_bit_image
        )
        sleep(1 / 30)
