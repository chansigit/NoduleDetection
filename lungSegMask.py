import numpy as np
import pandas as pd
import dicom
import os
import scipy.ndimage
import matplotlib.pyplot as plt
import glob
from skimage import measure, transform
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation
from skimage.segmentation import clear_border
from skimage.morphology import ball, disk, dilation, binary_erosion, remove_small_objects, erosion, closing, reconstruction, binary_closing
from skimage.morphology import binary_dilation, binary_opening
from skimage.filters import roberts, sobel
from scipy import ndimage as ndi
import cPickle as pickle


def load_scan(path):
    slices = []
    for s in os.listdir(path):
        if s.endswith('dcm'):
            slices.append(dicom.read_file(path + '/' + s))
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[
                                 2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(
            slices[0].SliceLocation - slices[1].SliceLocation)

    for s in slices:
        s.SliceThickness = slice_thickness

    return slices


def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])
    # Convert to int16 (from sometimes int16),
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)

    # Set outside-of-scan pixels to 0
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0

    # Convert to Hounsfield units (HU)
    for slice_number in xrange(len(slices)):

        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope

        if slope != 1:
            image[slice_number] = slope * \
                image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)

        image[slice_number] += np.int16(intercept)

    return np.array(image, dtype=np.int16)


def largest_label_volume(im, bg=-1):
    vals, counts = np.unique(im, return_counts=True)

    counts = counts[vals != bg]
    vals = vals[vals != bg]

    if len(counts) > 0:
        return vals[np.argmax(counts)]
    else:
        return None


def segment_lung_mask(image, fill_lung_structures=True, THRESHOLD=-320):

    # not actually binary, but 1 and 2.
    # 0 is treated as background, which we do not want
    binary_image = np.array(image > THRESHOLD, dtype=np.int8) + 1
    labels = measure.label(binary_image)

    # Pick the pixel in the very corner to determine which label is air.
    #   Improvement: Pick multiple background labels from around the patient
    #   More resistant to "trays" on which the patient lays cutting the air
    #   around the person in half
    background_label = labels[0, 0, 0]

    # Fill the air around the person
    binary_image[background_label == labels] = 2

    # Method of filling the lung structures (that is superior to something like
    # morphological closing)
    if fill_lung_structures:
        # For every slice we determine the largest solid structure
        for i, axial_slice in enumerate(binary_image):
            axial_slice = axial_slice - 1
            labeling = measure.label(axial_slice)
            l_max = largest_label_volume(labeling, bg=0)

            if l_max is not None:  # This slice contains some lung
                binary_image[i][labeling != l_max] = 1

    binary_image -= 1  # Make the image actual binary
    binary_image = 1 - binary_image  # Invert it, lungs are now 1

    # Remove other air pockets insided body
    labels = measure.label(binary_image, background=0)
    l_max = largest_label_volume(labels, bg=0)
    if l_max is not None:  # There are air pockets
        binary_image[labels != l_max] = 0

    return binary_image


def get_segmented_lungs(im, plot=False, THRESHOLD=-320):
    '''
    This funtion segments the lungs from the given 2D slice.
    '''
    if plot == True:
        f, plots = plt.subplots(3, 3, figsize=(5, 40))
    '''
    Step 1: Convert into a binary image. 
    '''
    binary = im < THRESHOLD
    if plot == True:
        plots[0, 0].axis('off')
        plots[0, 0].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 2: Remove the blobs connected to the border of the image.
    '''
    cleared = clear_border(binary)
    if plot == True:
        plots[1, 0].axis('off')
        plots[1, 0].imshow(cleared, cmap=plt.cm.bone)
    '''
    Step 3: Label the image.
    '''
    label_image = measure.label(cleared)
    if plot == True:
        plots[2, 0].axis('off')
        plots[2, 0].imshow(label_image, cmap=plt.cm.bone)
    '''
    Step 4: Keep the labels with 2 largest areas.
    '''
    areas = [r.area for r in measure.regionprops(label_image)]
    areas.sort()
    # print areas
    if len(areas) > 2:
        for region in measure.regionprops(label_image):
            if region.area < areas[-2]:
                for coordinates in region.coords:
                    label_image[coordinates[0], coordinates[1]] = 0
    binary = label_image > 0
    if plot == True:
        plots[0, 1].axis('off')
        plots[0, 1].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 5: Erosion operation with a disk of radius 2. This operation is 
    seperate the lung nodules attached to the blood vessels.
    '''
    selem = disk(2)
    binary = binary_erosion(binary, selem)
    if plot == True:
        plots[1, 1].axis('off')
        plots[1, 1].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 6: Closure operation with a disk of radius 10. This operation is 
    to keep nodules attached to the lung wall.
    '''
    selem = disk(15)
    binary = binary_closing(binary, selem)
    if plot == True:
        plots[2, 1].axis('off')
        plots[2, 1].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 7: Fill in the small holes inside the binary mask of lungs.
    '''
    edges = roberts(binary)
    binary = ndi.binary_fill_holes(edges)
    if plot == True:
        plots[0, 2].axis('off')
        plots[0, 2].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 8: Superimpose the binary mask on the input image.
    '''
    
    get_high_vals = binary == 0
    im[get_high_vals] = 0
    if plot == True:
        plots[1, 2].axis('off')
        plots[1, 2].imshow(im, cmap=plt.cm.bone)

    return im,binary


# here="E:/code/segmentation/LIDC"
here = "/data640/TCIA-LIDC-IDRI/DOI"
output = "/data640/TCIA-LIDC-IDRI_lungMaskExtracted"
for root, dirs, files in os.walk(here):
    if not dirs:
        if len([f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]) > 20:
            # then `root` is the folder that contains the dcm files
            path = root
            patientName = path.split('/')[4]

            patient = load_scan(path)
            patientImg = get_pixels_hu(patient)
            for imgID in xrange(len(patientImg)):
                lungImg, binary = get_segmented_lungs(im=patientImg[imgID], plot=False, THRESHOLD=-320)
                slicePos = patient[imgID].InstanceNumber
                sliceName = os.path.join(output, patientName)
                if os.path.isdir(sliceName) == False:
                    os.makedirs(sliceName)
                sliceName = os.path.join(
                    sliceName, "%s.mask.pickle" % slicePos)
                pickle.dump(binary, open(sliceName,"wb"))
                print(sliceName)
