import glob
import dicom
import PIL
import pylab

from . import DICOM_Helper
from . import XML_Helper
from . import Filter_Helper

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

    def getSampleWin(self, winSize=45, overlapRatio=0.3):
        (XMax, YMax) =self.sliceSize
        slidingStep = int(winSize*(1-overlapRatio))
        # 把所有滑动窗口的坐标预先算出来（每一层都用这一样的窗口扫）
        slidingWins=[]
        winX=0
        while winX+slidingStep<XMax:
            winY=0
            while winY+slidingStep<YMax:
                #print("leftUp=%s rightDown=%s "% (  (winX,winY),(winX+slidingStep, winY+slidingStep)  ))
                slidingWins.append( (winX,winY) )
                winY=winY+slidingStep
            winX=winX+slidingStep

        # 用滑动窗口的四个顶点坐标来存储滑动窗口，
        # 以统一为polygon的格式，方便后面做clipping
        slidingRects=[]
        for win in slidingWins:
            x=win[0]
            y=win[1]
            slidingRects.append([(x,y), (x,y+slidingStep), (x+slidingStep, y+slidingStep), (x+slidingStep,y)])


        #sampleWin=(winX,winY,winZ,size,mark)    finally changed to (winX, winY, winZ) attached to size
        positiveSamples = []
        negativeSamples = []

        doctorCnt = self.noduleInfo.getDoctorCount()
        nodule_ZCoords   = self.noduleInfo.getAllZCoords()
        doctor_ZCoords   = [ self.noduleInfo.getDoctorZCoords(doctorID) for doctorID in range(doctorCnt)]

        for z in self.ZCoords:
            # 如果z在某一个结节层里面
            if z in self.nodule_ZCoords:
                # 问每一个医生: z在不在他们标出来的结节层里面
                for doctorID in range(self.doctorCnt):
                    # 如果z这一层确实被该医生标记过，
                    # 那我们就要找是哪个结节在z这一层被该医生标记过，
                    # 并把该结节的边缘与所有的窗做交集，根据重叠面积进行判断
                    if z in self.doctor_ZCoords[doctorID]:
                        for noduleID  in range(self.doctorCountOut[doctorID]):
                            contour=self.noduleInfo.getNoduleEdgesByZCoord(doctorID, noduleID, z)
                            if contour==[]: # z层不在此结节里面标记过
                                continue
                            else: # z层在此结节里面标记过
                                # 求countour与所有窗的交集
                                # 丢弃掉第三维，变成平面图形
                                contour=[(point3d[0], point3d[1]) for point3d in contour]
                                # 给一个filter喂进去slidingRects ，过滤出符合要求的正负slidingRects的左上角顶点
                                (posWins, negWins) =Filter_Helper.winFilter(contour=contour, winList=slidingRects, intersectRatio=0.3)
                                posWins = [(win[0], win[1], z) for win in posWins]
                                negWins = [(win[0], win[1], z) for win in negWins]
                                positiveSamples += posWins
                                negativeSamples += negWins

            # z不在任何一个结节层里面，z层全层划为负样本
            else:
                negativeSamples += [ (win[0],win[1],z) for win in slidingWins ]
        return((positiveSamples,negativeSamples,winSize))


# next plan
# first encapsule the sampling
# show segmentation result
# show mask
# integrate segmentation into sampling

# lung segment
# https://www.kaggle.com/gzuidhof/data-science-bowl-2017/full-preprocessing-tutorial
# https://www.kaggle.com/mtfall/data-science-bowl-2017/my-idea-for-lung-segmentation
# https://www.kaggle.com/ankasor/data-science-bowl-2017/improved-lung-segmentation-using-watershed
