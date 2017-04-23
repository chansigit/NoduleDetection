import pyclipper
import numpy as np

def polygonIntersection(polygon, clip):
    subj=(polygon, ())
    pc = pyclipper.Pyclipper()
    pc.AddPath(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)
    solution = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    return solution[0]

def PolyArea(VertexList):
    [x,y]=zip(*VertexList)
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def slidingWinFilter(contour, slidingWinList ):
    filter(isWinOverlap, slidingWinList)
