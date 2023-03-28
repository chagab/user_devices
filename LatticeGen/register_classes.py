from labscript_devices import register_classes

register_classes(
    'LatticeGen',
    BLACS_tab='user_devices.LatticeGen.blacs_tab.LatticeGenTab',
    runviewer_parser=None
)
