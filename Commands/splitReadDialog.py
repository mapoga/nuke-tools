try:
	from PySide.QtGui import *
	from PySide.QtCore import *
except ImportError:
	from PySide2.QtWidgets import *
	from PySide2.QtCore import *
	from PySide2.QtGui import *

from functools import partial


class LayerItem(QListWidgetItem):
	enabled = QIcon(r'/P/DOSSIERS_PERSONNELS/mga/nuke/nuke-tools/Commands/layer_enabled.png')
	disabled = QIcon(r'/P/DOSSIERS_PERSONNELS/mga/nuke/nuke-tools/Commands/layer_disabled.png')

	def __init__(self, label, enabled=True):
		QListWidgetItem.__init__(self, label)
		self.set_enabled(enabled)

	def set_icon(self, enable):
		if enable:
			self.setIcon(LayerItem.enabled)
		else:
			self.setIcon(LayerItem.disabled)

	def set_enabled(self, enabled):
		self.enabled = enabled
		self.set_icon(self.enabled)

	def toggle_enabled(self):
		self.set_enabled( not self.enabled)


class LayersWidget(QListWidget):

	def __init__(self, layers):
		QListWidget.__init__(self)
		self.setDragDropMode(QAbstractItemView.InternalMove)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)

		#Layers
		self.layers = layers

		for layer in self.layers:
			item = LayerItem(layer)

			self.addItem(item)
		self.itemDoubleClicked.connect(self._handleDoubleClick)

		#Size
		self.setMinimumSize(300, 300)
		self.setMaximumSize(300, 900)
		self.resize(300, 10 +(self.sizeHintForRow(0) * self.count()))

		# Contextual menu
		self.setContextMenuPolicy(Qt.ActionsContextMenu)

		actEnable = QAction('Enable', self)
		actEnable.triggered.connect(partial(self.enable_selected, True))
		self.addAction(actEnable)

		actDisable = QAction('Disable', self)
		actDisable.triggered.connect(partial(self.enable_selected, False))
		self.addAction(actDisable)

	def _handleDoubleClick(self, item):
		item.toggle_enabled()

	def enable_selected(self, enable):
		for item in self.selectedItems():
			item.set_enabled(enable)

	def sizeHint(self):
		s = QSize()
		s.setWidth(300)
		s.setHeight(10 +(self.sizeHintForRow(0) * self.count()))
		return s


class LayersDialog(QDialog):
	def __init__(self, layers):
		QDialog.__init__(self)
		layout = QVBoxLayout()
		self.layers_widget = LayersWidget(layers)
		layout.addWidget(self.layers_widget)
		button = QPushButton('Split Layers')
		button.setDefault(True)
		button.clicked.connect(self.accept)
		layout.addWidget(button)
		self.setLayout(layout)
		self.setMaximumSize(300, 900)


	def create(self):
		layers = []
		for x in range(self.layers_widget.count()):
			item = self.layers_widget.item(x)
			if item.enabled:
				layers.append(item.text())
		return layers