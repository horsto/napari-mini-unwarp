### HELPER FUNCTIONS
from collections import OrderedDict
import numpy as np
from pointpats import PointPattern
from skimage.registration import phase_cross_correlation
from napari.utils import progress

from ._unwarp import * 

def generate_perfect_grid(data, 
                          rows,
                          cols,
                          start_margin=.1
                         ):
    '''
    Generates a 2D grid of dots 
    
    Parameters
    ----------
    data : np.array : image
    rows : int : number of rows
    cols : int : number of cols
    start_margin : float : Relative margin at start and end 
    
    Returns
    -------
    grid_dots : np.aray: rows x cols
    
    '''   
    HEIGHT = data.shape[-1]
    WIDTH  = data.shape[-2]

    HEIGHT_start = HEIGHT * start_margin
    HEIGHT_end   = HEIGHT - (HEIGHT * start_margin)
    WIDTH_start  = WIDTH * start_margin
    WIDTH_end    = WIDTH - (WIDTH * start_margin)
    
    row_pos = np.linspace(HEIGHT_start, HEIGHT_end, num=rows)
    col_pos = np.linspace(WIDTH_start, WIDTH_end,   num=cols)
    
    grid_dots = []
    for y in row_pos:
        for x in col_pos: 
            grid_dots.append([y,x])
    grid_dots = np.vstack(grid_dots)    

    return grid_dots


def get_median_spacing(grid_points, verbose=True):
    '''
    Helper for _propagate_points()
    '''
    point_pat = PointPattern(grid_points)
    nn1, nnd1 = point_pat.knn(1)
    med_dist = np.median(nnd1)
    if verbose:
        print(f'Median spacing points: {med_dist:.2f} [px]')
    return med_dist


def propagate_cross_corr(grid_image,
                         grid_points_current, 
                         plane_idx_current, 
                         b_box_halfwidth,
                         upsample_factor = 250
                         ):

    '''
    Helper function for propagating a single layer of user defined points 
    throughout a stack (all grid pictures across all planes). 
    This is achieved by calculating a local cross correlation of 
    size (b_box_halfwidth * 2)**2) around each user chosen point across 
    adjacent planes, and collecting the extracted offset

    
    Parameters
    ----------
    grid_image : np.array : planes x 3 
    grid_points_current : np.array : user defined grid points (2D grid) 
    plane_idx_current : int : current plane index that 
                              `grid_points_current` was collected from
    b_box_halfwidth : float : bounding box half width in pixels    
    upsample_factor : int : Upsampling factor. 
                            Bounding box images will be registered to within 
                            1 / upsample_factor of a pixel 
                            see: skimage.registration.phase_cross_correlation
                            Value 250 works well without slowing it all down too much

    Returns
    -------
    sorted_point_dict : dict : dictionary of 2D points across planes (keys are plane indices)
    '''

    # Initialize dictionary of points
    dict_points = {}
    dict_points[plane_idx_current] = grid_points_current

    # There are two arrays of indices, one going towards zero, the other going to grid_image.shape[0]
    # i.e. going outwards from the user selected plane towards the edges of the stack (plane 0 to plane end)
    to_end  = np.arange(plane_idx_current, grid_image.shape[0])[1:]
    to_zero = np.arange(plane_idx_current, -1, -1)[1:]

    # Go to adjacent plane - upwards
    # ... initialize
    last_idx    = plane_idx_current
    last_points = grid_points_current

    if len(to_end): 
        for idx in progress(to_end): 
            current_plane = grid_image[last_idx, :, :]  
            next_plane    = grid_image[idx, :, :]
            
            corr_points = []
            for point in last_points:
                point_int = np.round(point).astype(int)
                bound_b_img = current_plane[point_int[0]-b_box_halfwidth:point_int[0]+b_box_halfwidth,
                                            point_int[1]-b_box_halfwidth:point_int[1]+b_box_halfwidth]
            
                bound_b_img_next = next_plane[point_int[0]-b_box_halfwidth:point_int[0]+b_box_halfwidth,
                                            point_int[1]-b_box_halfwidth:point_int[1]+b_box_halfwidth]

                # get phase corr offset
                image = bound_b_img
                offset_image = bound_b_img_next           
                shift, _, _  = phase_cross_correlation(image, 
                                                    offset_image,
                                                    upsample_factor=upsample_factor,
                                                    normalization=None,
                                                    )
                shift_x, shift_y = shift
                corr_points.append([point_int[0]-shift_x, point_int[1]-shift_y])
            
            last_idx = idx
            corr_points = np.stack(corr_points)
            dict_points[idx] = corr_points
            last_points = corr_points

            

    # Go to adjacent plane - to zero
    # ... initialize
    last_idx    = plane_idx_current
    last_points = grid_points_current

    if len(to_zero): 
        for idx in progress(to_zero): 
            current_plane = grid_image[last_idx, :, :]
            next_plane    = grid_image[idx, :, :]
            
            corr_points = []
            for point in last_points:
                point_int = np.round(point).astype(int)
                bound_b_img = current_plane[point_int[0]-b_box_halfwidth:point_int[0]+b_box_halfwidth,
                                            point_int[1]-b_box_halfwidth:point_int[1]+b_box_halfwidth]
            
                bound_b_img_next = next_plane[point_int[0]-b_box_halfwidth:point_int[0]+b_box_halfwidth,
                                            point_int[1]-b_box_halfwidth:point_int[1]+b_box_halfwidth]

                # get phase corr offset
                image = bound_b_img
                offset_image = bound_b_img_next
                shift, _, _  = phase_cross_correlation(image, 
                                                    offset_image,
                                                    upsample_factor=upsample_factor,
                                                    normalization=None,
                                                    )
                shift_x, shift_y = shift
                corr_points.append([point_int[0]-shift_x, point_int[1]-shift_y])
            
            last_idx = idx
            corr_points = np.stack(corr_points)
            dict_points[idx] = corr_points
            last_points = corr_points
    
    # Sort dictionary by plane index
    sorted_point_dict = OrderedDict(sorted(dict_points.items()))
    return sorted_point_dict


def unwarp(usr_dots, 
           grid_dots, 
           grid_image_original
           ):

    unwarped = warp_images(
                from_points   = usr_dots,
                to_points     = grid_dots,
                images        = [grid_image_original],
                output_region = [0, 0, grid_image_original.shape[1], grid_image_original.shape[0]],
                interpolation_order = 1,
                approximate_grid = 1,
                )[0]
    # Check whether margins are free
    col1 = (unwarped[0,:] == 0).all()
    col2 = (unwarped[-1,:] == 0).all()
    row1 = (unwarped[:,0] == 0).all()
    row2 = (unwarped[:,-1] == 0).all()

    status = col1 == col2 == row1 == row2 == True
    # So IF status == True, this means that none of the borders is touched
    return unwarped, status


def get_optimal_unwarp(status,
                       margin,
                       usr_dots,
                       grid_image_original,
                       no_rows,
                       no_cols,
                       ):

    '''
    For the case that the unwarped image is touching the border of the image,
    it cannot be guaranteed that information is getting lost during (after) unwarping.

    The reverse is also bad: If the image is NOT touching any border, that means that 
    the warping artifically shrank the unwarped result compared to the original image 
    dimensions, which we want to prevent. 

    Therefore, systematically vary the spacing of the grid of (perfect) dots 
    (determined by initial margin to border), and run unwarping until no more touching
    of the border is detected

    "status" is output of unwarp() above and determines the initial condition:
    status == False: touching
    status == True:  not touching
    
    '''
    if status == True:
        while status: 
            print(f'Margin now at {margin:.4f}')
            margin-=0.005
            grid_dots_ = generate_perfect_grid(data = grid_image_original,
                                               rows = no_rows,
                                               cols = no_cols,
                                               start_margin = margin,
                                              )
            unwarped, status = unwarp(usr_dots, grid_dots_, grid_image_original)
    else:
        while not status: 
            print(f'Margin now at {margin:.4f}')
            margin+=0.005
            grid_dots_ = generate_perfect_grid(data = grid_image_original,
                                               rows = no_rows,
                                               cols = no_cols,
                                               start_margin = margin,
                                               )
            unwarped, status = unwarp(usr_dots, grid_dots_, grid_image_original)

    return unwarped, margin