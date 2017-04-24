import glob
import dicom
import PIL
import pylab

from . import DICOM_Helper
from . import XML_Helper

import matplotlib.pyplot as plt
from  matplotlib.patches import Polygon
from  matplotlib.patches import Circle

def drawPolygon(poly, color, alpha=0.5):
    shape=Polygon(poly, alpha=alpha)
    shape.set_alpha(alpha)
    shape.set_color(color)
    plt.gca().add_artist(shape)

def drawPoint(point, radius, color,alpha=0.5):
    cir = Circle(point, radius=radius)
    cir.set_alpha(alpha)
    cir.set_color(color)
    plt.gca().add_artist(cir)


class Patient:
    'Patient Class- dicom information and XML nodule information integrated'
    # ==========================================================================
    def __init__(self, dir):
        # File Path Information
        self.patientPath = dir
        self.nodulePath  = glob.glob("%s/*.xml" % self.patientPath)[0]

        # CT Image Information
        self.sliceList   = DICOM_Helper.load_scan(self.patientPath)
        self.pixelList   = DICOM_Helper.get_pixels_HU(self.sliceList)
        self.sliceCnt    = len(self.sliceList)
        self.sliceSize   = self.pixelList[0].shape
        self.ZCoords     = [float(slice.ImagePositionPatient[2]) for slice in self.sliceList]
        self.thickness   = self.sliceList[0].SliceThickness

        # -------------------------------------------------------
        # Nodule annotation
        self.noduleInfo  = XML_Helper.NoduleInfo(self.nodulePath)

        # 参加结节诊断的医生数目
        self.doctorCnt   = self.noduleInfo.getDoctorCount()

        # 所有包含结节的slice的z坐标
        self.nodule_ZCoords = self.noduleInfo.getAllZCoords()

        # 所有医生诊断出来的所有结节的z坐标    returns a list of set
        self.doctor_ZCoords = [ self.noduleInfo.getDoctorZCoords(doctorID) for doctorID in range(self.doctorCnt)]

        # 所有医生诊断出来的所有结节的数目     returns a list of int
        self.doctorCountOut = [ self.noduleInfo.getDoctorCountOut(doctorID) for doctorID in range(self.doctorCnt)]


    # ==========================================================================
    # This function supports direct slice extracting by `patient[-35.0]`
    # using Z-coordinate as subscript
    def __getitem__(self, ZCoord):
        idx = DICOM_Helper.getIndexByZCoord(self.sliceList, ZCoord)
        return self.sliceList[idx]

    # ==========================================================================
    # This function support direct CT-Value extracting by `patient[-35.0]`
    # using Z-coordinate as subscript
    def __call__(self, ZCoord):
        idx = DICOM_Helper.getIndexByZCoord(self.sliceList, ZCoord)
        return self.pixelList[idx]

    # ==========================================================================
    def showSlice(self, ZCoord):
        idx = DICOM_Helper.getIndexByZCoord(self.sliceList, ZCoord)
        sliceImage = self.pixelList[idx]
        pylab.imshow(sliceImage, cmap=pylab.cm.bone)
        pylab.show()

    # ==========================================================================
    def showContour(self, ZCoord):
        idx = DICOM_Helper.getIndexByZCoord(self.sliceList, ZCoord)
        sliceImage = self.pixelList[idx]
        pylab.imshow(sliceImage, cmap=pylab.cm.bone)
        pylab.show()


# lung segment
# https://www.kaggle.com/gzuidhof/data-science-bowl-2017/full-preprocessing-tutorial
# https://www.kaggle.com/mtfall/data-science-bowl-2017/my-idea-for-lung-segmentation
# https://www.kaggle.com/ankasor/data-science-bowl-2017/improved-lung-segmentation-using-watershed
