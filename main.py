from LIDCHelper.PatientClass import Patient

patientPath= 'E:/code/dicom_data/1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
p=Patient(patientPath)
#print((p.ZCoords))
#p.showSlice(ZCoord=-117.5)
#p.showContour(ZCoord=-117.5,alpha=0.0,radius=6)

maskZ117 = p.getMaskByZCoord(ZCoord=-117.5)
print(type(maskZ117))
print(maskZ117[0:0+3, 0:0+4])
print(maskZ117[180:180+60, 180:180+60].sum())
p.showMask(ZCoord=-117.5)


[positiveSamples, negativeSamples, size]=p.getSampleWin(winSize=39, overlapRatio=0.35)
print(positiveSamples)
