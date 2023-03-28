from labscript_devices import register_classes

register_classes(
    'LLSLaserArray',
    BLACS_tab='user_devices.LLSLaserArray.blacs_tab.LLSLaserArrayTab',
    runviewer_parser=None
)
