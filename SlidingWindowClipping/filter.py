import pyclipper
import numpy as np

def polygonIntersection(polygon, clip):
    subj=(polygon, ())
    pc = pyclipper.Pyclipper()
    pc.AddPath(clip, pyclipper.PT_CLIP, True)
    pc.AddPaths(subj, pyclipper.PT_SUBJECT, True)
    solution = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
    if solution==[]:
        return []
    else:
        return solution[0]

def polyArea(VertexList):
    if len(VertexList)<=1:
        return 0
    [x,y]=zip(*VertexList)
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))


# determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
def pointInsidePolygon(point, poly):
    x=point[0]
    y=point[1]
    n = len(poly)
    inside =False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside

def isWinIntersect(contour, win, intersectRatio, keepDotContour=True):
    if len(contour)==1:
        if pointInsidePolygon(contour[0], win):
            return True
        else:
            return False
    intersect = polygonIntersection(contour, win)
    if intersect==[] or keepDotContour==False:
        return False
    if polyArea(intersect) > polyArea(contour)*intersectRatio or polyArea(intersect) > polyArea(win)*intersectRatio :
        return True
    else:
        return False

def winFilter(contour, winList, intersectRatio):
    positiveFlag = [isWinIntersect(contour=contour, win=win, intersectRatio=intersectRatio) for win in winList]
    positiveSamples=[]
    negativeSamples=[]
    for winID in range(len(winList)):
        if positiveFlag[winID]:
            positiveSamples.append(winList[winID][0])
        else:
            negativeSamples.append(winList[winID][0])

    return (positiveSamples, negativeSamples)
