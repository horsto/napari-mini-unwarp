"""

"""
from collections import OrderedDict
from pathlib import Path
import numpy as np
from datetime import datetime
import pickle

from tifffile import imread
import scanreader
from scanreader.exceptions import ScanImageVersionError

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
    path = Path(path)

    if path.is_dir():
        available_tifs = list(path.glob(r'*.tif'))
        if available_tifs: 
            print(f'Reading {path.as_posix()}')
            return tif_reader
        else: 
            print('No .tifs found in folder')
            return None
    elif path.is_file():
        if path.suffix == '.tif':
            print(f'Reading tif {path.as_posix()}')
            return tif_reader
        elif path.suffix == '.pkl':
            print(f'Reading pickle {path.as_posix()}')
            return pkl_raw_reader
        else:
            print('Not a .tif or .pkl file')
            return None
    else: 
        return None

def pkl_raw_reader(path):
    '''
    Reads previously collected layer data back into napari 

    path : path to .pkl (pickle) file
        
    '''

    pkl_file = open(path, "rb")
    layer_data = pickle.load(pkl_file)

    data_type = layer_data["type"]
    timestamp = layer_data["export_timestamp"]

    # Actual layer information
    data = layer_data['data']
    add_kwargs = layer_data['add_kwargs']
    layer_type = layer_data['layer_type']

    print(f'Loaded .pkl export of type {data_type} from {timestamp}')
    return [(data, add_kwargs, layer_type)]


def tif_reader(path):

    '''
    Load single image tif / tif stack or 
    a folder of tif images


    Currently accepted combinations: 
    - Single tif files (ScanImage or else)
    - Folder of ScanImage tif files 
    
    If a folder of ScanImage tif files is read in, 
    tif files will be read one-by-one and z focus information will 
    be read out automatically and added to the layer metadata. 
    For each file in the folder, a average projection will be calculated 
    and a single layer that contains all average projections will be created.

    '''

    path = Path(path)

    if path.is_dir():
        tif_dict = {}
        
        # Check whether the zoom, width, height property is the same for all files, while reading them in.
        # A similar check is performed for imaging depth (which should yield unique numbers)
        # ... add more if you can think of more ... 
        zooms = []
        widths = []
        heights = []
        
        for tif_file in path.glob(r'*.tif'):
            # Extract z position solely from file name 
            # z_height = re.search(r'(?P<position>\d+)um', str(tif_file))
            # tif_dict[float(z_height.group('position'))] = tif_file

            # Read file with scanreader (https://github.com/kavli-ntnu/scanreader)
            # for basic checks
            try: 
                scan = scanreader.read_scan(tif_file.as_posix())
            except ScanImageVersionError:
                raise NotImplementedError('Not a ScanImage .tif file')
            if scan.num_scanning_depths > 1: 
                raise NotImplementedError(f'>1 imaging plane detected in {tif_file.as_posix()}')

            z_height = scan.scanning_depths_relative[0]
            print(f'{tif_file.name:<30} ScanImage .tif with {scan.num_frames} frames, zoom {scan.zoom}, depth {z_height}')
            tif_dict[z_height] = tif_file.as_posix()
            zooms.append(scan.zoom)
            widths.append(scan.image_width)
            heights.append(scan.image_height)
            
        # Create sorted dictionary from collected files
        sorted_zpos = OrderedDict(sorted(tif_dict.items()))
        print(f'Found {len(sorted_zpos)} matching tif files across z positions [microns]:\n{list(sorted_zpos.keys())}')
        # Perform checks 
        assert len(np.unique(list(sorted_zpos.keys()))) == len(sorted_zpos.keys()), 'There seem to be duplicates in z position data'
        assert len(np.unique(zooms)) == 1, f'There seems to be more than one zoom level across tifs {np.unique(zooms)}'
        assert len(np.unique(widths)) == 1, f'Tif stacks seem to vary in width {np.unique(widths)}'
        assert len(np.unique(heights)) == 1, f'Tif stacks seem to vary in height {np.unique(heights)}'
                
        # else:
        #     # Only if the naming convention is taken as basis for file info extraction
        #     print('Folder does not contain .tif files in right format')
        #     print('Please provided a folder of .tif files in the format:')
        #     print('"___900um___.tif", where "_" is any character and "900" is a number indicating the z position')

        # Create layer
        stacked_avg = []

        for no, tif_path in enumerate(sorted_zpos.values()):
            print(f'Reading ({no+1:<2}/{len(sorted_zpos):<2}) | {tif_path}')
            scan = scanreader.read_scan(tif_path)
            average_proj = np.mean(scan, axis=-1).squeeze()
            stacked_avg.append(average_proj)

        data = np.stack(stacked_avg)
            
        add_kwargs = {'rgb': False, 'name' : 'Grid image(s)', 'metadata': sorted_zpos, 'scale': [10, 1, 1]}
        layer_type = "image"  # optional, default is "image"
        
        # Before returning, also save the file as dictionary to disk 
        save_dict = {}
        save_dict['type'] = 'Raw grid image'
        save_dict['data'] = data
        save_dict['add_kwargs'] = add_kwargs
        save_dict['layer_type'] = layer_type
        save_dict['export_timestamp'] = datetime.now()
        with open(path/'napari_grid_image_raw.pkl', "wb") as export_file:
            print('Saving grid image layer dictionary into raw data folder')
            pickle.dump(save_dict, export_file)

        return [(data, add_kwargs, layer_type)]


    elif path.is_file():
        tif_file = path

        try: 
            scan = scanreader.read_scan(tif_file.as_posix())
            if scan.shape[-1] > 1:
                print(f'Timeseries assumed')
                average_proj = np.mean(scan, axis=-1).squeeze()
                print('Created average projection')
                data = average_proj 
            else: 
                data = np.array(scan).squeeze()

        except ScanImageVersionError:
            data = imread(tif_file.as_posix())
            if len(data.shape) == 3:
                assert data.shape[1] == data.shape[2], f'Image data shape not supported ({data.shape})'
                data = np.mean(data, axis=0)

        assert len(data.shape) == 2, 'Data has more than 2 dimensions'

        add_kwargs = {'rgb': False, 'name' : 'Grid image(s)', 'metadata': {}}
        layer_type = "image"  # optional, default is "image"
        
        return [(data, add_kwargs, layer_type)]

    else:
        print(f'Type not recognized ("{path}")')

