#creates randomly placed, colored, and oriented boxes all around everywhere


#boxList = [[random.randint(0,row*scl),random.randint(200,1000),random.randint(0,cols*scl)] for i in range(boxNum)]

def makeBoxes(boxList,terrain,scl,xLoc,zLoc):
    global drawRadius
    for boxThing in boxList:
        xC = floor(boxThing[0]/scl)
        zC = floor(boxThing[2]/scl)
        if abs(xC - xLoc) < drawRadius*2 and abs(zC-zLoc) < drawRadius*2:
            pushMatrix()
            translate(boxThing[0],boxThing[1],boxThing[2])
            if boxThing[1] < terrain[xC][zC]:
                stroke(0)
                fillThing = map(boxThing[1],250,-250,0,255)
                fill(0,0,fillThing,255-fillThing)
                rotateY(boxThing[1]/360 + boxThing[2]/360)
                #rotateZ(boxThing[0]/360 + boxThing[1]/360)
                box(boxThing[0]%100 + 10,boxThing[1]%100 + 10,boxThing[2]%100 + 10)
            popMatrix()


#computationally expensive. not really worth it
def makeStars(boxList,xLoc,zLoc):
    global drawRadius
    for boxThing in boxList:
        xC = floor(boxThing[0]/scl)
        zC = floor(boxThing[2]/scl)
        if abs(xC - xLoc) < drawRadius*2 and abs(zC-zLoc) < drawRadius*2:
            aDist = abs(xC - xLoc) + abs(zC - zLoc)
            stroke(map(aDist,0,drawRadius*4,255,0))
            strokeWeight(map(aDist,0,drawRadius*4,20,0))
            fill(map(aDist,0,drawRadius*4,255,0))
            point(boxThing[0],boxThing[1],boxThing[2])
            
    #makeBoxes(boxList,terrain,scl,xLoc,zLoc)
    #makeStars(boxList,xLoc,zLoc)
    
#old color fx
colors = map(terrain[i+l][j+k],-tScl/2,tScl/2,255,0)
sat = map(colors,0,255,150,0)