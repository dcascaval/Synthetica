import copy
from random import *

class Resource():
    
    def __init__(self):
        self.num = 1
    
    def addResource(self,item):
        curnum = self.num//4
        if self.type == item:
            self.num += 1
            if self.num//4 > curnum:
                if self.type == "Tetras":
                    self.branchTree(self.num//4)
    
    def removeResource(self):
        self.num -= 1
        if self.num > 0: 
            return False
        else: 
            return True
        
    @staticmethod
    def makeResource(terrainObjects, targX, targZ, item, world):
        if item == "Cubes" or item == "Rock":
            pts = Resource.getRockPts(targX, targZ, terrainObjects, world)
            if len(pts) == 4:
                return Rock(pts,randint(10, 50))
        elif item == "Tetras" or item == "Tree":
            return Tree(Resource.getTreePts(targX, targZ, terrainObjects, world), 
                         randint(10, 40),randint(25, 60), 0)
        elif item == "":
            pass #goal: add flows. 
    
    @staticmethod
    def getTreePts(i, j, terrainObjects, world):
        ptList = []
        ptList.append(PVector((i) * world.scl, terrainObjects[i][j]["y"], (j) * world.scl))
        for k in range(-1, 2):
            for l in range(-1, 2):
                if not (k == l == 0) and (0 < i + k < world.row and 0 < j + l < world.cols):
                    if uniform(0, 1) <= 0.5:
                        ptList.append(
                            PVector((i+k) * world.scl, terrainObjects[i+k][j+l]["y"], (j+l) * world.scl))
        return ptList
    
    @staticmethod
    def getRockPts(i, j, terrainObjects,world):
        ptList = []
        if 0 < i - 1 < i + 1 < world.row and 0 < j - 1 < j + 1 < world.cols:
            ptList.append(PVector((i) * world.scl, terrainObjects[i][j]["y"], (j) * world.scl))
            ptList.append(PVector((i + 1) * world.scl, terrainObjects[i + 1][j]["y"], (j) * world.scl))
            ptList.append(PVector((i + 1) * world.scl, terrainObjects[i + 1][j + 1]["y"], (j + 1) * world.scl))
            ptList.append(PVector((i) * world.scl, terrainObjects[i][j + 1]["y"], (j + 1) * world.scl))
        return ptList
        
class Tree(Resource):
    
    def __init__(self,basePts,ySc,xSc,level):
        Resource.__init__(self)
        self.type = "Tetras" 
        self.basePts = basePts
        self.ySc = ySc
        self.xSc = xSc
        self.lines = []
        self.branchPts = []
        self.makeTree()
        self.branchTree(level)
    
    def getFruit(self):
        self.fruitSize = []
        for pt in self.branchPts:
            self.fruitSize.append(randint(2,5))
    
    def makeTree(self):
        newPt = avgPts(self.basePts)
        maxY,minY = 0,0
        for pt in self.basePts:
            if pt.y > maxY: maxY = pt.y
            if pt.y < minY: minY = pt.y
        # if self.ySc <= abs(maxY-minY): self.ySc = abs(maxY-minY)
        newPt.add(PVector(0,-max([self.ySc,abs(maxY-minY)/2]),0))
        for pt in self.basePts:
            self.lines.append((pt,newPt))
        branchPt = PVector(0,-self.ySc*2,0)
        branchPt.add(newPt)
        self.branchPts.append(branchPt)
        self.lines.append((newPt,branchPt))
        self.trunkLen = len(self.lines) + 1
        
    def display(self,alp):
        colorMode(HSB)
        for i,pr in enumerate(self.lines):
            if i < self.trunkLen:
                strokeWeight(4)
                stroke(20,128,min([170,alp]))
            else: 
                stroke(20,128*self.trunkLen/i,min([170,alp]))
                strokeWeight(constrain(5 - i/self.trunkLen,1,5))
            line(pr[0].x,pr[0].y,pr[0].z,pr[1].x,pr[1].y,pr[1].z)
        for i,pt in enumerate(self.branchPts):
            strokeWeight(2)
            with pushMatrix():
                sphereDetail(0)
                translate(pt.x,pt.y,pt.z)
                rotateY(frameCount/100.0)
                noFill()
                stroke(map(pt.x%100,0,100,0,255),60,alp)
                sphere(self.fruitSize[i])
    
    def branchTree(self,level,depth=0):
        if level > 2: level = 2
        ySc = self.ySc
        xSc = self.xSc
        tempPts = []
        for i in range(len(self.branchPts)):
            for j in range(randint(1,5)):
                newPt = PVector(uniform(-xSc,xSc),-uniform((ySc/2) - depth*ySc/2,(ySc*2) - depth*ySc/2),uniform(-xSc,xSc))
                newPt.add(self.branchPts[i])
                tempPts.append(newPt)
                self.lines.append((self.branchPts[i],newPt))
        self.branchPts = tempPts
        self.getFruit()
        if level > 0:
            self.branchTree(level-1,depth+1)
    
def avgPts(pts):
    result = PVector(0, 0, 0)
    for pt in pts:
        result.add(pt)
    result.mult(1.0 / float(len(pts)))
    return result

class Rock(Resource):
    def __init__(self,pts,sc):
        Resource.__init__(self)
        self.pts = pts
        self.sc = sc
        self.type = "Cubes" 
        self.makeRock()
    
    
    def display(self,alp):
        val = constrain(alp-50,0,205)
        stroke(val)
        strokeWeight(3)
        noFill()
        for i in range(len(self.pts)):
            with beginShape(QUADS):
                vertex(self.pts[i-1].x,self.pts[i-1].y,self.pts[i-1].z)
                vertex(self.newPts[i-1].x,self.newPts[i-1].y,self.newPts[i-1].z)
                vertex(self.newPts[i].x,self.newPts[i].y,self.newPts[i].z)
                vertex(self.pts[i].x,self.pts[i].y,self.pts[i].z)
        with beginShape(QUADS):
            for pt in self.newPts:
                vertex(pt.x,pt.y,pt.z)
            
    
    def makeRock(self): 
        midpt = avgPts(self.pts)
        yTarg = midpt.y - self.sc
        self.newPts = []
        for pt in self.pts:
            self.newPts.append(PVector(pt.x,yTarg,pt.z))