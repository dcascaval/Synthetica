import random
import copy

class Tetrahedron():

    faceList = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]

    def __init__(self, position, size):
        self.pos = position
        self.size = size
        pt1 = PVector(-0.288, 0.0, 0.5)
        pt2 = PVector(-0.288, 0.0, -0.5)
        pt3 = PVector(0.576, 0.0, 0.0)
        pt4 = PVector(0.0, 0.816, 0.0)
        self.vertices = [pt1, pt2, pt3, pt4]
        for pt in self.vertices:
            pt.mult(self.size)

    def display(self):
        ptList = self.vertices
        hu = map(mouseX, 0, width, 0, 255)
        sat = map(mouseY, 0, height, 0, 255)
        colorMode(HSB)
        fill(hu, sat, 200)
        stroke(255)
        for face in Tetrahedron.faceList:
            beginShape(TRIANGLE)
            for i in range(3):
                vertex(ptList[face[i]].x, ptList[face[i]].y, ptList[face[i]].z)
            endShape()
        
    def drawTetrahedron(self,vertices,depth = 0):
        for face in Tetrahedron.faceList:
            beginShape(TRIANGLE)
            for i in range(3):
                #fill(0)
                noFill()
                hu = (map(mouseX + (depth*250),0,width,0,100))
                #hu = map(depth,0,3,0,255)
                sat = (map(mouseY,0,height,0,200))
                colorMode(HSB)
                # strokeWeight(2)
                stroke(hu,sat,map(i,0,2,0,255))
                vertex(vertices[face[i]].x, vertices[face[i]].y, vertices[face[i]].z)
            endShape()

    def recurseTetrahedron(self,vertices,level,size,depth=0):
        self.drawTetrahedron(vertices,depth)
        if level != 0:
            for face in Tetrahedron.faceList:
                for i in range(4):
                    if i not in face:
                        missingVertex = copy.deepcopy(vertices[i])
                reVerts = copy.deepcopy([vertices[face[0]],vertices[face[1]],vertices[face[2]]])
                centerPt = avgPts(reVerts)
                normVerts = copy.copy(reVerts)
                a = copy.copy(normVerts[2])
                a.sub(normVerts[1])
                b = copy.copy(normVerts[2])
                b.sub(normVerts[0])
                c = copy.copy(normVerts[2])
                c.sub(missingVertex)
                crossProduct = cross(a,b)
                crossProduct.setMag(-size)
                if dot(crossProduct, c) < 0:
                    crossProduct.mult(-1)
                centerPt.add(crossProduct)
                newVertices = midPts(reVerts) + [centerPt]
                self.recurseTetrahedron(newVertices, level - 1, size/1.5,depth+1)

def avgPts(pts):
    temp = PVector(0, 0, 0)
    for pt in pts:
        temp.add(pt)
    temp.mult(1.0 / float(len(pts)))
    return temp

def midPts(pts):
    avgPts = []
    for i in range(3):
        pair = copy.deepcopy([pt for j, pt in enumerate(pts) if i != j])
        pair[0].add(pair[1])
        pair[0].mult(0.5)
        avgPts.append(pair[0])
    return avgPts

def cross(a, b):
    c = PVector(a.y*b.z - a.z*b.y,
        a.z*b.x - a.x*b.z,
        a.x*b.y - a.y*b.x)
    return c

def dot(a,b):
    return a.x*b.x + a.y*b.y + a.z*b.z   