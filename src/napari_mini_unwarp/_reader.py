"""

"""
import numpy as np
from tifffile import imread

def napari_get_reader(path):
    """
    Decide which file type / reader function you are dealing with. 
    Here, because we are only dealing with single Tif files, the path is 
    just checked for suffix .tif 

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.

    """

    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # We are not dealing with multiple files, so abort early on
        #path = path[0]
        return None

    # If we know we cannot read the file, we immediately return None.
    if not path.endswith(".tif"):
        return None
    else: 
        print('Tif detected!')

    # Otherwise - switch to loading that file with the appropriate reader
    return tif_reader


def tif_reader(path):
    '''
    Load single tif or tif stack 
    
    
    '''
    original_tif = imread(path)

    print(f'Dimensions of tif: {original_tif.shape}')
    if len(original_tif.shape) == 3:
        print(f'Timeseries assumed')
        assert original_tif.shape[1] == original_tif.shape[2], 'Dimensions not supported'
        original_tif = np.mean(original_tif, axis=0)
        print('Created average projection')
    
    data = original_tif

    # Optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {'rgb': False, 'name' : 'Grid image'}
    layer_type = "image"  # optional, default is "image"
    
    return [(data, add_kwargs, layer_type)]


# def reader_function(path):
#     """Take a path or list of paths and return a list of LayerData tuples.

#     Readers are expected to return data as a list of tuples, where each tuple
#     is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
#     both optional.

#     Parameters
#     ----------
#     path : str or list of str
#         Path to file, or list of paths.

#     Returns
#     -------
#     layer_data : list of tuples
#         A list of LayerData tuples where each tuple in the list contains
#         (data, metadata, layer_type), where data is a numpy array, metadata is
#         a dict of keyword arguments for the corresponding viewer.add_* method
#         in napari, and layer_type is a lower-case string naming the type of layer.
#         Both "meta", and "layer_type" are optional. napari will default to
#         layer_type=="image" if not provided
#     """
#     # handle both a string and a list of strings
#     paths = [path] if isinstance(path, str) else path
#     # load all files into array
#     arrays = [np.load(_path) for _path in paths]
#     # stack arrays into single array
#     data = np.squeeze(np.stack(arrays))

#     # optional kwargs for the corresponding viewer.add_* method
#     add_kwargs = {}

#     layer_type = "image"  # optional, default is "image"
#     return [(data, add_kwargs, layer_type)]
