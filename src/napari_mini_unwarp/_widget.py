"""



"""
import numpy as np 
from napari.utils import progress
from qtpy.QtWidgets import (QWidget, 
                            QHBoxLayout, 
                            QPushButton, 
                            QVBoxLayout, 
                            QLineEdit,
                            QLabel,
                            QMessageBox,
                            QComboBox,
                           )

import qtpy.QtCore as qtcore 
from qtpy.QtGui import QIntValidator, QDoubleValidator

from ._helpers import (generate_perfect_grid, 
                       unwarp, 
                       get_median_spacing, 
                       propagate_cross_corr, 
                       get_optimal_unwarp,
                      )

# Some naming ... 
GRID_IMAGE_LAYER = 'Grid image(s)'
UNWARPED_LAYER = 'Unwarped grid image'
STANDARD_GRID_LAYER = 'Standard grid'
USR_GRID_LAYER = 'Grid'
CORRECTED_POINTS_LAYER = 'Corrected points'


class MiniUnwarpWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter

    def __init__(self, napari_viewer):
        super().__init__()

        
        self.viewer = napari_viewer
        width = 250
        self.left_margins=15
        self.top_margins=10
        self.right_margins=15
        self.bottom_margins=0
        self.setMaximumWidth(width)

        self.state_unwarp_btn = False # the "Unwarp!" button is deactivated from start
        self.state_export_btn = False # "Export" button
        self.state_propagate_btn = False # Propagate points (through stack) button

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
        layout_propagate_points_widget = self._generate_propagate_layout()
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
        layout.addWidget(layout_propagate_points_widget)
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

    def _generate_propagate_layout(self):
        # LAYOUT
        # Propagate user set points through stack button
        layout_propagate_points = QHBoxLayout()  
        self.propagate_points_button = QPushButton("Propagate points")
        self.propagate_points_button.clicked.connect(self._propagate_points)
        self.propagate_points_button.setEnabled(self.state_propagate_btn)
        layout_propagate_points.addWidget(self.propagate_points_button)
        layout_propagate_points.setContentsMargins(self.left_margins, 
                                                   self.top_margins, 
                                                   self.right_margins, 
                                                   self.bottom_margins
                                                   )
        layout_propagate_points_widget =  QWidget()
        layout_propagate_points_widget.setLayout(layout_propagate_points)
        return layout_propagate_points_widget


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
       
        gridspacing_label   = QLabel("Grid (??m)")
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

        # Check if meta data is present 
        if 'zoom' in self.viewer.layers[GRID_IMAGE_LAYER].metadata:
            self.zoomlevel.setText(self.viewer.layers[GRID_IMAGE_LAYER].metadata['zoom'])
            self.zoomlevel.setEnabled(False)
        else: 
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
        tlens_label  = QLabel("TLens (??m)")
        self.tlens = QLineEdit()

        # Check if meta data is present 
        if 'z_height' in self.viewer.layers[GRID_IMAGE_LAYER].metadata:
            self.tlens.setText(self.viewer.layers[GRID_IMAGE_LAYER].metadata['z_height'])
            self.tlens.setEnabled(False)
        else: 
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

        self.viewer.add_points(data=grid_dots,
                               name=STANDARD_GRID_LAYER,
                               edge_width=1, 
                               edge_color='#000000',  
                               face_color = 'white',
                               opacity = .8,    
                               size=grid_image.shape[-1]/50, # Adapt size of symbol to current data size
                               blending='translucent',
                               out_of_slice_display=False,
                              )
        self.viewer.add_points(data=grid_dots.copy(),
                               name=USR_GRID_LAYER, 
                               edge_width=.4, 
                               edge_color='orangered',  
                               face_color = 'white',
                               opacity = .5,    
                               size=grid_image.shape[-1]/40, # Adapt size of symbol to current data size
                               blending='translucent',
                               out_of_slice_display=False,
                              )
        self.viewer.layers[USR_GRID_LAYER].mode ='select'
        self.viewer.layers[USR_GRID_LAYER].symbol ='x'

        self.viewer.layers[STANDARD_GRID_LAYER].visible = False

        # Lastly, activate the propagate points and unwarp buttons
        # Check if the data is multiplane ... 
        if grid_image.ndim == 3: 
            self.state_propagate_btn = True
            self.propagate_points_button.setEnabled(self.state_propagate_btn)

        self.state_unwarp_btn = True
        self.unwarp_button.setEnabled(self.state_unwarp_btn)

        # ... and make sure the export button is (still) disabled (until warp is pressed)
        self.state_export_btn = False
        self.export_button.setEnabled(self.state_export_btn)

        return 

    def _propagate_points(self):
        '''
        For data spanning multiple layers, 
        take the currently activated layer and try to propagate points 
        in z (across planes)
        
        '''

        grid_image = self.viewer.layers[GRID_IMAGE_LAYER].data
        if grid_image.ndim != 3:
            print('Data is not 3D - cannot propagate points')
            # ... and deactivate (why was it activated in the first place?)
            self.state_propagate_btn = False
            self.propagate_points_button.setEnabled(self.state_propagate_btn)
            return 

        # Built in check for layer existence
        for l in self.viewer.layers:
            if (l.name == CORRECTED_POINTS_LAYER) :
                ret = QMessageBox.question(self, 'MessageBox', 
                                           "Previous propagated points exist. Delete?", 
                                           QMessageBox.Yes | QMessageBox.Cancel)

                if ret == QMessageBox.Yes:
                    print('Deleting layer')
                    self.viewer.layers.pop(CORRECTED_POINTS_LAYER)
                else:
                    print('Skipping')
                    return 

        plane_idx_current   = self.viewer.dims.current_step[0]
        print(f'Current plane: {plane_idx_current}')
        grid_points_current = self.viewer.layers['Grid'].data
        num_planes = grid_image.shape[0]
                
        med_dist = get_median_spacing(grid_points_current)
        b_box_halfwidth = int(med_dist/4)

        sorted_point_dict = propagate_cross_corr(grid_image,
                                                 grid_points_current, 
                                                 plane_idx_current, 
                                                 b_box_halfwidth,
                                                 )


        # To add these points to the viewer we have to jump through some hoops ... 
        corr_points = np.stack(list(sorted_point_dict.values()))       
        for no, pt in enumerate(np.moveaxis(corr_points,0,-1)):
            # Looping over (individual points, 2, number of planes)
            # Create new point 
            new_pt = np.vstack((np.arange(num_planes), pt))
            new_pt = np.moveaxis(new_pt, -1, 0)
            if no == 0:
                all_points = new_pt
            else:
                all_points = np.vstack((all_points, new_pt))


        # Add all points across all planes to viewer
        self.viewer.add_points(name=CORRECTED_POINTS_LAYER,
                               data=all_points,
                               edge_width=.7,
                               edge_color='#000000',
                               face_color = 'cornflowerblue',
                               opacity = .6,
                               size=grid_image.shape[-1]/50, # Adapt size of symbol to current data size
                               blending='translucent',
                               out_of_slice_display=False,
                               )
        # Switch off the user point layer (because it's confusing at this point)
        self.viewer.layers[USR_GRID_LAYER].visible = False

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
        num_planes = grid_image_original.shape[0]

        # Standard grid pattern
        standard_grid = generate_perfect_grid(data = grid_image_original,
                                              rows = self.no_rows,
                                              cols = self.no_cols,
                                              start_margin = self.start_margin,
                                         )
        
        ##### DECIDE WHETHER YOU DEAL WITH SINGLE PLANE OR MULTIPLANE DATA 
        if CORRECTED_POINTS_LAYER in self.viewer.layers: 
            if grid_image_original.ndim == 3:
                multiplane = True
                usr_layer_grid =  self.viewer.layers[CORRECTED_POINTS_LAYER]
            else:
                raise NotImplementedError(f'{CORRECTED_POINTS_LAYER} layer detected but no 3D grid data')
        else: 
            multiplane = False 
            usr_layer_grid =  self.viewer.layers[USR_GRID_LAYER]

        # User grid pattern
        usr_dots = usr_layer_grid.data
        margin = self.start_margin


        # UNWARPING
        if not multiplane: 
            
            unwarped, status = unwarp(usr_dots, standard_grid, grid_image_original)
            # Start optimization
            unwarped, margin = get_optimal_unwarp(status,
                                                  margin,
                                                  usr_dots,
                                                  grid_image_original,
                                                  self.no_rows,
                                                  self.no_cols,
                                                 )
            standard_grid = generate_perfect_grid(data = grid_image_original[plane,:,:],
                                                  rows = self.no_rows,
                                                  cols = self.no_cols,
                                                  start_margin = margin,
                                                )


        else: 
            # Need to jump through some hoops to reformat the data in original 2D representation ... 
            usr_dots_reshaped = np.reshape(usr_dots,(-1,num_planes,3))
            usr_dots_reshaped = np.moveaxis(usr_dots_reshaped, 0, -1)

            # Do this twice - once just to get optimal margins across the whole stack
            # then to actually collect the output at optimal margin
            print('Optimizing margins ...')
            for plane in progress(np.arange(num_planes), desc='Optimizing margins'):
                usr_dots = usr_dots_reshaped[plane, 1:].T # LOVELY! 
                
                standard_grid = generate_perfect_grid(data = grid_image_original[plane,:,:],
                                                      rows = self.no_rows,
                                                      cols = self.no_cols,
                                                      start_margin = margin,
                                                      )
                unwarped, status = unwarp(usr_dots, standard_grid, grid_image_original[plane,:,:])

                # Start optimization
                unwarped, margin_ = get_optimal_unwarp(status,
                                                       margin,
                                                       usr_dots,
                                                       grid_image_original[plane,:,:],
                                                       self.no_rows,
                                                       self.no_cols,
                                                    )
                if margin_ > margin: 
                    # We are only intereseted in those unwarping results 
                    # that overshoot the boundaries (loose information over borders):
                    # Those are the ones that determine the upper bound, i.e. only the max counts here
                    margin = margin_

            print(f'Selected margin: {margin}')

            # ... now do it for real and collect the output
            print('Unwarping all planes ...')
            all_unwarped = []
            for plane in progress(np.arange(num_planes), desc='Collecting output'):
                standard_grid = generate_perfect_grid(data = grid_image_original[plane,:,:],
                                                      rows = self.no_rows,
                                                      cols = self.no_cols,
                                                      start_margin = margin,
                                                     )
                unwarped, status = unwarp(usr_dots, standard_grid, grid_image_original[plane,:,:])
                all_unwarped.append(unwarped)
            unwarped = np.stack(all_unwarped)

        # Lastly, add the unwarped grid image to the viewer
        self.viewer.add_image(data=unwarped, rgb=False, name=UNWARPED_LAYER)





        # Replace the standard grid with the optimized one 
        # this is the case for both the single as well as the multi plane case, so 
        # do it now, at the end

        self.viewer.layers.pop(STANDARD_GRID_LAYER)
        self.viewer.add_points(data=standard_grid,
                               name=STANDARD_GRID_LAYER,
                               edge_width=1, 
                               edge_color='#000000',  
                               face_color = 'white',
                               opacity = .8,    
                               size=grid_image_original.shape[-1]/50, # Adapt size of symbol to current data size
                               blending='translucent',
                               out_of_slice_display=False,
                              )
        self.viewer.layers[STANDARD_GRID_LAYER].visible = False




        self.state_export_btn = True
        self.export_button.setEnabled(self.state_export_btn)

        return

    def _export(self):
        '''
        Export the unwarping results to disk.
        
        '''
        #Collect output 
        for l in [GRID_IMAGE_LAYER, UNWARPED_LAYER, STANDARD_GRID_LAYER]:
            if l not in self.viewer.layers:
                print(f'{l} layer is missing')
                self.state_export_btn = False
                self.export_button.setEnabled(self.state_export_btn)
                return

        # Original grid image 
        grid_image = self.viewer.layers[GRID_IMAGE_LAYER].data
        # Unwarped grid image
        grid_image_unwarped = self.viewer.layers[UNWARPED_LAYER].data

        # Standard grid 
        standard_grid_points = self.viewer.layers[STANDARD_GRID_LAYER].data 
        # Corrected grid
        if CORRECTED_POINTS_LAYER in self.viewer.layers: 
            # This is only the case for multi plane data (and then the right one to export)
            corrected_grid_points = self.viewer.layers[CORRECTED_POINTS_LAYER].data
        elif USR_GRID_LAYER in self.viewer.layers:
            # ... if only a single layer is available
            corrected_grid_points = self.viewer.layers[USR_GRID_LAYER].data
        else:
            print('No user corrected grid layer was found.')
            self.state_export_btn = False
            self.export_button.setEnabled(self.state_export_btn)
            return
        
        # path = 
        print('EXPORTING')

        # with open(path/'export_timestamp_something.pkl', "wb") as export_file:
        #     print('Saving all results into ')
        #     pickle.dump(save_dict, export_file)

