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
