# from pypylon import pylon

# camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
# camera.Open()

# # demonstrate some feature access
# new_width = camera.Width.GetValue() - camera.Width.GetInc()
# if new_width >= camera.Width.GetMin():
#     camera.Width.SetValue(new_width)

# numberOfImagesToGrab = 100
# camera.StartGrabbingMax(numberOfImagesToGrab)

# while camera.IsGrabbing():
#     grabResult = camera.RetrieveResult(
#         5000, pylon.TimeoutHandling_ThrowException)

#     if grabResult.GrabSucceeded():
#         # Access the image data.
#         print("SizeX: ", grabResult.Width)
#         print("SizeY: ", grabResult.Height)
#         img = grabResult.Array
#         print("Gray value of first pixel: ", img[0, 0])

#     grabResult.Release()
# camera.Close()
from pypylon import pylon
from pypylon import genicam
import time

try:
    imageWindow = pylon.PylonImageWindow()
    imageWindow.Create(1)
    print(type(imageWindow))
    # Create an instant camera object with the camera device found first.
    camera = pylon.InstantCamera(
        pylon.TlFactory.GetInstance().CreateFirstDevice())

    # Print the model name of the camera.
    print("Using device ", camera.GetDeviceInfo().GetModelName())
    print("Using device ", camera.GetDeviceInfo().GetModelSerialNumber())

    # Start the grabbing of c_countOfImagesToGrab images.
    # The camera device is parameterized with a default configuration which
    # sets up free-running continuous acquisition.
    camera.StartGrabbingMax(10000, pylon.GrabStrategy_LatestImageOnly)

    while camera.IsGrabbing():
        # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
        grabResult = camera.RetrieveResult(
            5000, pylon.TimeoutHandling_ThrowException)

        # Image grabbed successfully?
        if grabResult.GrabSucceeded():
            imageWindow.SetImage(grabResult)
            imageWindow.Show()
        else:
            print("Error: ",
                  grabResult.ErrorCode)  # grabResult.ErrorDescription does not work properly in python could throw UnicodeDecodeError
        grabResult.Release()
        time.sleep(0.05)

        if not imageWindow.IsVisible():
            camera.StopGrabbing()

    # camera has to be closed manually
    camera.Close()
    # imageWindow has to be closed manually
    imageWindow.Close()

except genicam.GenericException as e:
    # Error handling.
    print("An exception occurred.")
    print(e.GetDescription())
