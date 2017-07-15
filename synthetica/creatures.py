from math import *
import random
from resources import Resource
import copy


#This is where most of the fun recursive drawing stuff happens! 

class Creature():
    
    def __init__(self):
        self.num = 1
        self.vel = PVector(0,0,0)
        self.attract = PVector(0,0,0)
        self.vision = 3
        self.cRange = [0] + [b for a in ((x,-x) for x in range(1, self.vision + 1)) for b in a]
        self.edgeRad = 4
    
    def addResource(self,item):
        if self.type == item:
            self.num += 1
            return True
        else: return False
            
    def removeResource(self):
        self.num -= 1
        if self.num > 0: 
            return False
        else: 
            return True
    
    #Creature Generator
    @staticmethod 
    def makeCreature(creatureType,world,ptX,ptY,ptZ):
        if creatureType == 'Grower' or creatureType == 'Tetras':
            return Grower(PVector(ptX * world.scl, ptY - 20, ptZ * world.scl), 14, random.randint(10,30), random.randint(0,1000))
        elif creatureType == 'Tetra' or creatureType == 'Cubes':
            return Tetrahedron(PVector(ptX * world.scl, ptY - 20, ptZ * world.scl), random.randint(30,50))
        elif creatureType == 'Bubble' or creatureType == 'Spheres':
            return Bubbles(PVector(ptX * world.scl, ptY - 20, ptZ * world.scl), random.randint(10,30))
        elif creatureType == 'Planar' or creatureType == 'Planes':
            return Planar(PVector(ptX * world.scl, ptY - 20, ptZ * world.scl), random.randint(3,8))
        elif creatureType == 'Light':
            return Light(PVector(ptX * world.scl, ptY - 20, ptZ * world.scl))
        else: return None


    #Creature 'AI' part 1 - "seeing" 
    def getNear(self,terrainObjects,i,j,scl,dx=0,dz=0):

        for k in self.cRange:
            for l in self.cRange:
                try: resource = terrainObjects[i+k][j+l]["rList"]
                except: break
                try: cList = terrainObjects[i+k][j+l]["cList"]
                except: break
                
                if not (k == l == 0): #don't be attracted to yourself!
                    if len(cList) != 0 and cList != [None]:
                        if cList[0].num != self.num:
                            dx = (i+k+0.5)*scl - self.pos.x
                            dz = (j+l+0.5)*scl - self.pos.z
                            self.attract = PVector(dx,0,dz)
                            return True
                        
                if resource != None and resource.type == self.type:
                    dx = (i+k+0.5)*scl - self.pos.x
                    dz = (j+l+0.5)*scl - self.pos.z
                    if k == l == 0: 
                        self.attract = PVector(0,0,0)
                        if terrainObjects[i][j]["rList"] != None:
                            resource = terrainObjects[i][j]["rList"]
                            for c in terrainObjects[i][j]["cList"]:
                                if c.addResource(resource.type):
                                        if resource.removeResource():
                                            terrainObjects[i][j]["rList"] = None
                    else: self.attract = PVector(dx,0,dz)
                    return True
                    
        return False
    
    
    #Creature 'AI' part 2 - "moving"
    def move(self,terrainObjects,i,j,quick,scl,world):
        row, cols = world.row, world.cols
        dx,dz = 0,0 
        
        if self.getNear(terrainObjects,i,j,scl):
            self.vel = self.attract 
            #poetically enough, their hunger for resources may lead to their doom.
        
        else: 
            if (self.edgeRad>i) or (i>row-self.edgeRad) or (self.edgeRad>j) or (j>cols-self.edgeRad):
                dx = constrain((row/2)*scl - self.pos.x,-3,3)
                dz = constrain((cols/2)*scl - self.pos.z,-3,3)
            dx += map(noise(i/10.0 + frameCount/200.0),0,1,-quick,quick)
            dz += map(noise(j/10.0 + frameCount/200.0),0,1,-quick,quick)
            self.vel = PVector(self.vel.x + dx, 0, self.vel.z + dz)
        

        self.vel.setMag(1)
   
        k,l = 0,0
        
        yHeight = float(min([terrainObjects[i+m][j+n]["y"] for m in range(-1,2) for n in range(-1,2)]))
        
        if self.pos.y != yHeight - 30.0:
            dy = constrain((yHeight - 30.0) - self.pos.y,-0.5,0.5) #smooth shifting btwn avg heights
        else:
            dy = 0.0
        
        if int((self.pos.x) / scl) != i: #check if they've moved boxes
            k = int(self.pos.x / scl) - i
        elif int((self.pos.z) / scl) != j:
            l = int(self.pos.z / scl) - j
        
        if not (k == l == 0): #move the boxes
            if terrainObjects[i+k][j+l]["cList"] == [None]:
                terrainObjects[i+k][j+l]["cList"] = [self]
            else:
                terrainObjects[i+k][j+l]["cList"].append(self)
            terrainObjects[i][j]["cList"].remove(self)
            
        self.pos = PVector(self.pos.x + self.vel.x, self.pos.y + dy, self.pos.z + self.vel.z)
        
    
    #Creature 'AI'/Interaction Part 3 - "Merging/Dying"
    @staticmethod
    def checkMerge(terrainObjects, i, j, world): #now includes explosions!
        cList = terrainObjects[i][j]["cList"]
        oDict = dict()
        
        for c in cList:
            name = c.__class__.__name__
            if name in oDict:
                oDict[name].append(c)
            else:
                oDict[name] = [c]
                
        cList = []

        for name in oDict:
            c = oDict[name][0]
            if len(oDict[name]) > 1:
                for dead in oDict[name][1:]:
                    c.num += dead.num
            cList.append(c)
            
        if len(cList) > 1:
            maxNum = 0
            bestCreature = None
            for c in cList:
                if c.num > maxNum:
                    maxNum = c.num
                    bestCreature = c
            cList.remove(bestCreature)
            for dead in cList:
                if dead.type == "Tetras" or dead.type == "Cubes":
                    Creature.spreadRemains(dead,terrainObjects,i,j,world)
                    print dead.type, "was desynthesized."
                else:
                    pass
                    # bestCreature.num += dead.num
                    # print dead.type, "was assimilated into", bestCreature.type,bestCreature.num
            cList = [bestCreature]
            
        return cList
    
    @staticmethod
    def spreadRemains(dead,terrainObjects,i,j,world):
        
        while dead.num > 0:
            dead.removeResource()
            k = random.randint(-2,3)
            l = random.randint(-2,3)
            if terrainObjects[i+k][j+l]["rList"] != None:
                terrainObjects[i+k][j+l]["rList"].addResource(dead.type)
            else:
                terrainObjects[i+k][j+l]["rList"] = Resource.makeResource(terrainObjects,i+k,j+l,dead.type,world)
            

#lots of fun branchy things via close-by randomly selected spherical coordinates                         
class Grower(Creature):

    def __init__(self,position,startBranches,r,seed,level=0):
        Creature.__init__(self)
        self.pos = position
        self.type = "Tetras"
        self.branches = []
        self.radius = r
        self.seed = seed
        self.level = level
        random.seed(seed)
        for i in range(startBranches):
            theta = random.uniform(0,2*pi)
            phi = random.uniform(-pi/2,pi/2)
            newPos = spherical(self.pos,r,theta,phi)
            self.branches.append((self.pos,newPos,theta,phi))
            
    def display(self,branches=None,s=2,black=50):
            
        for branch in branches:
            with beginShape(LINES):
                strokeWeight(s+3)
                hu = map(s+2,0,(1 + (self.num**0.5)//3),80,60)
                stroke(hu,120,map(s+2,0,(1 + self.num//4),255,black))
                vertex(branch[0].x,branch[0].y,branch[0].z)
                strokeWeight(s+1)
                hu = map(s,0,(1 + (self.num**0.5)//3),80,60)
                stroke(hu,120,map(s,0,(1 + self.num//4),255,black))
                vertex(branch[1].x,branch[1].y,branch[1].z)
        
    def moveBranches(self,speed):
        dTheta,dPhi = speed,-speed
        newBranches = []
        for branch in self.branches:
            theta,phi = branch[2]+dTheta,branch[3]+dPhi
            newPos = spherical(self.pos,self.radius,theta,phi)
            newBranches.append((self.pos,newPos,theta,phi))
        self.branches = newBranches
    
    def recurseBranches(self,level=None,branches=None,radius=0,depth=0,variation=1):
        if level == None: level = constrain((self.num**0.5)//3,0,5)
        if branches == None: branches = self.branches
        self.display(branches,level)
        if radius == 0: radius = self.radius*2
        if level > 0:
            newBranches = []
            for j,branch in enumerate(branches):
                for i in range(2):
                    random.seed("%s%s"% (self.seed,i*(depth+1)*j))
                    dTheta = random.uniform(-variation,variation)
                    dPhi = random.uniform(-variation,variation)
                    theta,phi = branch[2]+dTheta,branch[3]+dPhi
                    newPos = spherical(self.pos,radius*1.1,theta,phi)
                    newBranches.append((branch[1],newPos,theta,phi))
            self.recurseBranches(level-1,newBranches,radius*1.5,depth+1)
                
def spherical(pos,r,theta,phi):
    x = pos.x + r*sin(theta)*cos(phi)
    y = pos.y + r*sin(theta)*sin(phi)
    z = pos.z + r*cos(theta)
    return PVector(x,y,z) 

#Fractal tetrahedron generated of each face of previous tetrahedron.
class Tetrahedron(Creature):

    faceList = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    vertPairs = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]

    def __init__(self, position, size):
        Creature.__init__(self)
        self.pos = position
        self.size = size
        self.type = "Cubes"
        pt1 = PVector(-0.288, 0.0, 0.5)
        pt2 = PVector(-0.288, 0.0, -0.5)
        pt3 = PVector(0.576, 0.0, 0.0)
        pt4 = PVector(0.0, 0.816, 0.0)
        self.vertices = [pt1, pt2, pt3, pt4]
        for pt in self.vertices:
            pt.mult(self.size)
        
    def drawTetrahedron(self,vertices,depth = 0):
        for face in Tetrahedron.faceList:
            beginShape(TRIANGLE)
            for i in range(3):
                noFill()
                hu = map(depth,0,3,0,50)
                sat = map(depth,3,0,0,255)
                colorMode(HSB)
                strokeWeight(2)
                stroke(hu,sat,map(i,0,2,0,255))
                vertex(vertices[face[i]].x, vertices[face[i]].y, vertices[face[i]].z)
            endShape()

    
    def recurseTetrahedron(self,vertices,size,level = None,depth=0):
        if level == None: level = constrain((self.num**0.5)//3,0,1)
        self.drawTetrahedron(vertices,depth)
        if level > 0:
            for i,face in enumerate(Tetrahedron.faceList):
                missingVertex = copy.deepcopy(vertices[i-3])
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

#Sphere that has other spheres orbiting it. Ideally those spheres will have spheres orbiting them,
#once the logic changes to accomodate. 
class Bubbles(Creature):

    def __init__(self, pos, sc):
        Creature.__init__(self)
        self.pos = pos
        self.sc = sc
        self.type = "Spheres"
        self.posList = [(PVector(0,0,0),)]
        self.scList = [self.sc]
        self.rList = [0]
        self.dList = [1.5]
        self.outerList = [self.pos]
        self.level = 0
        self.makeSpheres(0)

    def makeSpheres(self, level=0, depth=0):
        if level > 0:
            tempPts = []
            for pt in self.outerList:
                for i in range(random.randint(2, 10)):
                    theta = random.uniform(0, 2 * PI)
                    phi = random.uniform(-PI / 2, PI / 2)
                    r = (self.sc / (depth + 1) ** 2)
                    newPos = spherical(pt, r, theta, phi)
                    self.posList.append((newPos, theta, phi, pt))
                    self.rList.append(r)
                    self.dList.append(0.5 * (1+level))
                    self.scList.append(self.sc / (depth + 2) ** 2)
                    tempPts.append(newPos)
            self.outerList = tempPts
            self.makeSpheres(level - 1, depth + 1)


    def display(self):
        noFill()
        
        for i in range(len(self.posList)):
            self.posList[i][0].add(self.pos)
            strokeWeight(self.dList[i])
            hu = map(i,0,len(self.posList),130,170)
            stroke(hu,128,190)
            with pushMatrix():
                if i!= 0:
                    translate(self.posList[i][0].x, self.posList[i][0].y, self.posList[i][0].z)
                sphereDetail(0)
                rotateY(frameCount / (400.0 * self.dList[i]))
                ellipse(0, 0, self.scList[i] * 1.5, self.scList[i] * 1.5)
                rotateY(PI / 2)
                ellipse(0, 0, self.scList[i] * 1.5, self.scList[i] * 1.5)
                rotateX(PI / 2)
                rotateX(frameCount / (300.0 * self.dList[i]))
                ellipse(0, 0, self.scList[i] * 1.5, self.scList[i] * 1.5)
                rotateY(PI / 2)
                rotateX(PI / 2)
                rotateY(frameCount / (200.0 * self.dList[i]))
                ellipse(0, 0, self.scList[i], self.scList[i])
                rotateX(PI / 2)
                ellipse(0, 0, self.scList[i], self.scList[i])
                rotateX(PI / 2)
                rotateX(frameCount / (100.0 * self.dList[i]))
                ellipse(0, 0, self.scList[i] / 2, self.scList[i] / 2)
                rotateY(PI / 2)
                ellipse(0, 0, self.scList[i] / 2, self.scList[i] / 2)
                sphere(self.scList[i] / 4)
                rotateX(PI / 2)
                ellipse(0, 0, self.scList[i] / 2, self.scList[i] / 2)

#https://en.wikipedia.org/wiki/Piet_Mondrian
class Planar(Creature):
    
    def __init__(self, pos, sc):
        Creature.__init__(self)
        self.pos = pos
        self.sc = sc
        self.level = self.num
        self.type = "Planes"
        self.xNum = random.randint(1,self.num)
        self.yNum = random.randint(1,self.num)
        self.zNum = random.randint(1,self.num)
        self.rectList = []
        self.makeRectangles()
    
    def makeRectangles(self):
        for i in range(self.xNum):
            p1 = PVector(random.randint(0,self.sc),0,random.randint(0,self.sc))
            p2 = PVector(self.sc,0,self.sc)
            p3 = random.randint(0,255)
            self.rectList.append((p1,p2,p3))
        for j in range(self.yNum):
            p1 = PVector(0,random.randint(0,self.sc),random.randint(0,self.sc))
            p2 = PVector(0,self.sc,self.sc)
            p3 = random.randint(0,200)
            self.rectList.append((p1,p2,p3))
        for k in range(self.zNum):
            p1 = PVector(random.randint(0,self.sc),random.randint(0,self.sc),0)
            p2 = PVector(self.sc,self.sc,0)
            p3 = random.randint(0,150)
            self.rectList.append((p1,p2,p3))
    
    def reNumber(self):
        self.xNum = random.randint(1,1+self.num//4)
        self.yNum = random.randint(1,1+self.num//4)
        self.zNum = random.randint(1,1+self.num//4)
        self.level = self.num//4
        self.rectList = []
        self.makeRectangles()
        
    def drawCorner(self,i,pair):
        stroke(255/(i+1))
        hu = map(self.xNum,0,self.num,0,255)
        sat = map(self.yNum,0,self.num,0,128)
        brite = map(self.zNum,0,self.num,0,255)
        fill(hu,sat,brite,(noise(i/100.0 + frameCount/200.0))*self.sc*12)
        with pushMatrix():
            translate(noise(i/100.0 + frameCount/200.0)*self.sc,0,0)
            rect(pair[0].x, pair[0].z, pair[1].x, pair[1].z)
            rotateX(PI/2)
            translate(0,noise(i/100.0 + frameCount/200.0)*self.sc,0)
            rect(pair[0].x, pair[0].z, pair[1].x, pair[1].z)
            rotateY(PI/2)
            translate(0,0,noise(i/100.0 + frameCount/200.0)*self.sc)
            rect(pair[0].x, pair[0].z, pair[1].x, pair[1].z)
            rotateZ(PI/2)
            rect(pair[0].x, pair[0].y, pair[1].x, pair[1].y)
    
    def display(self):
        noFill()
        stroke(255)
        strokeWeight(2)
        for i,pair in enumerate(self.rectList):
            with pushMatrix():
                with pushMatrix():
                    self.drawCorner(i,pair)
                    rotateY(PI/2)
                    translate(0,1,0)
                    self.drawCorner(i,pair)
                    rotateZ(PI/2)
                    translate(0,0,1)
                    self.drawCorner(i,pair)
                rotateX(PI/2)
                translate(1,1,1)
                with pushMatrix():
                    self.drawCorner(i,pair)
                    rotateZ(PI/2)
                    translate(0,0,1)
                    self.drawCorner(i,pair)
                    rotateY(PI/2)
                    translate(0,1,0)
                    self.drawCorner(i,pair)

class Light(Creature):
    # This creature is a visualisation of the Burke-Shaw strange attractor. Documents 
    # can be found here: http://www.atomosyd.net/spip.php?article33
    # The visualisation method
    #     -using multiple particles w/ different parameters
    #     -displaying limited-length particle "streaks" w/ varying stroke
    # is original code.

    def __init__(self,pos):
        Creature.__init__(self)
        self.num = random.randint(1,5)
        self.level = self.num
        self.pos = pos
        self.type = "Light"
        self.a = 10.0
        self.b = 4.272
        self.pts = []
        self.pScl = self.num * 3
        self.dt = 0.01
        self.trails = 200
        self.initLists()

    def initLists(self):
        self.xList = [float(i) / 100 for i in range(self.num)]
        self.yList = [0 for i in range(self.num)]
        self.zList = [0 for i in range(self.num)]
        self.level = self.num
        self.pScl = self.num * 3

    def run(self):
        self.pList = []
        xList, yList, zList = self.xList, self.yList, self.zList
        for i in range(self.num):
            dx = (-self.a * (xList[i] + yList[i])) * self.dt
            dy = (-yList[i] - (self.a * xList[i] * zList[i])) * self.dt
            dz = (self.a * xList[i] * yList[i] + self.b) * self.dt
            
            self.xList[i] += dx
            self.yList[i] += dy
            self.zList[i] += dz
            
            self.pList.append(PVector(xList[i] * self.pScl, yList[i] * self.pScl, zList[i] * self.pScl))
        self.pts.append(self.pList)
        if len(self.pts) > self.trails:
            self.pts = self.pts[len(self.pts)-self.trails:]
        flipPts = zip(*self.pts[::-1])

        for p in flipPts:
            noFill()
            with beginShape():
                p = p[::-1]
                for i in range(len(p)):
                    strokeWeight(2)
                    stroke(255 * i/ self.trails)
                    if p[i].x != 0.0 and p[i].y != 0.0 and p[i].z != 0.0:
                        curveVertex(p[i].x, p[i].y, p[i].z)

def avgPts(pts):
    result = PVector(0, 0, 0)
    for pt in pts:
        result.add(pt)
    result.mult(1.0 / float(len(pts)))
    return result

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