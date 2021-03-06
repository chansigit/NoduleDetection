import xml.dom.minidom

# ==============================================================================
class NoduleInfo:
    'Handling Nodule Information Stored in the XML file'
    XMLStructureInfo = '''<XML structure>
---------------------------------
LidcReadMessage (root)
 |
 --ResponseHeader
 |     --SeriesInstanceUid
 |     --StudyInstanceUID
 |
 --readingSession
 |     --servicingRadiologistID
 |     --UnbindedReadNodule
 |           --noduleID
 |           --characteristic
 |           --roi
 |                  --imageZposition
 |                  --inclusion
 |                  --edgeMap
 |                      --xCoord
 |                      --yCoord
 |     --nonNodule
 --readingSession
 |     --...
 |
 |
 --readingSession
 |     --...
 |
 ...
 |
 --readingSession
 |     --...
'''

    def help(self):
        print(self.XMLStructureInfo)

    def __init__(self, filepath):
        self.NoduleInfoXMLPath = filepath
        dom = xml.dom.minidom.parse(self.NoduleInfoXMLPath)
        root = dom.documentElement

        # *************** parse responseHeader ***************
        ResponseHeader = root.getElementsByTagName('ResponseHeader')[0]
        StudyUIDNode = ResponseHeader.getElementsByTagName('StudyInstanceUID')[
            0]
        SeriesUIDNode = ResponseHeader.getElementsByTagName('SeriesInstanceUid')[
            0]
        self.SeriesUID = SeriesUIDNode.firstChild.data
        self.StudyUID = StudyUIDNode.firstChild.data

        # *************** parse readingSession ***************
        # trace to `readingSession`, each`readingSession` stores an expert's
        # annotation.
        self.radiologistList = []
        ExpertReadingSessions = root.getElementsByTagName('readingSession')
        for radiologistIdx, radiologist in enumerate(ExpertReadingSessions):
            # ON_WHEN_DEBUG__ print(radiologist.getElementsByTagName('servicingRadiologistID')[0].firstChild.data)
            # ON_WHEN_DEBUG__ print('****************doctor%d'%radiologistIdx)
            # trace to `unblindedReadNodule`, which stores a nodule crossing
            # multiple neighboring CT slices
            unblindedReadNodules = radiologist.getElementsByTagName(
                'unblindedReadNodule')
            nodulesByOneRadiologist = []
            for ubrNoduleIdx, ubrNodule in enumerate(unblindedReadNodules):
                # ON_WHEN_DEBUG__ print('======nodule %d'%ubrNoduleIdx)
                # trace to `roi`, which stores RegionOfInterest in one CT
                # slice.
                RoiInNodule = ubrNodule.getElementsByTagName('roi')
                slicesAmongNodules = dict()
                for roiIdx, roi in enumerate(RoiInNodule):
                    isContour = roi.getElementsByTagName('inclusion')[0].firstChild.data == "TRUE"
                    if not isContour:
                        continue
                    zCoord = float(roi.getElementsByTagName('imageZposition')[0].firstChild.data)
                    # ON_WHEN_DEBUG__ print('ROI%d %f'%(roiIdx,zCoord))
                    roiInOneSlice = []
                    # only keep the outer edge, ignore the inner edge.
                    if isContour:
                        for edgeMapIdx, edgeMap in enumerate(roi.getElementsByTagName('edgeMap')):
                            xCoord = float(edgeMap.getElementsByTagName(
                                'xCoord')[0].firstChild.data)
                            yCoord = float(edgeMap.getElementsByTagName(
                                'yCoord')[0].firstChild.data)
                            edgePoint = (xCoord, yCoord, zCoord)
                            roiInOneSlice.append(edgePoint)
                    # ON_WHEN_DEBUG__ print("# of edgepoints %d"
                    # %len(roiInOneSlice))
                    slicesAmongNodules[zCoord] = roiInOneSlice
                # ON_WHEN_DEBUG__ print(slicesAmongNodules.keys())
                nodulesByOneRadiologist.append(slicesAmongNodules)
            # ON_WHEN_DEBUG__ print(len(nodulesByOneRadiologist))
            self.radiologistList.append(nodulesByOneRadiologist)

    def getSeriesInstanceUID(self):
        return self.SeriesUID

    def getStudyInstanceUID(self):
        return self.StudyUID

    def getContainningFolder(self):
        return "%s/%s" % (self.getSeriesInstanceUID(), self.getStudyInstanceUID())

    def getAllDoctorAnnotation(self):
        return self.radiologistList

    def getDoctorCount(self):
        return len(self.radiologistList)

    def getAnnotationByDoctor(self, doctorID):
        try:
            return self.radiologistList[doctorID]
        except IndexError:
            print('ERROR: doctorID exceeds doctor counts, please check if doctor < %d' %
                  self.getDoctorCount())

    def getDoctorCountOut(self, doctorID):
        try:
            return len(self.radiologistList[doctorID])
        except IndexError:
            print('ERROR: doctorID exceeds doctor counts, please check if doctor < %d' %
                  self.getDoctorCount())

    def getNoduleZCoords(self, doctorID, noduleID):
        'Returns the Z-coords that the nodule crosses'
        try:
            return list(self.radiologistList[doctorID][noduleID].keys())
        except IndexError:
            print('ERROR: doctorID or noduleID overflowed')

    def getNoduleSlices(self, doctorID, noduleID):
        'Returns a python dict() whose keys are z-coords, values are contour vertices'
        try:
            return self.radiologistList[doctorID][noduleID]
        except IndexError:
            print('ERROR: doctorID or noduleID overflowed')

    def getNoduleEdgesByZCoord(self, doctorID, noduleID, z):
        "Return a nodule's contour at a certain z-coord"
        try:
            return self.getNoduleSlices(doctorID, noduleID)[z]
        except KeyError:
            return list()

    def getDoctorZCoords(self, doctorID):
        "Return all Zcoords that has been marked by a doctor"
        docZCoords= []
        noduleCnt =self.getDoctorCountOut(doctorID=doctorID)
        for noduleID in range(noduleCnt):
            docZCoords=docZCoords+self.getNoduleZCoords(doctorID=doctorID, noduleID=noduleID)
        return set(docZCoords)

    def getAllZCoords(self):
        ZCoords=set()
        doctorCnt=self.getDoctorCount()
        for doctorID in range(doctorCnt):
            ZCoords=ZCoords | self.getDoctorZCoords(doctorID=doctorID)
        return ZCoords

# ==============================================================================
