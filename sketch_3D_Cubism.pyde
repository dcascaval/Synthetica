from math import *
from grower import *
from tetrahedron import *
import copy
import random

random.seed(0) #Preferably user-defined.

scl = 32 #25 ## SIZE OF EACH MESH QUAD
tScl = 250 #400 ## POSSIBLE PERLIN AMPLITUDE
row = 100 #100 ## NUMBER OF TERRAIN X CHUNKS
cols = 100 #100 ## NUMBER OF TERRAIN Y CHUNKS
chunk = 12 #BLOCKS PER CREATURE RENDER CHUNK

searchRadius = 100 # radius of "local " analysed to find local maxima (for beacons)
drawRadius = 28 # Radius that you can see. Generally below 30 works ok. 50 is slightly more impressive, but slow. 
maxLength = (((row + cols)/2) * scl)/2  # Prox cap for beacon connection pts.


## INITIAL CAMERA PLACEMENT FXNS. 
camX = scl*row/2 
camY = -tScl
camZ = scl*cols/2
eyeX = camX + 100
eyeY = camY
eyeZ = camZ
theta = 0
yTheta = 0
r = 100


## SPEED OPERATORS (add gravSpeed, lookSpeed, moveSpeed)
speed = 1.0


#Lovely lists of things that are created in setup. 
noiseShift = []
boxList = []
boxSizes = []
linepts = []
terrain = []
linePairs = []
biomeColor = []
biomeList = []
creatureList = []

#Stats 
flyDist = 0

def setup():
    size(1000, 1000, P3D)
    noiseSeed(0)
    noSmooth()
    global noiseShift,biomeList,biomeColor, creatureList
    global scl, boxNum, searchRadius, maxLength
    noises = [[random.uniform(-scl/4,scl/4) for i in range(row+1)] for j in range (cols+1)]
    #noises = [[0 for i in range(row+1)] for j in range (cols+1)]
    biomeColor = [[(0,0) for i in range(row+1)] for j in range (cols+1)]
    noiseShift = noises
    global linepts, terrain
    terrain = [[map(noise((float(i)/10),float(j)/10),0,1,-tScl,tScl) for i in range(row+1)] for j in range (cols+1)]
    #calcLines(cols, row, searchRadius, terrain, maxLength)
    makeBiomes(biomeList,20)
    creatureList = [[[None] for i in range((row/chunk) + 1)] for j in range((cols/chunk)+1)]
    #print len(creatureList), len(creatureList[0])
    placeCreatures(20)
    #defining this allows the clipping planes of the perspective viewport to be explicitly defined. 
    cameraZ = (height/2.0) / tan(PI*60.0/360.0)
    perspective(PI/3.0, width/height, cameraZ/100.0, cameraZ*10)
    
    
#INTENSIVE LOOP, can take a few seconds to boot game
#Could probably be optimised... dicts maybe?

def calcLines(cols, row, searchRadius, terrain, maxLength):
    global linepts
    for i in range(1,cols-1):
        for j in range(1,row-1):
            if PVector(i*scl+noiseShift[i][j],terrain[i][j],(j*scl)+noiseShift[i][j]) in linepts: continue
            count = 0 
            for k in range(searchRadius):
                for l in range(searchRadius):
                    if i-k<0 or j-l<0 or i+k > cols or j+l>row: count += 0
                    elif terrain[i][j] > terrain[i-k][j-l]: count +=1; break
                    elif terrain[i][j] > terrain[i-k][j+l]: count +=1; break
                    elif terrain[i][j] > terrain[i+k][j-l]: count +=1; break
                    elif terrain[i][j] > terrain[i+k][j+l]: count +=1; break
                if count != 0: break
            if count == 0:
                linepts.append(PVector(i*scl+noiseShift[i][j],terrain[i][j],(j*scl)+noiseShift[i][j]))

    distPairs = []
    
    for i in range(len(linepts)):
        for j in range(len(linepts)):
            if i != j:
                dist = (distance(linepts[i],linepts[j]))
                if dist < maxLength:
                    distPairs.append([i,j])
                                     
    global linePairs
    for i in range(len(distPairs)):
        if [distPairs[i][1],distPairs[i][0]] not in linePairs:
            linePairs.append(distPairs[i])


#TODO - Poisson Disc Sampling
def makeBiomes(biomeList,numBiomes):
    global row, cols, biomeColor
    for i in range(numBiomes):
        ptX = random.randint(0,row)
        ptZ = random.randint(0,cols)
        biomeLoc = PVector(ptX, 0, ptZ)
        biomeVal = random.choice(['desert','mountain','jungle','plains','ocean'])
        biomeList.append((biomeLoc,biomeVal))
    
    for i in range(row+1):
        for j in range(cols+1):
            minDist,closeBiome = None,None
            for k,biome in enumerate(biomeList):
                d = distance(PVector(i,0,j),biome[0])
                if minDist == None: 
                    minDist = d
                    closeBiome = k
                elif d < minDist: 
                    minDist = d
                    closeBiome = k
            biomeColor[i][j] = getBiomeColor(biomeList[closeBiome][1])

#TODO - Add next-closest neighbor color-scaling

def getBiomeColor(biomeVal):
    if biomeVal == 'desert':
        return(50,128)
    elif biomeVal == 'mountain':
        return(0,0)
    elif biomeVal == 'jungle':
        return(140,152)
    elif biomeVal == 'plains':
        return(95,152)
    elif biomeVal == 'ocean':
        return(210,128)


def placeCreatures(numCreatures):
    global creatureList, terrain, scl
    for i in range(numCreatures):
        random.seed(i)
        creatureType = random.choice(['Grower','Tetra'])
        ptX = random.randint(0,row)
        ptZ = random.randint(0,cols)
        ptY = terrain[ptX][ptZ]
        # print ptX, ptY, ptZ
        if creatureType == 'Grower':
            c = Grower(PVector(ptX*scl,ptY-20,ptZ*scl),14,20,'seed')
        elif creatureType == 'Tetra':
            c = Tetrahedron(PVector(ptX*scl,ptY-20,ptZ*scl),20)
        # print ptX/chunk, ptZ/chunk
        # print len(creatureList), len(creatureList[0])
        if creatureList[ptX/chunk][ptZ/chunk] == [None]:
            creatureList[ptX/chunk][ptZ/chunk] = [c]
        else: creatureList[ptX/chunk][ptZ/chunk].append(c)
    for i in range(len(creatureList)):
        for j in range(len(creatureList)):
            print len(creatureList[i][j])
            # for creature in creatureList[i][j]:
            #     if creature != None:
            #         print creature.pos

            
# t = Tetrahedron(PVector(0, 0, 0), 100)

           
                

#GENERAL PURPOSE DISTANCE FXN        
def distance(a,b):
    return((b.x - a.x)**2 + (b.y - a.y)**2 + (b.z-a.z)**2)**0.5


#### HUD STUFF ### 
def screenText(camX,camZ,camY,head,yTheta):
    global flyDist
    stroke(255)
    fill(255)
    hint(DISABLE_DEPTH_TEST)
    lights()
    textMode(MODEL)
    textAlign(LEFT)
    text(frameRate, 10, 10 + textAscent())
    text("X: " + ("+" if head.x > 0 else "-"), 10,height-45 + textAscent())
    text("Z: " + ("+" if head.z > 0 else "-"), 10,height-30 + textAscent())
    textAlign(RIGHT)
    text(speed, width-10, 10 + textAscent())
    text(str(int((-yTheta)*180/pi)) + chr(176), width-10, height-30 + textAscent())
    textAlign(CENTER)
    text("( " + str(int(camX)) + " , " + str(int(camZ)) + " , " + str(int(-camY)) +" )" , width/2, 10 + textAscent())
    text("Flown: " + str(int(flyDist)), width/2, height-30 + textAscent())
    
    strokeCap(SQUARE)
    line(width/2 - 10,height/2,width/2 +10,height/2)
    line(width/2,height/2 - 10, width/2, height/2 + 10)
    strokeCap(ROUND)
    hint(ENABLE_DEPTH_TEST)

#######


def makeLines(linepts,thickness,radius,linePairs):
    global camX, camY, camZ, maxLength
    pos = PVector(camX,camY,camZ)
    sphereDetail(0)
    for item in linepts:
        bright = map(distance(pos,item),0,drawRadius*scl*2,255,0)
        strokeWeight(0.25)
        stroke(bright)
        emissive(100)
        fill((frameCount/(10.0))%255,180,bright)
        pushMatrix()
        translate(item.x,item.y-radius,item.z)
        rotateY(frameCount/(200.0))
        sphere(radius-5)
        popMatrix()
    
    strokeWeight(1)
    noFill()
    
    for item in linePairs:
        val = min([distance(pos,linepts[item[0]]),distance(pos,linepts[item[1]])])
        pairDist = distance(linepts[item[0]],linepts[item[1]])
        hu = map(pairDist,maxLength/4,maxLength,0,128)
        stroke(hu,constrain(map(val,0,drawRadius*scl,255,100),50,255),map(val,0,maxLength/2,255,0))
        line(linepts[item[0]].x,linepts[item[0]].y-radius,linepts[item[0]].z,
             linepts[item[1]].x,linepts[item[1]].y-radius,linepts[item[1]].z)
                
    strokeWeight(1)
    



#### ALPHA (COLORFADE) FUNCTION
def getAlp(xLoc,zLoc,i,j):
    global camX, camZ
    xAlp = (((i*scl)-(camX))/scl)**2
    yAlp = (((j*scl)-(camZ))/scl)**2
    return map((xAlp + yAlp)**0.5, drawRadius-15, drawRadius-5, 150, 0)

head = PVector(0,0,0)

keyDict = {"w":False,"s":False,"d":False,"a":False,"q":False,"e":False," ":False,"x":False,"c":False}
def draw():
    background(0)
    
    global eyeX,eyeY,eyeZ,camX,camY,camZ,theta,r,yTheta,speed,head,flyDist
    
    global scl,tScl,row,cols
    
    global noiseShift
    
    global screenText
    
    global keyDict
    
    #KEYS CONTROL CAMERA TRANSLATION MOVEMENT
    
    if keyDict["w"]:
        camX += head.x
        camY += head.y
        camZ += head.z
        eyeX += head.x
        eyeY += head.y
        eyeZ += head.z
    if keyDict["s"]:
        camX -= head.x
        camY -= head.y
        camZ -= head.z
        eyeX -= head.x
        eyeY -= head.y
        eyeZ -= head.z
    if keyDict["d"]:
        camX -= head.z
        camY += head.y
        camZ += head.x
        eyeX -= head.z
        eyeY += head.y
        eyeZ += head.x
    if keyDict["a"]:
        camX += head.z
        camY += head.y
        camZ -= head.x
        eyeX += head.z
        eyeY += head.y
        eyeZ -= head.x
    if keyDict["q"]:
        camY += 1 * speed
        eyeY += 1 * speed
    if keyDict["e"]:
        camY -= 1 * speed
        eyeY -= 1 * speed
    if keyDict[" "]:
        speed += 0.01
    if not keyDict[" "]:
        if speed > 1:
            speed -= 0.01
    if keyDict["x"]:
        speed = 0
    if speed > 0:
        if keyDict["c"]:
            speed -= 0.1
            
    #modifier
    head = PVector(eyeX-camX, eyeY-camY, eyeZ-camZ)
    head.setMag(1*speed)
    flyDist += 1*speed
            
    #MOUSE CONTROLS CAMERA SHIFT VIEW DIRECTION
    
    if mouseX > 0 and mouseY > 0:
        if mouseX > width/2:
            diff =map(abs(width/2 - mouseX),0,height/2,0,0.01)
            theta += diff 
        elif mouseX < width/2:
            diff = map(abs(width/2 - mouseX),0,height/2,0,0.01)
            theta -= diff
        if mouseY < height/2:
            diff =map(abs(height/2 - mouseY),0,height/2,0,0.01)
            yTheta -= diff
        elif mouseY > height/2:
            diff =map(abs(height/2 - mouseY),0,height/2,0,0.01)
            yTheta += diff
        if camX > 0 and camX < cols * scl and camZ > 0 and camZ < row*scl:
            i = int(floor(camX/scl))
            j = int(floor(camZ/scl))
            yHeight = min([terrain[i][j],terrain[i+1][j],terrain[i+1][j+1],
                           terrain[i+1][j-1],terrain[i][j+1],terrain[i][j-1],
                           terrain[i-1][j+1],terrain[i-1][j],terrain[i-1][j-1]])
            temp = camY
            if camY < yHeight - 11:
                camY += 0.1 * speed*2
                eyeY += (camY - temp)
            elif  camY > yHeight - 10:
                camY -= 0.1 * speed*2
                eyeY += (camY - temp)
        
    ###############################
    
    #CAMSHIFT HAPPENS HERE
    eyeX = camX + (r * cos(theta))
    eyeZ = camZ + (r * sin(theta))
    eyeY = camY + (r * sin(yTheta))    
    camera(camX,camY,camZ,eyeX,eyeY,eyeZ,0,1,0)
    
    ### MAKING TERRAIN ###
    xLoc = int(floor(camX/scl))
    zLoc = int(floor(camZ/scl))

    colorMode(HSB)
    
    count = 1
    strokeWeight(2)
    #noStroke()
    noFill()
    # fill(0)
    #first round of the iteration is determining the lookup in terrain from the base location. count is used for a sin interp to make a circular region.
    for i in range(xLoc - drawRadius, xLoc+drawRadius):
        for j in range(int(zLoc - (drawRadius * sin(pi*count/(drawRadius*2)))), int(zLoc + (drawRadius*sin(pi*count/(drawRadius*2))))):
            if i > 0 and i < row and j > 0 and j < cols:
                #if the lookup is valid, the quadShape is drawn with the second round of iteration
                beginShape(QUADS)
                for k in xrange(0,2):
                    lrange = xrange(0,2) if k == 0 else xrange(1,-1,-1)
                    for l in lrange:
                        #all of the coloring done before the vertex is fetched
                        alp = getAlp(xLoc,zLoc,i+l,j+k)
                        # if alp > 20: 
                        #     stroke(0,0,alp*2)
                        # else: 
                        # noStroke()
                        stroke(biomeColor[i+l][j+k][0],biomeColor[i+l][j+k][1],alp)
                        vertex((i+l)*scl+noiseShift[i+l][j+k],terrain[i+l][j+k],((j+k)*scl)+noiseShift[i+l][j+k])
                endShape()
        count +=1
        

    #makeLines(linepts,2,30,linePairs)
    global creatureList
    
    cX,cZ = xLoc/chunk, zLoc/chunk
    # print creatureList
    for i in range(-2,3):
        for j in range(-2,3):
            if cX + i < 0 or cZ + j < 0 or cX + i >= len(creatureList) or cZ+j > len(creatureList): break
            for c in creatureList[cX+i][cZ+j]:
                if c == None: break
                if distance(c.pos, PVector(camX,0,camZ)) < drawRadius*scl:
                    if c.__class__.__name__ == 'Grower':
                        print "madeGrower", c.pos
                        c.moveBranches(0.005)
                        c.recurseBranches(1)
                    elif c.__class__.__name__ == 'Tetrahedron':
                        print 'madeTetra', c.pos
                        with pushMatrix():
                            translate(c.pos.x,c.pos.y,c.pos.z)
                            rotateY(frameCount/200.0)
                            c.recurseTetrahedron(c.vertices,2,c.size)
    

    # for c in creatureList:
    #     if c.__class__.__name__ == 'Grower':
    #         c.moveBranches(0.005)
    #         c.recurseBranches(1)
    #     # elif c.__class__.__name__ == 'Tetrahedron':
        #     print 'madeTetra'
        #     with pushMatrix():
        #         rotateY(frameCount/200.0)
        #         c.recurseTetrahedron(c.vertices,2,c.size)
            
    
    camera()
    strokeWeight(1)
    screenText(camX,camZ,camY,head,yTheta)

#key controls

def keyPressed():
    global keyDict
    global eyeX,eyeY,eyeZ,camX,camY,camZ,theta,r,yTheta,speed,head,flyDist

    if key in keyDict:
        keyDict[key] = not keyDict[key]
            
            
def keyReleased():
    if key in keyDict:
        keyDict[key] = not keyDict[key]
    