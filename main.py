from LIDCHelper.PatientClass import Patient

patientPath= 'E:/code/dicom_data/1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192'
p=Patient(patientPath)

print(p.sliceCnt)
print((p.pixelList))
print(p.sliceList[10].ImagePositionPatient)
print(p[-35.0])
print(p(-35.0))
print((p.ZCoords))
print(p.thickness)


print(p.noduleInfo.getContainningFolder())
print(p.noduleInfo.getDoctorCount())
#print(p.noduleInfo.getAllDoctorAnnotation())
