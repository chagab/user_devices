from labscript_devices.IMAQdxCamera.blacs_tabs import IMAQdxCameraTab

class HamamatsuDCAMTab(IMAQdxCameraTab):

    worker_class = 'labscript_devices.HamamatsuDCAM.blacs_workers.HamamatsuDCAMWorker'