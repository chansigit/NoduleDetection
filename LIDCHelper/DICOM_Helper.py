import os
import dicom
import numpy as np

# ==============================================================================
# DICOM folder loading
#    This function accepts a path that contains one patient's DICOM CT slices in a scan
#    and returns a python list whose element is sorted DICOM CT slices.
#    The sorting key is `slice.ImagePositionPatient[2]`, i.e. the z-coordinate value.
#    The function also assign each slice's thickness as the first 2 slices' margin.
#    NOTE THAT only files with `.dcm` extension can be correctly identified.
def load_scan(path):
    slices = []
    # find al files ending with dcm
    for s in os.listdir(path):
        if s.endswith('dcm'):
            slices.append(dicom.read_file(path + '/' + s))

    # sort slices
    slices.sort(key = lambda x: float(x.ImagePositionPatient[2]), reverse=True)

    # assign thickness for each slice
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices


# ==============================================================================
# Get pixel information from slices
#    This function accepts a python list containing DICOM CT slices produced
#    by load_scan(PATH_OF_DICOM_DIR)
#    and returns a numerical 3-d array whose pixels correspond to CT values.
#    The 1st dimension corresponds to the z-coordinate of each slice
#    The 2nd and 3rd dimension correspond to the x and y coordinates of one image
def get_pixels_HU(slices):
    image = np.stack([s.pixel_array for s in slices])
    # Convert to int16 (from sometimes int16),
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)

    # Set outside-of-scan pixels to 0
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0

    # Convert to Hounsfield units (HU)
    for slice_number in range(len(slices)):
        intercept = slices[slice_number].RescaleIntercept
        slope     = slices[slice_number].RescaleSlope
        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)
        image[slice_number] += np.int16(intercept)

    return np.array(image, dtype=np.int16)


# ==============================================================================
# Get Index of the slice with specified Z-coordinate
#     This function accepts a python list containing DICOM CT slices produced
#     by load_scan(PATH_OF_DICOM_DIR)
#     and returns the single slice whose Z-coordinate corresponds to ZCoord
def getIndexByZCoord(slices, ZCoord):
    FirstPosition = slices[0].ImagePositionPatient[2]
    Thickness     = slices[0].SliceThickness
    idx = int((FirstPosition-ZCoord)/Thickness)
    if slices[idx].ImagePositionPatient[2] == ZCoord:
        return idx
    else:
        raise IndexError('ZCoord %f not found'%ZCoord)

def getWindowFromSlice(ctMatrix, leftUpPos, winSize):
    xlim, ylim= ctMatrix.shape
    return ctMatrix[leftUpPos[0]:leftUpPos[0]+winSize, leftUpPos[1]:leftUpPos[1]+winSize]


# ==============================================================================
