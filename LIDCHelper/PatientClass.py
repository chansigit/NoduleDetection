import glob
import dicom
import PIL
import pylab

from . import DICOM_Helper
from . import XML_Helper

import matplotlib.pyplot as plt
from  matplotlib.patches import Polygon
from  matplotlib.patches import Circle

def drawPolygon(poly, color, alpha=0.15):
    shape=Polygon(poly, alpha=alpha)
    shape.set_alpha(alpha)
    shape.set_color(color)
    plt.gca().add_artist(shape)

def drawPoint(point, radius, color,alpha=0.15):
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
        # this function shows the CT image at ZCoord
        try:
            idx = DICOM_Helper.getIndexByZCoord(self.sliceList, ZCoord)
        except IndexError:
            print(">> ERROR: No Slice at this ZCoord `%f`"%ZCoord)
            return
        sliceImage = self.pixelList[idx]
        pylab.imshow(sliceImage, cmap=pylab.cm.bone)
        pylab.show()

    # ==========================================================================
    def showContour(self, ZCoord, alpha=0.15, radius=6):
        # this function shows all doctors' annotation at ZCoord
        try:
            idx = DICOM_Helper.getIndexByZCoord(self.sliceList, ZCoord)
        except IndexError:
            print(">> ERROR: No Slice at this ZCoord `%f`"%ZCoord)
            return
        sliceImage = self.pixelList[idx]
        pylab.imshow(sliceImage, cmap=pylab.cm.bone)
        colorList=['b','g','c','r','m','y','k','w'] #maximum doctor cnt =8 for now
        for doctorID in range(self.doctorCnt):
            noduCnt = self.doctorCountOut[doctorID]
            for noduID in range(noduCnt):
                contour = self.noduleInfo.getNoduleEdgesByZCoord(doctorID, noduID, ZCoord)
                if contour!=[]:
                    contour = [(vertex[0],vertex[1]) for vertex in contour]
                    if len(contour)==1:
                        drawPoint(point=contour[0], radius=radius, color=colorList[doctorID], alpha=alpha)
                    else:
                        #print(contour)
                        drawPolygon(poly=contour, color=colorList[doctorID], alpha=alpha)
        pylab.show()


# next plan
# show segmentation result
# show mask
# integrate segmentation into sampling

# lung segment
# https://www.kaggle.com/gzuidhof/data-science-bowl-2017/full-preprocessing-tutorial
# https://www.kaggle.com/mtfall/data-science-bowl-2017/my-idea-for-lung-segmentation
# https://www.kaggle.com/ankasor/data-science-bowl-2017/improved-lung-segmentation-using-watershed
