NoduleInfoXMLPath = 'E:/code/dicom_data/1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192/069.xml'

import xml.dom.minidom

#得到文档元素对象
dom = xml.dom.minidom.parse(NoduleInfoXMLPath)
root = dom.documentElement
print(root.nodeName)
print(root.nodeValue)
print(root.nodeType)
print(root.ELEMENT_NODE)

# XML structure
# LidcReadMessage (root)
#  |
#  --ResponseHeader
#  |     --SeriesInstanceUid
#  |     --StudyInstanceUID
#  |
#  --readingSession
#        --servicingRadiologistID
#        --UnbindedReadNodule
#              --noduleID
#              --characteristic
#              --roi
#                     --imageZposition
#                     --inclusion
#                     --edgeMap
#                         --xCoord
#                         --yCoord
#        --nonNodule

ResponseHeader= root.getElementsByTagName('ResponseHeader')[0]
StudyUIDNode = ResponseHeader.getElementsByTagName('StudyInstanceUID')[0]
SeriesUIDNode = ResponseHeader.getElementsByTagName('SeriesInstanceUid')[0]
SeriesUID = SeriesUIDNode.firstChild.data
StudyUID  = StudyUIDNode.firstChild.data
print("Dir is `%s/%s`\n\n\n"%(SeriesUID,StudyUID))




# trace to `readingSession`, each`readingSession` stores an expert's annotation.
radiologistList=[]
ExpertReadingSessions=root.getElementsByTagName('readingSession')
for radiologistIdx,radiologist in enumerate(ExpertReadingSessions):
    #ON_WHEN_DEBUG__ print(radiologist.getElementsByTagName('servicingRadiologistID')[0].firstChild.data)
    #ON_WHEN_DEBUG__ print('****************doctor%d'%radiologistIdx)
    # trace to `unblindedReadNodule`, which stores a nodule crossing multiple neighboring CT slices
    unblindedReadNodules = radiologist.getElementsByTagName('unblindedReadNodule')
    nodulesByOneRadiologist=[]
    for ubrNoduleIdx, ubrNodule in enumerate(unblindedReadNodules):
        #ON_WHEN_DEBUG__ print('======nodule %d'%ubrNoduleIdx)
        # trace to `roi`, which stores RegionOfInterest in one CT slice.
        RoiInNodule = ubrNodule.getElementsByTagName('roi')
        slicesAmongNodules=dict()
        for roiIdx, roi in enumerate(RoiInNodule):
            isContour = roi.getElementsByTagName('inclusion')[0].firstChild.data =="TRUE"
            zCoord= float(roi.getElementsByTagName('imageZposition')[0].firstChild.data)
            #ON_WHEN_DEBUG__ print('ROI%d %f'%(roiIdx,zCoord))
            roiInOneSlice=[]
            # only keep the outer edge, ignore the inner edge.
            if isContour:
                for edgeMapIdx, edgeMap in enumerate(roi.getElementsByTagName('edgeMap')):
                    xCoord= edgeMap.getElementsByTagName('xCoord')[0].firstChild.data
                    yCoord= edgeMap.getElementsByTagName('yCoord')[0].firstChild.data
                    edgePoint=(xCoord,yCoord,zCoord)
                    roiInOneSlice.append(edgePoint)
            #ON_WHEN_DEBUG__ print("# of edgepoints %d" %len(roiInOneSlice))
            slicesAmongNodules[zCoord]=roiInOneSlice
        #ON_WHEN_DEBUG__ print(slicesAmongNodules.keys())
        nodulesByOneRadiologist.append(slicesAmongNodules)
    #ON_WHEN_DEBUG__ print(len(nodulesByOneRadiologist))
    radiologistList.append(nodulesByOneRadiologist)
