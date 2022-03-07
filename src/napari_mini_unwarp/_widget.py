"""



"""

from qtpy.QtWidgets import (QWidget, 
                            QHBoxLayout, 
                            QPushButton, 
                            QVBoxLayout, 
                            QLineEdit,
                            QLabel,
                            QMessageBox,
                            QComboBox
                           )

import qtpy.QtCore as qtcore 
from qtpy.QtGui import QIntValidator, QDoubleValidator

from ._helpers import generate_perfect_grid, unwarp



GRID_IMAGE_LAYER = 'Grid image(s)'
UNWARPED_LAYER = 'Unwarped grid image'
STANDARD_GRID_LAYER = 'Standard grid'
USR_GRID_LAYER = 'Grid'


class MiniUnwarpWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter

    def __init__(self, napari_viewer):
        super().__init__()

        
        self.viewer = napari_viewer
        width = 200
        self.left_margins=15
        self.top_margins=10
        self.right_margins=15
        self.bottom_margins=0
        self.setMaximumWidth(width)

        self.state_unwarp_btn = False # the "Unwarp!" button is deactivated from start
        self.state_export_btn = False # "Export" button

        ### Main Layout
        layout = QVBoxLayout()    
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        

        ## Define grid cols and rows 
        # First info box
        layout_info = QHBoxLayout()  
        info_text = QLabel("<b>(A)</b> Enter the number of <br> <i>rows</i> and <i>columns</i> <br> below.<br>You can press space bar<br>and move the image<br> or zoom in by scrolling.")
        layout_info.addWidget(info_text, 100)
        layout_info_widget = QWidget()
        layout_info_widget.setLayout(layout_info)
        layout_info_widget.setContentsMargins( 0, 
                                               0, 
                                               0, 
                                               0
                                               )
        layout_grid_def_widget = self._generate_grid_def_layout()
        layout_start_margin_widget = self._generate_start_margin_layout()
        layout_generate_grid_widget = self._generate_grid_generate_layout()
        layout_unwarp_widget = self._generate_unwarp_layout()
        layout_gridspacing = self._generate_gridspacing_layout()
        
        # System, scope, objective, zoom and tlens plane information 
        layout_systemname    = self._generate_systemname_layout()
        layout_scopename     = self._generate_scopename_layout()
        layout_objectivename = self._generate_objectivename_layout()
        layout_zoomname      = self._generate_zoom_layout()
        layout_tlens_plane   = self._generate_tlens_layout()

        layout_export = self._generate_export_layout()



        #### Take care of main layout

        layout.addWidget(layout_info_widget) 
        layout.addWidget(layout_grid_def_widget) 
        layout.addWidget(layout_start_margin_widget)   
        layout.addWidget(layout_generate_grid_widget)
        layout.addWidget(layout_unwarp_widget)

        # Second info box
        layout_info2 = QHBoxLayout()  
        info_text2 = QLabel("<b>(B)</b> What is the physical <br>grid spacing in microns?")
        layout_info2.addWidget(info_text2, 100)
        layout_info_widget2 = QWidget()
        layout_info_widget2.setLayout(layout_info2)
        layout_info_widget2.setContentsMargins(0, 
                                               30, 
                                               0, 
                                               0
                                               )
        layout.addWidget(layout_info_widget2) 
        layout.addWidget(layout_gridspacing)

        # Third info box
        layout_info3 = QHBoxLayout()  
        info_text3 = QLabel("<b>(C)</b> Specify system and<br>acquisition parameters")
        layout_info3.addWidget(info_text3, 100)
        layout_info_widget3 = QWidget()
        layout_info_widget3.setLayout(layout_info3)
        layout_info_widget3.setContentsMargins(0, 
                                               30, 
                                               0, 
                                               0
                                               )
        layout.addWidget(layout_info_widget3) 

        layout.addWidget(layout_systemname)
        layout.addWidget(layout_scopename)
        layout.addWidget(layout_objectivename)
        layout.addWidget(layout_zoomname)
        layout.addWidget(layout_tlens_plane)

        layout.addWidget(layout_export)

        layout.setAlignment(qtcore.Qt.AlignTop)
        self.setLayout(layout)

    
    ##### LAYOUT ELEMENTS #############################################################################
    ###################################################################################################
    
    def _generate_grid_def_layout(self):
        # LAYOUT
        # Define grid cols and rows (input text fields)
        
        # To allow only int
        onlyInt = QIntValidator()

        # Cols: ___ Rows: ____ 
        layout_grid_def = QHBoxLayout()  
        label_no_rows = QLabel("Rows")
        label_no_cols = QLabel("Cols")

        self.no_rows_edit = QLineEdit()
        self.no_rows_edit.setMaxLength(2)
        self.no_rows_edit.setText('9')
        self.no_rows_edit.setValidator(onlyInt)
        self.no_cols_edit = QLineEdit()
        self.no_cols_edit.setMaxLength(2)
        self.no_cols_edit.setText('9')
        self.no_cols_edit.setValidator(onlyInt)
        # ... add to layout
        layout_grid_def.addWidget(label_no_rows, 20)
        layout_grid_def.addWidget(self.no_rows_edit, 30)
        layout_grid_def.addWidget(label_no_cols, 20)
        layout_grid_def.addWidget(self.no_cols_edit, 30)
        layout_grid_def.setContentsMargins(self.left_margins, 
                                           0, 
                                           self.right_margins, 
                                           self.bottom_margins
                                           )
        layout_grid_def_widget = QWidget()
        layout_grid_def_widget.setLayout(layout_grid_def)
        return layout_grid_def_widget

    def _generate_start_margin_layout(self):
        # LAYOUT
        # Start margin input box 
        layout_start_margin = QHBoxLayout()  
        start_margin_label = QLabel("Start margin")
        self.start_margin_edit = QLineEdit()
        self.start_margin_edit.setText('0.1')
        range_0_1 = QDoubleValidator(0.,1.,2)
        self.start_margin_edit.setValidator(range_0_1)
        layout_start_margin.addWidget(start_margin_label)
        layout_start_margin.addWidget(self.start_margin_edit)
        layout_start_margin.setContentsMargins(self.left_margins, 
                                               self.top_margins, 
                                               self.right_margins, 
                                               self.bottom_margins
                                               )
        layout_start_margin_widget =  QWidget()
        layout_start_margin_widget.setLayout(layout_start_margin)
        return layout_start_margin_widget

    def _generate_grid_generate_layout(self):
        # LAYOUT
        # Generate grid generation button
        layout_generate_grid = QHBoxLayout()  
        generate_grid_button = QPushButton("Generate grid")
        generate_grid_button.clicked.connect(self._generate_grid)
        layout_generate_grid.addWidget(generate_grid_button)
        layout_generate_grid.setContentsMargins(self.left_margins, 
                                                self.top_margins, 
                                                self.right_margins, 
                                                self.bottom_margins
                                                )
        layout_generate_grid_widget =  QWidget()
        layout_generate_grid_widget.setLayout(layout_generate_grid)
        return layout_generate_grid_widget

    def _generate_unwarp_layout(self):
        # LAYOUT
        # Generate unwarp button
        layout_unwarp = QHBoxLayout()  
        self.unwarp_button = QPushButton("Unwarp!")
        self.unwarp_button.clicked.connect(self._unwarp)
        self.unwarp_button.setEnabled(self.state_unwarp_btn)
        layout_unwarp.addWidget(self.unwarp_button)
        layout_unwarp.setContentsMargins(self.left_margins, 
                                                self.top_margins, 
                                                self.right_margins, 
                                                self.bottom_margins
                                                )
        layout_unwarp_widget =  QWidget()
        layout_unwarp_widget.setLayout(layout_unwarp)
        return layout_unwarp_widget

    def _generate_gridspacing_layout(self):
        # LAYOUT
        # Generate gridspacing input field

        layout_gridspacing = QHBoxLayout()  
       
        gridspacing_label   = QLabel("Grid (µm)")
        self.gridspacing_edit = QLineEdit()
        self.gridspacing_edit.setText('50.0')
        layout_gridspacing.addWidget(gridspacing_label,30)
        layout_gridspacing.addWidget(self.gridspacing_edit,70)

        layout_gridspacing.setContentsMargins(self.left_margins, 
                                               0, 
                                               self.right_margins, 
                                               self.bottom_margins
                                               )
        layout_gridspacing_widget =  QWidget()
        layout_gridspacing_widget.setLayout(layout_gridspacing)
        return layout_gridspacing_widget

    def _generate_systemname_layout(self):
        # LAYOUT
        # Generate system name input field

        layout_systemname = QHBoxLayout()  
       
        systemname_label   = QLabel("System")
        self.systemname_edit = QLineEdit()
        self.systemname_edit.setText('Emerald')
        layout_systemname.addWidget(systemname_label,30)
        layout_systemname.addWidget(self.systemname_edit,70)

        layout_systemname.setContentsMargins(self.left_margins, 
                                             0, 
                                             self.right_margins, 
                                             self.bottom_margins
                                             )
        layout_systemname_widget =  QWidget()
        layout_systemname_widget.setLayout(layout_systemname)
        return layout_systemname_widget

    def _generate_scopename_layout(self):
        # LAYOUT
        # Generate scope name input field

        layout_scopename = QHBoxLayout()  
       
        scopename_label   = QLabel("Scope")
        self.scopename_edit = QLineEdit()
        self.scopename_edit.setText('Enormous')
        layout_scopename.addWidget(scopename_label,30)
        layout_scopename.addWidget(self.scopename_edit,70)

        layout_scopename.setContentsMargins(self.left_margins, 
                                            self.top_margins, 
                                            self.right_margins, 
                                            self.bottom_margins
                                            )
        layout_scopename_widget =  QWidget()
        layout_scopename_widget.setLayout(layout_scopename)
        return layout_scopename_widget

    def _generate_objectivename_layout(self):
        # LAYOUT
        # Generate objetive name QComboBox dropdown

        layout_scopename = QHBoxLayout()  
        scopename_label  = QLabel("Objective")
        self.scopename   = QComboBox()
        self.scopename.addItems(["D0213", "D0277", "D0254"])
        #self.scopename.currentIndexChanged.connect(self.____)

        layout_scopename.addWidget(scopename_label, 30)
        layout_scopename.addWidget(self.scopename,  70)

        layout_scopename.setContentsMargins(self.left_margins, 
                                            self.top_margins, 
                                            self.right_margins, 
                                            self.bottom_margins
                                            )
        layout_scopename_widget =  QWidget()
        layout_scopename_widget.setLayout(layout_scopename)
        return layout_scopename_widget


    def _generate_zoom_layout(self):
        # LAYOUT
        # Generate zoom level input field

        layout_zoomlevel = QHBoxLayout()  
        zoomlevel_label  = QLabel("Zoom")
        self.zoomlevel = QLineEdit()
        self.zoomlevel.setText('1.0')


        layout_zoomlevel.addWidget(zoomlevel_label, 30)
        layout_zoomlevel.addWidget(self.zoomlevel,  70)

        layout_zoomlevel.setContentsMargins(self.left_margins, 
                                            self.top_margins, 
                                            self.right_margins, 
                                            self.bottom_margins
                                            )
        layout_zoomlevel_widget =  QWidget()
        layout_zoomlevel_widget.setLayout(layout_zoomlevel)
        return layout_zoomlevel_widget

    def _generate_tlens_layout(self):
        # LAYOUT
        # Generate tlens zplane level input field

        layout_tlens = QHBoxLayout()  
        tlens_label  = QLabel("TLens (µm)")
        self.tlens = QLineEdit()
        self.tlens.setText('0.0')

        layout_tlens.addWidget(tlens_label, 30)
        layout_tlens.addWidget(self.tlens,  70)

        layout_tlens.setContentsMargins(self.left_margins, 
                                        self.top_margins, 
                                        self.right_margins, 
                                        self.bottom_margins
                                        )
        layout_tlens_widget =  QWidget()
        layout_tlens_widget.setLayout(layout_tlens)
        return layout_tlens_widget



    def _generate_export_layout(self):
        # LAYOUT
        # Generate export button
        layout_export = QHBoxLayout()  
        self.export_button = QPushButton("Export (WIP!)")
        self.export_button.clicked.connect(self._export)
        self.export_button.setEnabled(self.state_export_btn)
        layout_export.addWidget(self.export_button)
        layout_export.setContentsMargins(self.left_margins, 
                                         30, 
                                         self.right_margins, 
                                         self.bottom_margins
                                         )
        layout_export_widget =  QWidget()
        layout_export_widget.setLayout(layout_export)
        return layout_export_widget



    ##### FUNCTIONS / CALLBACKS #######################################################################
    ###################################################################################################
    

    def _generate_grid(self):
        '''
        Callback for "Generate grid" button.

        Generate a "perfect" (i.e. standard) grid of dots, 
        and create a new layer from it. 
        Only create the layer if it does not exist yet, or 
        the experimenter wants to overwrite the previously generated one.
        
        '''
        # Fetch the following (grid defining) parameters 
        # once so they become available to other functiions downstream 

        self.no_rows = int(self.no_rows_edit.text())
        self.no_cols = int(self.no_cols_edit.text())
        self.start_margin = float(self.start_margin_edit.text()) # Needs to get available to other functions too

        grid_image = self.viewer.layers[GRID_IMAGE_LAYER].data

        print(f'Adding dots ... \n rows: {self.no_rows} x cols: {self.no_cols} | margin: {self.start_margin}')

        grid_dots = generate_perfect_grid(grid_image,
                                          rows= self.no_rows,
                                          cols=self.no_cols,
                                          start_margin=self.start_margin,
                                          )
        self.standard_grid_dots = grid_dots.copy() # Create copy for later ... 

        # Built in check for layer existence
        for l in self.viewer.layers:
            if (l.name == STANDARD_GRID_LAYER) or (l.name == USR_GRID_LAYER) :
                ret = QMessageBox.question(self, 'MessageBox', 
                                           "Previously generated grid dot patterns exist. Delete?", 
                                           QMessageBox.Yes | QMessageBox.Cancel)

                if ret == QMessageBox.Yes:
                    print('Deleting layer')
                    try:
                        self.viewer.layers.pop(STANDARD_GRID_LAYER)
                        self.viewer.layers.pop(USR_GRID_LAYER)
                    except KeyError: 
                        pass
                    # Also delete any previous unwarping result
                    try: 
                        self.viewer.layers.pop(UNWARPED_LAYER)
                    except KeyError:
                        pass
                else:
                    print('Skipping')
                    return 

        ###### ADD DOTS ##########################################################################

        self.viewer.add_points(name=STANDARD_GRID_LAYER,
                  data=grid_dots,
                  edge_width=1, 
                  edge_color='#000000',  
                  face_color = 'white',
                  opacity = .8,    
                  size=grid_image.shape[0]/60, # Adapt size of symbol to current data size
                  blending='translucent'
              )
        self.viewer.add_points(data=grid_dots.copy(),
                        name=USR_GRID_LAYER, 
                        edge_width=.4, 
                        edge_color='orangered',  
                        face_color = 'white',
                        opacity = .5,    
                        size=grid_image.shape[0]/40, # Adapt size of symbol to current data size
                        blending='translucent'
                    )
        self.viewer.layers[USR_GRID_LAYER].mode ='select'
        self.viewer.layers[USR_GRID_LAYER].symbol ='x'

        self.viewer.layers[STANDARD_GRID_LAYER].visible = False

        # Lastly, activate the unwarp button 
        self.state_unwarp_btn = True
        self.unwarp_button.setEnabled(self.state_unwarp_btn)

        # ... and make sure the export button is (still) disabled (until warp is pressed)
        self.state_export_btn = False
        self.export_button.setEnabled(self.state_export_btn)

        return 


    def _unwarp(self):
        '''
        Callback for "Unwarp!" button

        Generate piecewise affine transformation from standard and user defined 
        grid pattern, unwarp and add to napari viewer 
        
        '''
        print('Unwarping ...')

        # Built in check for layer existence
        for l in self.viewer.layers:
            if (l.name == UNWARPED_LAYER) :
                ret = QMessageBox.question(self, 'MessageBox', 
                                           "Previous unwarping result exists. Delete?", 
                                           QMessageBox.Yes | QMessageBox.Cancel)

                if ret == QMessageBox.Yes:
                    print('Deleting layer')
                    self.viewer.layers.pop(UNWARPED_LAYER)
                else:
                    print('Skipping')
                    return 

        # Grid image
        grid_image_layer = self.viewer.layers[GRID_IMAGE_LAYER]
        grid_image_original = grid_image_layer.data

        # Standard grid pattern
        standard_grid = generate_perfect_grid(data = grid_image_original,
                                              rows = self.no_rows,
                                              cols = self.no_cols,
                                              start_margin = self.start_margin,
                                         )
        
        # User grid pattern
        usr_layer_grid = self.viewer.layers[USR_GRID_LAYER]
        usr_dots = usr_layer_grid.data

        # UNWARPING
        unwarped, status = unwarp(usr_dots, standard_grid, grid_image_original)

        # Start margin ...
        margin = self.start_margin


        if status == True:
            while status: 
                print(f'margin now at {margin:.4f}')
                margin-=0.005
                grid_dots_ = generate_perfect_grid(data = grid_image_original,
                                                   rows = self.no_rows,
                                                   cols = self.no_cols,
                                                   start_margin = margin,
                                                )
                unwarped, status = unwarp(usr_dots, grid_dots_, grid_image_original)
        else:
            while not status: 
                print(f'margin now at {margin:.4f}')
                margin+=0.005
                grid_dots_ = generate_perfect_grid(data = grid_image_original,
                                                rows = self.no_rows,
                                                cols = self.no_cols,
                                                start_margin = margin,
                                                )
                unwarped, status = unwarp(usr_dots, grid_dots_, grid_image_original)

        # Lastly, add the unwarped grid image to the viewer
        self.viewer.add_image(data=unwarped, rgb=False, name=UNWARPED_LAYER)

        self.state_export_btn = True
        self.export_button.setEnabled(self.state_export_btn)

        return

    def _export(self):
        '''
        Export the unwarping results to disk.
        
        '''
        print('EXPORT')