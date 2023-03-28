from labscript_devices import register_classes

register_classes(
    'MeadowlarkSLM',
    BLACS_tab='user_devices.MeadowlarkSLM.blacs_tab.MeadowlarkSLMTab',
    runviewer_parser=None
)
