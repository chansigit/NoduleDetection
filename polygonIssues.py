# This file handles:
# polygon intersection (clip)
# polygon visualization
# polygon area calculation

import pyclipper
pts=[(180, 200), (260, 200), (260, 150), (180, 150)]
clip=((190, 210), (240, 210), (240, 130), (190, 130))
# this function support integer points only
def polygonIntersection(polygon, clip):
    subj=(polygon, ())
    pc = pyclipper.Pyclipper()
    pc.AddPath(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)
    solution = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    return solution[0]

clipped=(polygonIntersection(pts, clip))
##################################################################################
##################################################################################
import numpy as np
x = np.arange(0, 1, 0.001)
y = list(map(lambda a:a*a, x))
x=np.append(x,1)
y=np.append(y,0)
points=list(zip(x,y))
print(points)

def PolyArea(VertexList):
    [x,y]=zip(*VertexList)
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))
PolyArea(points)
##################################################################################
##################################################################################



filename='E:/code/dicom_data/1.3.6.1.4.1.14519.5.2.1.6279.6001.179049373636438705059720603192/000065.dcm'
filename='E:/博一下/4-17广州交流/广东人民医院20170418CT training set/non-invasive/P343652/RUL-mPLC-LW-1.25/RDLGIJSC/WRQNTGHU/I1570000'
import dicom
import PIL
from dicom.contrib.pydicom_PIL import show_PIL
from dicom.contrib.pydicom_PIL import get_LUT_value
ds = dicom.read_file(filename)

image = get_LUT_value(data=ds.pixel_array, window=ds.WindowWidth, level=ds.WindowCenter)
im = PIL.Image.fromarray(image).convert('L')
#im.show()


import pylab

x=[100,110,120,130,140,150,160]
y=[100,100,100,100,110,110,110]
pylab.imshow(ds.pixel_array, cmap=pylab.cm.bone)
pylab.plot(x,y,'.')

import matplotlib.pyplot as plt
from  matplotlib.patches import Polygon
from  matplotlib.patches import Circle
pointListX=(100,300,200)
pointListY=(100,200,400)
xyList = list(zip(pointListX, pointListY))
p = Polygon(xyList, alpha=0.4)
plt.gca().add_artist(p)

pointListX=(0,400,250    )
pointListY=(460,500,200)
xyList = list(zip(pointListX, pointListY))
p = Polygon(xyList)
p.set_alpha(0.3)
p.set_color('m')
plt.gca().add_artist(p)

cir = Circle(xy=(256,256), radius=5)
cir.set_alpha(0.5)
cir.set_color('b')
plt.gca().add_artist(cir)

#pylab.show()
plt.savefig('demo.png',transparent=True, dpi=1200)
