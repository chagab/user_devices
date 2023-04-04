from labscript_devices import register_classes

register_classes(
    'HamamatsuDCAM',
    BLACS_tab='labscript_devices.HamamatsuDCAM.blacs_tabs.HamamatsuDCAMTab',
    runviewer_parser=None,
)
