import numpy as np
import pandas as pd
import os

import dicom
from skimage import measure, morphology
from skimage.segmentation import clear_border
from skimage.morphology import ball, disk, dilation, binary_erosion, remove_small_objects, erosion, closing, reconstruction, binary_closing
from skimage.morphology import binary_dilation, binary_opening
from skimage.filters import roberts, sobel
from scipy import ndimage as ndi
# ==============================================================================
# This section is adopted from
# https://www.kaggle.com/mtfall/data-science-bowl-2017/my-idea-for-lung-segmentation
# ==============================================================================

def largest_label_volume(im, bg=-1):
    vals, counts = np.unique(im, return_counts=True)

    counts = counts[vals != bg]
    vals = vals[vals != bg]

    if len(counts) > 0:
        return vals[np.argmax(counts)]
    else:
        return None


# This function accepts an CT image pixel matrix in HU,
# and returns a mask.
def segment_lung_mask(image, fill_lung_structures=True):
    # not actually binary, but 1 and 2.
    # 0 is treated as background, which we do not want
    binary_image = np.array(image > -320, dtype=np.int8)+1
    binary_image = morphology.erosion(morphology.dilation(binary_image))
    labels = measure.label(binary_image)

    # Pick the pixel in the very corner to determine which label is air.
    #   Improvement: Pick multiple background labels from around the patient
    #   More resistant to "trays" on which the patient lays cutting the air
    #   around the person in half
    background_label = labels[0,0,0]

    #Fill the air around the person
    binary_image[background_label == labels] = 2

    # Method of filling the lung structures (that is superior to something like
    # morphological closing)
    if fill_lung_structures:
        # For every slice we determine the largest solid structure
        for i, axial_slice in enumerate(binary_image):
            axial_slice = axial_slice - 1
            labeling = measure.label(axial_slice)
            l_max = largest_label_volume(labeling, bg=0)

            if l_max is not None: #This slice contains some lung
                binary_image[i][labeling != l_max] = 1


    binary_image -= 1 #Make the image actual binary
    binary_image = 1-binary_image # Invert it, lungs are now 1

    # Remove other air pockets insided body
    labels = measure.label(binary_image, background=0)
    l_max = largest_label_volume(labels, bg=0)
    if l_max is not None: # There are air pockets
        binary_image[labels != l_max] = 0

    return binary_image







#This funtion segments the lungs from the given 2D slice.
def get_segmented_lungs(im, THRESHOLD=-320, erosionSize=2, closureSize=15):
    #Step 1: Convert into a binary image.
    binary = im < THRESHOLD

    # Step 2: Remove the blobs connected to the border of the image.
    cleared = clear_border(binary)

    # Step 3: Label the image.
    label_image = measure.label(cleared)

    # Step 4: Keep the labels with 2 largest areas.
    areas = [r.area for r in measure.regionprops(label_image)]
    areas.sort()
    if len(areas) > 2:
        for region in measure.regionprops(label_image):
            if region.area < areas[-2]:
                for coordinates in region.coords:
                    label_image[coordinates[0], coordinates[1]] = 0
    binary = label_image > 0

    # Step 5: Erosion operation with a disk of radius 2. This operation is seperate the lung nodules attached to the blood vessels.
    selem = disk(erosionSize)
    binary = binary_erosion(binary, selem)

    #Step 6: Closure operation with a disk of radius 10. This operation is to keep nodules attached to the lung wall.
    selem = disk(closureSize)
    binary = binary_closing(binary, selem)

    # Step 7: Fill in the small holes inside the binary mask of lungs.
    edges = roberts(binary)
    binary = ndi.binary_fill_holes(edges)
    intRes= binary.astype(int)
    #return binary
    return intRes
