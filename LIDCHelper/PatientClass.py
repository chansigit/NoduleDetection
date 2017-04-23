import glob
#import load_scan
#from  .  import NoduleInfo

from . import DICOM_Helper
from . import XML_Helper

class Patient:
    def __init__(self, dir):
        # File Path Information
        self.patientPath = dir
        self.nodulePath  = glob.glob("%s/*.xml" % self.patientPath)[0]

        # CT Image Information
        self.sliceList   = DICOM_Helper.load_scan(self.patientPath)
        self.pixelList   = DICOM_Helper.get_pixels_HU(self.sliceList)
        self.sliceCnt    = len(self.sliceList)
        self.sliceSize   = self.pixelList[0].shape
        self.ZCoords     = [slice.ImagePositionPatient[2] for slice in self.sliceList]
        self.thickness   = self.sliceList[0].SliceThickness
        # Nodule annotation
        self.noduleInfo  = XML_Helper.NoduleInfo(self.nodulePath)

    # This function supports direct slice extracting by `patient[-35.0]`
    # using Z-coordinate as subscript
    def __getitem__(self, ZCoord):
        idx = DICOM_Helper.getIndexByZCoord(self.sliceList, ZCoord)
        return self.sliceList[idx]

    # This function support direct CT-Value extracting by `patient[-35.0]`
    # using Z-coordinate as subscript
    def __call__(self, ZCoord):
        idx = DICOM_Helper.getIndexByZCoord(self.sliceList, ZCoord)
        return self.pixelList[idx]
