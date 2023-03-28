from blacs.device_base_class import DeviceTab
from user_devices.LatticeGen.llspy_slm.slmgen.slmwindow import SLMdialog


class LatticeGenTab(DeviceTab):

    def initialise_GUI(self):
        self.latticeGen = SLMdialog()
        self.get_tab_layout().addWidget(self.latticeGen)

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
            'user_devices.LatticeGen.blacs_worker.LatticeGenWorker',
            worker_initialisation_kwargs,
        )
        self.primary_worker = 'main_worker'
