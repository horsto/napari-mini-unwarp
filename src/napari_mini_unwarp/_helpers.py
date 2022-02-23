### HELPER FUNCTIONS
import numpy as np
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
    HEIGHT = data.shape[1]
    WIDTH  = data.shape[0]

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



def unwarp(usr_dots, grid_dots, grid_image_original):
    unwarped = warp_images(
                from_points   = usr_dots,
                to_points     = grid_dots,
                images        = [grid_image_original],
                output_region = [0, 0, grid_image_original.shape[1], grid_image_original.shape[0]],
                interpolation_order = 5,
                approximate_grid = 1,
                )[0]
    # Check whether margins are free
    col1 = (unwarped[0,:] == 0).all()
    col2 = (unwarped[-1,:] == 0).all()
    row1 = (unwarped[:,0] == 0).all()
    row2 = (unwarped[:,-1] == 0).all()

    status = col1 == col2 == row1 == row2 == True
    return unwarped, status
