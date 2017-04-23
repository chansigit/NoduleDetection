import xml.dom.minidom


class NoduleInfo(object):
	XMLStructureInfo =
'''XML structure
LidcReadMessage (root)
 |
 --ResponseHeader
 |     --SeriesInstanceUid
 |     --StudyInstanceUID
 |
 --readingSession
       --servicingRadiologistID
       --UnbindedReadNodule
             --noduleID
             --characteristic
             --roi
                    --imageZposition
                    --inclusion
                    --edgeMap
                        --xCoord
                        --yCoord
       --nonNodule
'''

    def _init_(self, filepath):
        self.NoduleInfoXMLPath = filepath
		dom = xml.dom.minidom.parse(self.NoduleInfoXMLPath)
		root = dom.documentElement

		# *************** parse responseHeader ***************
		ResponseHeader= root.getElementsByTagName('ResponseHeader')[0]
		StudyUIDNode  = ResponseHeader.getElementsByTagName('StudyInstanceUID')[0]
		SeriesUIDNode = ResponseHeader.getElementsByTagName('SeriesInstanceUid')[0]
		SeriesUID = SeriesUIDNode.firstChild.data
		StudyUID  = StudyUIDNode.firstChild.data

		# *************** parse readingSession ***************
		# trace to `readingSession`, each`readingSession` stores an expert's annotation.
		self.radiologistList=[]
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
		    self.radiologistList.append(nodulesByOneRadiologist)

    def help():
    	print(XMLStructureInfo)
