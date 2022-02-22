"""



"""
from qtpy.QtWidgets import (QWidget, 
                            QHBoxLayout, 
                            QPushButton, 
                            QVBoxLayout, 
                            QLineEdit,
                            QLabel,
                            QFrame,
                           )

import qtpy.QtCore as qtcore 
from qtpy.QtGui import QIntValidator


class MiniUnwarpWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        width = 200
        self.setMaximumWidth(width)


        ### Main Layout
        layout = QVBoxLayout()    
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # To allow only int
        onlyInt = QIntValidator()

        ## Define grid cols and rows 
        layout_info = QHBoxLayout()  
        info_text = QLabel("Enter the number of <br> <b>rows</b> and <b>columns</b> <br> below.")
        layout_info.addWidget(info_text, 100)

        layout_info_widget = QWidget()
        layout_info_widget.setLayout(layout_info)


        ## Define grid cols and rows 
        # Cols: ___ Rows: ____ 
        layout_grid_def = QHBoxLayout()  
        label_no_rows = QLabel("Rows")
        label_no_cols = QLabel("Cols")

        self.no_rows = QLineEdit()
        self.no_rows.setMaxLength(2)
        self.no_rows.setValidator(onlyInt)
        self.no_cols = QLineEdit()
        self.no_cols.setMaxLength(2)
        self.no_cols.setValidator(onlyInt)
        # ... add to layout
        layout_grid_def.addWidget(label_no_rows, 20)
        layout_grid_def.addWidget(self.no_rows, 30)
        layout_grid_def.addWidget(label_no_cols, 20)
        layout_grid_def.addWidget(self.no_cols, 30)

        layout_grid_def_widget = QWidget()
        layout_grid_def_widget.setLayout(layout_grid_def)






        #### Take care of main layout

        #layout.setAlignment(qtcore.Qt.AlignTop)
        layout.addWidget(layout_info_widget) 
        layout.addWidget(layout_grid_def_widget)    
        #separator_top = QFrame(lineWidth=3)
        #separator_top.Shape(QFrame.HLine)
        #layout.addWidget(separator_top)

        layout.setAlignment(qtcore.Qt.AlignTop)
        self.setLayout(layout)


        # btn = QPushButton("Click me now!")
        # btn.clicked.connect(self._on_click)

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")

