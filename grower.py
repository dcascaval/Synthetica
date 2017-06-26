from math import *
import random
import copy

class Grower():

    def __init__(self,position,startBranches,r,seed,level=0):
        self.pos = position #PVector
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
            
    def display(self,branches = None,s=2,black=200):
        for branch in branches:
            beginShape(LINES)
            strokeWeight(s+2)
            stroke(map(s+2,0,self.level*2,255,black))
            vertex(branch[0].x,branch[0].y,branch[0].z)
            strokeWeight(s)
            stroke(map(s,0,self.level*2,255,black))
            vertex(branch[1].x,branch[1].y,branch[1].z)
            endShape()
            # line(branch[0].x,branch[0].y,branch[0].z,branch[1].x,branch[1].y,branch[1].z)
            
    def drawCircle(self,uDiv,vDiv,radius):
        stroke(100)
        noFill()
        strokeWeight(2)
        for i in range(uDiv):
            beginShape()
            for j in range(-vDiv,vDiv):
                px = spherical(self.pos,radius,i*pi*2/uDiv,j*pi/(vDiv*2))
                point(px.x, px.y, px.z)
            endShape()
        
    def moveBranches(self,speed):
        dTheta,dPhi = speed,-speed
        newBranches = []
        for branch in self.branches:
            theta,phi = branch[2]+dTheta,branch[3]+dPhi
            newPos = spherical(self.pos,self.radius,theta,phi)
            newBranches.append((self.pos,newPos,theta,phi))
        self.branches = newBranches
        
    
    def recurseBranches(self,level,branches=None,radius=0,depth=0,variation=1):
        if self.level == 0: self.level = level
        if branches == None: branches = self.branches
        self.display(branches,level*2)
        if radius == 0: radius = self.radius*1.1
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