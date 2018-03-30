import os.path
# Nuke 11 switched to PySide2
try:
    from PySide import QtGui, QtCore
    QtWidgets = QtGui
except:
    from PySide2 import QtGui, QtCore, QtWidgets
import PFTrack_import as PFT


class ElidedLabel(QtWidgets.QLabel):
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        metrics = QtGui.QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(),
                                    QtCore.Qt.TextElideMode.ElideMiddle,
                                    self.width())
        painter.drawText(self.rect(), self.alignment(), elided)


class ImportTracks(QtWidgets.QDialog):
    def __init__(self):
        super(self.__class__, self).__init__()

        # Window
        self.setWindowTitle('PFTrack: Import 2D Tracks')
        self.setMinimumSize(QtCore.QSize(400, 360))
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.layout)

        # browseBtn
        self.BrowseCombo = QtWidgets.QHBoxLayout()
        self.BrowseCombo.setAlignment(QtCore.Qt.AlignLeft)
        self.fileLabel = ElidedLabel()
        self.filePath = ''
        browseBtn = QtWidgets.QPushButton('Browse')
        browseBtn.clicked.connect(self.browseBtn)
        browseBtn.setFixedWidth(80)
        self.BrowseCombo.addWidget(browseBtn)
        self.BrowseCombo.addWidget(self.fileLabel)
        self.layout.addLayout(self.BrowseCombo)

        # list
        ListCombo = QtWidgets.QVBoxLayout()
        ListCombo.setAlignment(QtCore.Qt.AlignTop)
        listTitle = QtWidgets.QLabel('Trackers')
        self.listView = QtWidgets.QListView()
        self.listView.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.listView.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        ListCombo.addWidget(listTitle)
        ListCombo.addWidget(self.listView)
        self.layout.addLayout(ListCombo)

        # Selection
        selectionCombo = QtWidgets.QHBoxLayout()
        selectionCombo.setAlignment(QtCore.Qt.AlignLeft)
        allBtn = QtWidgets.QPushButton('All')
        allBtn.clicked.connect(self.listView.selectAll)
        allBtn.setFixedWidth(80)
        noneBtn = QtWidgets.QPushButton('None')
        noneBtn.clicked.connect(self.listView.clearSelection)
        noneBtn.setFixedWidth(80)
        selectionCombo.addWidget(allBtn)
        selectionCombo.addWidget(noneBtn)
        self.layout.addLayout(selectionCombo)

        # Action
        self.old = QtWidgets.QCheckBox('Use tracker3 node')
        self.old.setChecked(True)
        actionCombo = QtWidgets.QHBoxLayout()
        actionCombo.setAlignment(QtCore.Qt.AlignRight)
        importBtn = QtWidgets.QPushButton('Import')
        importBtn.setFixedWidth(80)
        importBtn.clicked.connect(self.importTrackers)
        cancelBtn = QtWidgets.QPushButton('Cancel')
        cancelBtn.setFixedWidth(80)
        cancelBtn.clicked.connect(self.cancel)
        actionCombo.addWidget(self.old)
        actionCombo.addWidget(importBtn)
        actionCombo.addWidget(cancelBtn)
        self.layout.addLayout(actionCombo)

    def cancel(self):
        self.reject()

    def browseBtn(self):
        selectedFile, fileFilter = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select exported tracks(.txt)',
            '', 'PFTracks Exports(*.txt)')

        if selectedFile:
            # file label
            self.filePath = selectedFile
            self.fileLabel.setText(self.filePath)

            # tracking data
            self.trackersData = PFT.parsePFTracks(selectedFile)

            # update model
            self.listModel = QtGui.QStandardItemModel()
            for track in self.trackersData:
                item = QtGui.QStandardItem()
                item.setData(track, QtCore.Qt.ItemDataRole.UserRole)
                item.setData(track['name'], QtCore.Qt.ItemDataRole.DisplayRole)
                self.listModel.appendRow(item)
            self.listView.setModel(self.listModel)

    def importTrackers(self):
        indexes = self.listView.selectedIndexes()
        data = []
        isOld = self.old.isChecked()

        # Get tracking data from selected
        for i in indexes:
            data.append(i.data(QtCore.Qt.ItemDataRole.UserRole))

        # Create trackers
        if data:
            name, ext = os.path.splitext(os.path.basename(self.filePath))
            if not isOld:
                PFT.createTracker(data, 0, name)
            else:
                PFT.createTracker3(data, 0, name)
        self.accept()


def panel():
    p = ImportTracks()
    p.exec_()
