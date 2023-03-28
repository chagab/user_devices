from labscript_devices import register_classes

register_classes(
    'MPBCFiberLaser',
    BLACS_tab='user_devices.MPBCFiberLaser.blacs_tab.MPBCFiberLaserTab',
    runviewer_parser=None
)
