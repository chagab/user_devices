from blacs.device_base_class import DeviceTab

from qtutils.qt import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from blacs.tab_base_classes import (
    define_state,
    MODE_MANUAL,
    MODE_TRANSITION_TO_BUFFERED,
    MODE_TRANSITION_TO_MANUAL,
    MODE_BUFFERED
)


class QFileDialogPreview(QFileDialog):
    def __init__(self, *args, **kwargs):
        QFileDialog.__init__(self, *args, **kwargs)
        self.setOption(QFileDialog.DontUseNativeDialog, True)

        box = QVBoxLayout()

        self.setMinimumSize(self.width() + 250, self.height())

        self.mpPreview = QLabel("Preview", self)
        self.mpPreview.setMinimumSize(250, 250)
        self.mpPreview.setAlignment(Qt.AlignTop)
        self.mpPreview.setObjectName("labelPreview")
        box.addWidget(self.mpPreview)

        box.addStretch()

        self.layout().addLayout(box, 1, 3, 1, 1)

        self.currentChanged.connect(self.onChange)
        self.fileSelected.connect(self.onFileSelected)
        self.filesSelected.connect(self.onFilesSelected)

        self._fileSelected = None
        self._filesSelected = None

    def onChange(self, path):
        pixmap = QPixmap(path)

        if (pixmap.isNull()):
            self.mpPreview.setText("Preview")
        else:
            self.mpPreview.setPixmap(
                pixmap.scaled(
                    self.mpPreview.width(),
                    self.mpPreview.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

    def onFileSelected(self, file):
        self._fileSelected = file

    def onFilesSelected(self, files):
        self._filesSelected = files

    def getFileSelected(self):
        return self._fileSelected

    def getFilesSelected(self):
        return self._filesSelected


class MeadowlarkSLMTab(DeviceTab):

    def initialise_GUI(self):

        # Get the layout
        self.layout = self.get_tab_layout()
        # Create all the QWidget you want (pushbutton, loading bar etc)
        self.file_explorer = QFileDialogPreview(
            caption="Open Image",
            directory="C:\\Experiments\\example_apparatus\\test_SLM",
            filter="Image Files (*.png *.jpg *.bmp)"
        )
        # Add all the QWidgets to the layout
        self.layout.addWidget(self.file_explorer)
        # Connect the QWidget to the desired behavior
        self.file_explorer.fileSelected.connect(self.onFileSelected)

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
            'user_devices.MeadowlarkSLM.blacs_worker.MeadowlarkSLMWorker',
            worker_initialisation_kwargs,
        )
        self.primary_worker = 'main_worker'

    @define_state(MODE_MANUAL | MODE_BUFFERED | MODE_TRANSITION_TO_BUFFERED | MODE_TRANSITION_TO_MANUAL, True)
    def onFileSelected(self, button):
        fileName = self.file_explorer.selectedFiles()
        yield (self.queue_work(self.primary_worker, 'load_image', fileName[0]))
        # when fileSelected is called, the dialog window is erased so
        # we need to re-create it
        self.file_explorer = QFileDialogPreview(
            caption="Open Image",
            directory="C:\\Experiments\\example_apparatus\\test_SLM",
            filter="Image Files (*.png *.jpg *.bmp)"
        )
        self.layout.addWidget(self.file_explorer)
        self.file_explorer.fileSelected.connect(self.onFileSelected)
