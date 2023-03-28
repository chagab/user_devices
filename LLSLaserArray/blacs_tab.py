from blacs.device_base_class import DeviceTab


class LLSLaserArrayTab(DeviceTab):

    def initialise_GUI(self):
        # print(self.power_boundaries)
        do_prop = {
            'ON 403nm': {},
            'ON 444nm': {},
            'ON 488nm': {},
            'ON 514nm': {},
            'ON 560nm': {},
            'ON 607nm': {},
            'ON 642nm': {},
        }

        # For the min/max values of the MPB laser, check our lasers TDR as well as specific laser
        # caracteristics at
        # https://mpbcommunications.com/en/site/products/fiber_laser/continuous-wave/visible/

        ao_prop = {
            'Power 403nm': {
                'base_unit': 'mW',
                'min': 0,
                'max': 300,
                'step': 1e-3,
                'decimals': 1
            },
            'Power 444nm': {
                'base_unit': 'mW',
                'min': 0,
                'max': 10,
                'step': 1e-3,
                'decimals': 1
            },
            'Power 488nm': {
                'base_unit': 'mW',
                'min': 500 * 0.2,
                'max': 500 * 1,
                'step': 1e-3,
                'decimals': 1
            },
            'Power 514nm': {
                'base_unit': 'mW',
                'min': 1000 * 0.2,
                'max': 1000 * 1,
                'step': 1e-3,
                'decimals': 1
            },
            'Power 560nm': {
                'base_unit': 'mW',
                'min': 1000 * 0.2,
                'max': 1000 * 1,
                'step': 1e-3,
                'decimals': 1
            },
            'Power 607nm': {
                'base_unit': 'mW',
                'min': 1000 * 0.2,
                'max': 1000 * 1,
                'step': 1e-3,
                'decimals': 1
            },
            'Power 642nm': {
                'base_unit': 'mW',
                'min': 0,
                'max': 10,
                'step': 1e-3,
                'decimals': 1
            },
        }

        # Create the output objects
        self.create_digital_outputs(do_prop)
        self.create_analog_outputs(ao_prop)

        # Create widgets for output objects
        _, ao_widgets, do_widgets = self.auto_create_widgets()

        # and auto place the widgets in the UI
        self.auto_place_widgets(
            ("Laser ON OFF", do_widgets),
            ("Laser output power", ao_widgets)
        )

        # Store the board number to be used
        connection_object = self.settings['connection_table'].find_by_name(
            self.device_name
        )
        self.board_number = int(connection_object.BLACS_connection)

        # And which scheme we're using for buffered output programming and
        # triggering: (default values for backward compat with old connection
        # tables)
        self.programming_scheme = connection_object.properties.get(
            'programming_scheme',
            'pb_start/BRANCH'
        )

        worker_initialisation_kwargs = \
            self.connection_table.find_by_name(self.device_name).properties
        worker_initialisation_kwargs['addr'] = self.BLACS_connection
        self.create_worker(
            'main_worker',
            'user_devices.LLSLaserArray.blacs_worker.LLSLaserArrayWorker',
            worker_initialisation_kwargs,
        )
        self.primary_worker = 'main_worker'
