import copy
import random

#defines the player's resources and attributes

class Player():
    
    def __init__(self,world):
        self.moveSpeed = 2.0
        self.lookSpeed = 2.0
        self.gravity = 2.0
        self.mode = "basic" #playerMode, not gameMode
        self.initResources()
        self.inventory() #make the inventory
        self.active = 0 #active inventory item
        self.rMap = ["Tetras","Cubes","Spheres","Fluid","Planes","Light"]
        self.col = (0, 0, 200)
        self.initCamera(world)
        self.loadImages()
        self.keyDict = {"w": False, "s": False, "d": False, "a": False,
           "q": False, "e": False, " ": False, "x": False, "c": False}
    
    def initCamera(self,world):
        self.camX = world.scl * world.row / 2
        self.camY = -world.tScl
        self.camZ = world.scl * world.cols / 2
        self.eyeX = self.camX + 100
        self.eyeY = self.camY
        self.eyeZ = self.camZ
        self.theta = 0
        self.yTheta = 0
        self.r = 100
        self.view = False
        self.targX = 0
        self.targZ = 0
    
    
    
    def loadImages(self):
        self.tutorial = loadImage("tutorial.png")
        self.tree = loadImage("treeicon.png")
        self.cube = loadImage("cubeicon.png")
        self.spher = loadImage("sphereicon.png")
        self.flow = loadImage("flowicon.png")
        self.plane = loadImage("planeicon.png")
        self.light = loadImage("lighticon.png")
        self.images = (self.tree,self.cube,self.spher,self.flow,self.plane,self.light)
    
    def initResources(self):
        self.rd = {"Tetras":0,"Cubes":0,"Spheres":0,"Fluid":0,"Planes":0,"Light":0}
    
    def inventory(self):
        rd = self.rd
        self.resources = [rd["Tetras"],rd["Cubes"],rd["Spheres"],rd["Fluid"],rd["Planes"],rd["Light"]]
        modeVal = self.getModeVal()
        if modeVal == None: self.mode,self.col = "basic", (0, 0, 200)
        else:
            if modeVal == "Tetras": self.mode,self.col = "growth",(0,200,200)
            elif modeVal == "Cubes": self.mode,self.col = "cubic", (40,200,200)
            elif modeVal == "Spheres": self.mode,self.col = "spherical", (80,200,200)
            elif modeVal == "Fluid": self.mode,self.col = "fluidic", (140,200,200)
            elif modeVal == "Planes": self.mode,self.col = "planar", (160,200,200)
            elif modeVal == "Light": self.mode,self.col = "luminous", (200,200,200)
    
    def getModeVal(self):
        threshold = 9
        modeVal = None
        for i,val in enumerate(self.resources):
            if val > threshold:
                modeVal = self.rMap[i]
                threshold = val
        return modeVal
                

    #gets all the items in the inventory and draws the HUD
    def drawInventory(self):
        rects = len(self.resources)
        stroke(self.col[0],self.col[1],self.col[2])
        strokeWeight(2)
        line(width/2 - rects*20,height - 70,width/2 + rects*20,height - 70)
        line(width/2 - rects*20,height - 30,width/2 + rects*20,height - 30)
        for i in range(rects + 1):
            if i < rects:
                image(self.images[i],width/2 - (rects*20) + i*40,height - 70,40,40)
            line(width/2 - (rects*20) + i*40,height - 70, width/2 - (rects*20) + i*40, height-30)
        for i in range(rects):
            text(str(self.resources[i]),width/2 - (rects*20) + i*40 + 20, height-15 + textDescent())
        stroke(255)
        strokeWeight(3)
        noFill()
        rect(width/2 - rects*20 + self.active*40,height-70,40,40) 

    def dropItem(self): #drops
        if self.rd[self.rMap[self.active]] > 0:
            self.rd[self.rMap[self.active]] -= 1
            self.inventory() 
            return True
        else:
            return False
        
    
    def collectItem(self, item):#catches from surroundings
        if item  in self.rd:
            self.rd[item] += 1
        self.inventory()