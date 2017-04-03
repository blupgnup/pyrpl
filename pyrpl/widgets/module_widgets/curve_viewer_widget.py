from PyQt4 import QtCore, QtGui
from .base_module_widget import ReducedModuleWidget


class CurveViewerWidget(ReducedModuleWidget):
    def init_attribute_layout(self):
        super(CurveViewerWidget, self).init_attribute_layout()
        textwidget = self.attribute_widgets["params"]
        self.main_layout.removeWidget(textwidget)
        self.textbox = QtGui.QHBoxLayout()
        self.main_layout.addLayout(self.textbox)
        self.textbox.addWidget(textwidget)