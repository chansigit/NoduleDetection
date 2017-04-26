from LIDCHelper.PatientClass import Patient
from SlidingWindowClipping.filter import winFilter
patientPath= 'E:/code/dicom_data/1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
p=Patient(patientPath)
print((p.ZCoords))
p.showSlice(ZCoord=-170)
p.showContour(ZCoord=-117.5,alpha=0.3,radius=6)
[positiveSamples, negativeSamples, size]=p.getSampleWin(winSize=39, overlapRatio=0.35)
