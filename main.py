from LIDCHelper.PatientClass import Patient
from SlidingWindowClipping.Filter import winFilter
patientPath= 'E:/code/dicom_data/1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
p=Patient(patientPath)
print((p.ZCoords))
p.showSlice(ZCoord=-170)
p.showContour(ZCoord=-117.5,alpha=0.3,radius=6)



# print(p.sliceCnt)
# print((p.pixelList))
# print(p.sliceList[10].ImagePositionPatient)
# print(p[-35.0])
# print(p(-35.0))
# print(p.thickness)
#
#
# print(p.noduleInfo.getContainningFolder())
# print(p.noduleInfo.getDoctorCount())


(XMax, YMax) =p.sliceSize
winSize = 45
overlapRatio = 0.3
slidingStep = int(winSize*(1-overlapRatio))

# 把所有滑动窗口的坐标预先算出来（每一层其实都一样）
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

doctorCnt = p.noduleInfo.getDoctorCount()
nodule_ZCoords   = p.noduleInfo.getAllZCoords()
doctor_ZCoords   = [ p.noduleInfo.getDoctorZCoords(doctorID) for doctorID in range(doctorCnt)]


for z in p.ZCoords:
    # 如果z在某一个结节层里面
    if z in p.nodule_ZCoords:
        # 问每一个医生: z在不在他们标出来的结节层里面
        for doctorID in range(p.doctorCnt):
            # 如果z这一层确实被该医生标记过，
            # 那我们就要找是哪个结节在z这一层被该医生标记过，
            # 并把该结节的边缘与所有的窗做交集，根据重叠面积进行判断
            if z in p.doctor_ZCoords[doctorID]:
                for noduleID  in range(p.doctorCountOut[doctorID]):
                    contour=p.noduleInfo.getNoduleEdgesByZCoord(doctorID, noduleID, z)
                    if contour==[]: # z层不在此结节里面标记过
                        continue
                    else: # z层在此结节里面标记过
                        # 求countour与所有窗的交集
                        print("Doctor=%d, z=%f"%(doctorID,z))
                        # 丢弃掉第三维，变成平面图形
                        contour=[(point3d[0], point3d[1]) for point3d in contour]
                        # 给一个filter喂进去slidingRects ，过滤出符合要求的正负slidingRects的左上角顶点
                        (posWins, negWins) =winFilter(contour=contour, winList=slidingRects, intersectRatio=0.3)
                        posWins = [(win[0], win[1], z) for win in posWins]
                        negWins = [(win[0], win[1], z) for win in negWins]
                        positiveSamples += posWins
                        negativeSamples += negWins

    # z不在任何一个结节层里面，z层全层划为负样本
    else:
        negativeSamples += [ (win[0],win[1],z) for win in slidingWins ]

for i in positiveSamples:
    print(i)
    print(positiveSamples)
