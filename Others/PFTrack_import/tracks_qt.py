import os.path
# Nuke 11 switched to PySide2
try:
    from PySide import QtGui, QtCore
    QtWidgets = QtGui
except:
    from PySide2 import QtGui, QtCore, QtWidgets
import tracks_parse
import tracks_nuke


class ElidedLabel(QtWidgets.QLabel):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(),
                                    QtCore.Qt.TextElideMode.ElideMiddle,
                                    self.width())
        painter.drawText(self.rect(), self.alignment(), elided)


class ImportTracks(QtWidgets.QDialog):
    def __init__(self, label=''):
        super(self.__class__, self).__init__()

        # WINDOW
        self.setWindowTitle('Tracks Import {0}'.format(label))
        self.setMinimumSize(QtCore.QSize(400, 360))
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        # BROWSE
        lay_browse = QtWidgets.QHBoxLayout()
        lay_browse.setAlignment(QtCore.Qt.AlignLeft)

        btn_browse = QtWidgets.QPushButton('Browse')
        btn_browse.setFixedWidth(80)
        btn_browse.clicked.connect(self.browse)
        self.label_file = ElidedLabel()

        lay_browse.addWidget(btn_browse)
        lay_browse.addWidget(self.label_file)
        layout.addLayout(lay_browse)

        # LIST
        lay_list = QtWidgets.QVBoxLayout()
        lay_list.setAlignment(QtCore.Qt.AlignTop)

        label_list = QtWidgets.QLabel('Trackers')
        self.view_list = QtWidgets.QListView()
        self.view_list.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.view_list.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)

        lay_list.addWidget(label_list)
        lay_list.addWidget(self.view_list)
        layout.addLayout(lay_list)

        # SELECTION
        lay_sel = QtWidgets.QHBoxLayout()
        lay_sel.setAlignment(QtCore.Qt.AlignLeft)

        btn_all = QtWidgets.QPushButton('All')
        btn_all.clicked.connect(self.view_list.selectAll)
        btn_all.setFixedWidth(80)
        btn_none = QtWidgets.QPushButton('None')
        btn_none.clicked.connect(self.view_list.clearSelection)
        btn_none.setFixedWidth(80)

        lay_sel.addWidget(btn_all)
        lay_sel.addWidget(btn_none)
        layout.addLayout(lay_sel)

        # ACTION
        self.chk_tracker3 = QtWidgets.QCheckBox('Use tracker3 node')
        self.chk_tracker3.setChecked(True)
        lay_action = QtWidgets.QHBoxLayout()
        lay_action.setAlignment(QtCore.Qt.AlignRight)

        btn_import = QtWidgets.QPushButton('Import')
        btn_import.setFixedWidth(80)
        btn_import.clicked.connect(self.import_tracks)
        btn_cancel = QtWidgets.QPushButton('Cancel')
        btn_cancel.setFixedWidth(80)
        btn_cancel.clicked.connect(self.reject)

        lay_action.addWidget(self.chk_tracker3)
        lay_action.addWidget(btn_import)
        lay_action.addWidget(btn_cancel)
        layout.addLayout(lay_action)

    def browse(self):
        file_selected, file_filter = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select exported tracks(.txt)',
            '', 'PFTracks Exports(*.txt)')

        if file_selected:
            # file label
            self.label_file.setText(file_selected)

            # tracking data
            self.tracks_data = tracks_parse.pftrack(file_selected)

            # update model
            self.model_list = QtGui.QStandardItemModel()
            for track in self.tracks_data:
                item = QtGui.QStandardItem()
                item.setData(track, QtCore.Qt.ItemDataRole.UserRole)
                item.setData(track['name'], QtCore.Qt.ItemDataRole.DisplayRole)
                self.model_list.appendRow(item)
            self.view_list.setModel(self.model_list)

    def import_tracks(self):
        indexes = self.view_list.selectedIndexes()
        data = []
        is_tracker3 = self.chk_tracker3.isChecked()

        # Get tracking data from selected
        for i in indexes:
            data.append(i.data(QtCore.Qt.ItemDataRole.UserRole))

        # Create trackers
        if data:
            name, ext = os.path.splitext(
                os.path.basename(self.label_file.text()))
            if not is_tracker3:
                tracks_nuke.create_tracker4(data, name)
            else:
                tracks_nuke.create_tracker3(data, name)
        self.accept()


def panel():
    p = ImportTracks('PFTrack')
    p.exec_()
