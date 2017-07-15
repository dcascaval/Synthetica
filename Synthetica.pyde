####################################
# Name: Dan Cascaval
# CMU 15-112 Term Project | June 2017
# Built in Processing 3.3.4, requires Java or Processing
# All code original unless otherwise stated.
####################################

from math import *
from resources import *
from creatures import *
from player import *
from world import *
import copy
import random

#game window
width = 1400
height = 1000

#default world-gen options
optsList = [1,1,1,1,1,0]

random.seed(0)


##
# Processing works based on setup function that is run automatically upon
# the start of the program. I use it to define some base parameters and load things
# but otherwise, having the world be player configurable requires that most of it be
# done in the various drawn menus.

def setup():
    size(width, height, P3D)  # main size
    noSmooth()
    #globals are used for overall and pre-game-initialisation varaibles.
    global gameMode,tutorial,prevMode
    gameMode = "start"
    tutorial = loadImage("tutorial.png")
    # defining this allows the clipping planes of the perspective viewport to be explicitly defined.
    fov = PI / 3.0
    cameraZ = (height / 2.0) / tan(fov / 2.0)
    perspective(fov, width * 1.0 / height, cameraZ / 100.0, cameraZ * 10)

##World creation function
def makeWorld(optsList):
    global player, world
    world = World(optsList)
    player = Player(world)
    makeTerrainObjects()

####Generative Logic (via game start parameters)

#Random point distribution to distribute "spawn" points for biomes,
#after which terrain is placed into a biome category based on closest spawn 
def makeBiomes(biomeList, numBiomes):

    for i in range(numBiomes):
        ptX = random.randint(0, world.row)
        ptZ = random.randint(0, world.cols)
        biomeLoc = PVector(ptX, 0, ptZ)
        if world.terrain[ptX][ptZ] >= 0:
            biomeVal = "ocean"
        elif world.terrain[ptX][ptZ] <= -world.tScl / 2:
            biomeVal = "mountain"
        else:
            biomeVal = random.choice(world.biomeOptions)
        biomeList.append((biomeLoc, biomeVal))

    for i in range(world.row + 1):
        for j in range(world.cols + 1):
            minDist, closeBiome = None, None
            for k, biome in enumerate(biomeList):
                d = distance(PVector(i, 0, j), biome[0])
                if minDist == None:
                    minDist = d
                    closeBiome = k
                elif d < minDist:
                    minDist = d
                    closeBiome = k
            world.biomeVals[i][j] = biomeList[closeBiome][1]
            world.biomeColor[i][j] = getBiomeColor(biomeList[closeBiome][1])


def getBiomeColor(biomeVal):
    if biomeVal == 'desert':
        return(35, 128)
    elif biomeVal == 'mountain':
        return(0, 0)
    elif biomeVal == 'jungle':
        return(99, 152)
    elif biomeVal == 'plains':
        return(67, 152)
    elif biomeVal == 'ocean':
        return(150, 128)

# Manual weights determine creature spawning in each biome type. 
def placeCreatures(numCreatures, terrainObjects, creatureList):
    cCount = 0
    while cCount < numCreatures:
        random.seed()
        ptX = random.randint(0,world.row)
        ptZ = random.randint(0,world.cols)

        while world.creatureList[ptX][ptZ] != [None]:
            ptX = random.randint(0,world.row)
            ptZ = random.randint(0,world.cols)

        ptY = terrainObjects[ptX][ptZ]["y"]
        biome = terrainObjects[ptX][ptZ]["bVal"]

        if biome == "ocean":
            tetra, grower, bubble, planar, light = 0.0, 0.0, 0.1, 0.0, 0.01
        elif biome == "desert":
            tetra, grower, bubble, planar, light = 0.4, 0.0, 0.0, 0.05, 0.01
        elif biome == "mountain":
            tetra, grower, bubble, planar, light = 0.6, 0.0, 0.1, 0.0, 0.02
        elif biome == "jungle":
            tetra, grower, bubble, planar, light = 0.1, 0.6, 0.0, 0.02, 0.0
        elif biome == "plains":
            tetra, grower, bubble, planar, light = 0.2, 0.2, 0.2, 0.02, 0.01
            
        testVal = random.uniform(0, 1)
        if testVal < tetra:
            creatureType = 'Tetra'
        elif testVal < tetra + grower:
            creatureType = 'Grower'
        elif testVal < tetra + grower + bubble:
            creatureType = 'Bubble'
        elif testVal < tetra + grower + bubble + planar:
            creatureType = 'Planar'
        elif testVal < tetra + grower + bubble + planar + light:
            creatureType = 'Light'
        else:continue
        
        c = Creature.makeCreature(creatureType,world,ptX,ptY,ptZ)
        
        if c != None:
            if creatureList[ptX][ptZ] == [None]:
                creatureList[ptX][ptZ] = [c]
                cCount += 1

def getFlows(numFlows,terrainObjects):
    flowList = []
    i = 0
    while i < numFlows:
        ptX = random.randint(0, world.row)
        ptZ = random.randint(0, world.cols)
        if terrainObjects[ptX][ptZ]["y"] <= 0:
            biome = terrainObjects[ptX][ptZ]["bVal"]
            if biome != "ocean" and biome != "desert":
                flowList.append((ptX, ptZ))
                i += 1
    return flowList

#Analyses lowest-pt paths and includes a bit of erosion for
#realistic results. Weighted via amplitude

def flowLines(terrainObjects, flowPaths, flowList):
    for a, flowStart in enumerate(flowList):
        flowPaths[a] = [flowStart]
        i, j = flowStart[0], flowStart[1]

        downhill = True

        while downhill:
            maxDown = 0
            dX, dZ = 0, 0
            downhill = False

            for k in range(-1, 2):
                for l in range(-1, 2):
                    if 0 < i + k < world.row and 0 < j + l < world.cols:
                        if terrainObjects[i + k][j + l]["y"] - terrainObjects[i][j]["y"] > maxDown:
                            downhill = True
                            maxDown = terrainObjects[i + k][j + l]["y"] - terrainObjects[i][j]["y"]
                            dX, dZ = k, l
            i += dX
            j += dZ
            flowPaths[a].append((i, j))
            if terrainObjects[i][j]["flows"] == None:
                terrainObjects[i][j]["flows"] = [a]
            elif not (a in terrainObjects[i][j]["flows"]):
                terrainObjects[i][j]["flows"].append(a)
            if 0 < i+1 < world.row and 0 < j+1 < world.cols:
                terrainObjects[i + 1][j]["y"] += 1 + world.tScl/100
                terrainObjects[i][j+1]["y"] += 1 + world.tScl/100




def placeResources(density, terrainObjects, resourceList):
    for i in range(1, world.row):
        for j in range(1, world.cols):
            biome = terrainObjects[i][j]["bVal"]
            if biome == "desert":
                rock, tree, none = 0.1, 0.1, 0.8
            elif biome == "ocean":
                rock, tree, none = 0.0, 0.0, 1.0
            elif biome == "jungle":
                rock, tree, none = 0.1, 0.9, 0.0
            elif biome == "mountain":
                rock, tree, none = 0.9, 0.1, 0.0
            elif biome == "plains":
                rock, tree, none = 0.4, 0.4, 0.0
            if random.uniform(0, 100) < density: #chance something will be generated at all
                if random.uniform(0, 1) < rock: 
                    resourceList[i][j] = Resource.makeResource(terrainObjects, i, j, "Rock", world)
                elif rock < random.uniform(0, 1) < rock + tree:
                    resourceList[i][j] = Resource.makeResource(terrainObjects, i, j, "Tree", world)
                else:
                    resourceList[i][j] = None
            else:
                resourceList[i][j] = None

#Compiling it all into one lovely terrain Object! List of dicts.
def makeTerrainObjects():  
    row, cols = world.row, world.cols
    terrainObjects = world.terrainObjects

    for i in range(row + 1):
        for j in range(cols + 1):
            terrainObjects[i][j]["y"] = world.terrain[i][j]

    makeBiomes(world.biomeList, world.numBiomes)
    
    for i in range(row + 1):
        for j in range(cols + 1):
            if world.biomeVals[i][j] == 'ocean': terrainObjects[i][j]["y"] = 0
            if world.biomeVals[i][j] == 'mountain': 
                terrainObjects[i][j]["y"] = map(terrainObjects[i][j]["y"], 0, -world.tScl, 0, -world.tScl * 2)
            terrainObjects[i][j]["bVal"] = world.biomeVals[i][j]
            terrainObjects[i][j]["bCol"] = world.biomeColor[i][j]
            
    for i in range(row + 1):
        for j in range(cols + 1):
            terrainObjects[i][j]["flows"] = None
            
    flowLines(terrainObjects, world.flowPaths, getFlows(world.flowNum,terrainObjects))

    placeCreatures(world.numCreatures, terrainObjects, world.creatureList)
    placeResources(world.resourceDensity, terrainObjects, world.resourceList)

    for i in range(row + 1):
        for j in range(cols + 1):
            terrainObjects[i][j]["cList"] = world.creatureList[i][j]
            terrainObjects[i][j]["rList"] = world.resourceList[i][j]


def distance(a, b):
    return((b.x - a.x) ** 2 + (b.y - a.y) ** 2 + (b.z - a.z) ** 2) ** 0.5


# ALPHA FUNCTION (Fading off into the distance - Currently set to black)
# Color fade logic was implemented to change to any color, but was slower.

def getAlp(xLoc, zLoc, i, j, scl, r):
    xAlp = (((i * scl) - (player.camX)) / scl) ** 2
    yAlp = (((j * scl) - (player.camZ)) / scl) ** 2
    return map((xAlp + yAlp) ** 0.5, 0, r, 500, 0)

def drawFlow(terrainObjects, flowPaths, a, xLoc, zLoc, scl, r):
    flow = flowPaths[a]
    with beginShape():
        noFill()
        for k in range(len(flow)):
            x, z = flow[k]
            y = terrainObjects[x][z]["y"]
            alp = getAlp(xLoc, zLoc, x, z, scl, r)
            colorMode(HSB)
            stroke(150, 150, alp-40)
            noFill()
            strokeWeight(1.5*k)
            strokeCap(ROUND)
            curveVertex(x * scl, y - abs(world.tScl/20), z * scl)

# head = PVector(0, 0, 0)

isSave = False #press g to start recording your screen! press g again to stop. 

### MAIN DRAW LOOP
def draw():

    if gameMode == "start":
        drawStart()
        
    
    if gameMode == "menu":
        background(20)
        drawMenu()

    if gameMode == "tutorial":
        global tutorial
        background(20)
        image(tutorial,0,0)
        
    elif gameMode == "play" or gameMode == "paused":
        background(0)
        
        #referenced both to get the performance benefit of the local variable
        #as well as for brevity.
        
        row,cols,scl = world.row,world.cols,world.scl
        terrainObjects = world.terrainObjects
        
        # KEYS CONTROL CAMERA TRANSLATION MOVEMENT
        if gameMode == "play":
            if player.keyDict["w"]:
                player.camX += player.head.x;player.camY += player.head.y;player.camZ += player.head.z
                player.eyeX += player.head.x;player.eyeY += player.head.y;player.eyeZ += player.head.z
            if player.keyDict["s"]:
                player.camX -= player.head.x;player.camY -= player.head.y;player.camZ -= player.head.z
                player.eyeX -= player.head.x;player.eyeY -= player.head.y;player.eyeZ -= player.head.z
            if player.keyDict["d"]:
                player.camX -= player.head.z;player.camY += player.head.y;player.camZ += player.head.x
                player.eyeX -= player.head.z;player.eyeY += player.head.y;player.eyeZ += player.head.x
            if player.keyDict["a"]:
                player.camX += player.head.z;player.camY += player.head.y;player.camZ -= player.head.x
                player.eyeX += player.head.z;player.eyeY += player.head.y;player.eyeZ -= player.head.x
            if player.keyDict["q"]:  # linearly raises
                player.camY += 1 * player.moveSpeed
                player.eyeY += 1 * player.moveSpeed
            if player.keyDict["e"]:  # linearly drops
                player.camY -= 1 * player.moveSpeed
                player.eyeY -= 1 * player.moveSpeed
            if player.keyDict[" "]:
                player.moveSpeed += 0.05
            if not player.keyDict[" "]:  # autoSpeed!
                if player.moveSpeed > 2.0:
                    player.moveSpeed -= 0.05
            if player.keyDict["x"]: 
                player.moveSpeed = 0
                for item in player.keyDict:
                    item = False
            if player.moveSpeed > 0:
                if player.keyDict["c"]:
                    player.moveSpeed -= 0.1
    
            # modifier
            player.head = PVector(player.eyeX - player.camX, player.eyeY - player.camY, player.eyeZ - player.camZ)
            player.head.setMag(1 * player.moveSpeed)
    
            # MOUSE POSITION CONTROLS CAMERA VIEW DIRECTION
    
            if mouseX > 0 and mouseY > 0:
                if mouseX > width / 2:
                    diff = map(abs(width / 2 - mouseX), 0, height / 2, 0, 0.01)
                    player.theta += diff * player.lookSpeed
                elif mouseX < width / 2:
                    diff = map(abs(width / 2 - mouseX), 0, height / 2, 0, 0.01)
                    player.theta -= diff * player.lookSpeed
                if mouseY < height / 2:
                    diff = map(abs(height / 2 - mouseY), 0, height / 2, 0, 0.01)
                    if not player.yTheta < -pi / 2:
                        player.yTheta -= diff * player.lookSpeed
                elif mouseY > height / 2:
                    diff = map(abs(height / 2 - mouseY), 0, height / 2, 0, 0.01)
                    if not player.yTheta > pi / 2:
                        player.yTheta += diff * player.lookSpeed
    
                # Colliding with ground
                if player.camX > 0 and player.camX < cols * scl and player.camZ > 0 and player.camZ < row * scl:
                    i = int(floor(player.camX / scl))
                    j = int(floor(player.camZ / scl))
                    yHeight = min([terrainObjects[i + m][j + n]["y"]
                                for m in range(-1, 2) for n in range(-1, 2)])
                    
                #Gravities!
                    temp = player.camY
                    if player.camY < yHeight - 11:
                        player.camY += 0.1 * player.gravity
                        player.eyeY += (player.camY - temp)
                    elif player.camY > yHeight - 10:
                        player.camY -= 2.0
                        player.eyeY += (player.camY - temp)

        # CAMSHIFT HAPPENS HERE
        player.eyeX = player.camX + (player.r * cos(player.theta))
        player.eyeZ = player.camZ + (player.r * sin(player.theta))
        player.eyeY = player.camY + (player.r * sin(player.yTheta))
        camera(player.camX, player.camY, player.camZ, player.eyeX, player.eyeY, player.eyeZ, 0, 1, 0)

        ### MAKING TERRAIN ###
        xLoc = int(floor(player.camX / scl))
        zLoc = int(floor(player.camZ / scl))
        try: #beats out the equivalent conditional performance-wise
            yLoc = abs(int((terrainObjects[xLoc][zLoc]["y"] - player.camY) / scl))
        except:
            yLoc = 0

        #establishes looking direction
        player.targX = int(xLoc + player.head.x * 2)
        player.targZ = int(zLoc + player.head.z * 2)
        colorMode(HSB)

        # first round of the iteration is determining which terrain to draw from the base location
        # frustrum "rectangle" culling - additional inclusions for aspect ratio and height above terrain
        
        phi = PI / 3.0
        r = world.drawRadius
        aspect = width/height - 1
        
        iMin = int(min([r * cos(player.theta - phi / 2), r * cos(player.theta + phi / 2), -aspect*2])) - (1 + (yLoc // 4))
        iMax = int(max([r * cos(player.theta - phi / 2), r * cos(player.theta + phi / 2), aspect*2])) + (1 + (yLoc // 4))
        jMin = int(min([r * sin(player.theta - phi / 2), r * sin(player.theta + phi / 2), -aspect*2])) - (1 + (yLoc // 4))
        jMax = int(max([r * sin(player.theta - phi / 2), r * sin(player.theta + phi / 2), aspect*2])) + (1 + (yLoc // 4))

        drawnFlows = set()
        
        
        ##Fetch and draw all the stuff whose indices were just determined
        for i in xrange(xLoc + iMin, xLoc + iMax):
            for j in xrange(zLoc + jMin, zLoc + jMax):

                if 0 < i and i < row and 0 < j and j < cols: #add angle calculation

                    strokeWeight(3)
                    #Terrain
                    with beginShape(QUADS): 
                        for k in xrange(0, 2):
                            lrange = xrange(0, 2) if k == 0 else xrange(1, -1, -1)
                            for l in lrange:
                                # all of the coloring done before the vertex is fetched
                                alp = getAlp(xLoc, zLoc, i+l, j+k, scl,r)
                                fill(terrainObjects[i+l][j+k]["bCol"][0], terrainObjects[i+l][j+k]["bCol"][1], constrain(alp,0,30))
                                stroke(terrainObjects[i+l][j+k]["bCol"][0], terrainObjects[i+l][j+k]["bCol"][1], alp)
                                vertex((i+l) * scl, terrainObjects[i+l][j+k]["y"], ((j+k) * scl))
                    
                    noFill()
                    strokeWeight(2)
                    
                    #Creatures
                    if len(terrainObjects[i][j]["cList"]) != 0 and terrainObjects[i][j]["cList"][0] != None:
                        if len(terrainObjects[i][j]["cList"]) > 1:
                            terrainObjects[i][j]["cList"] = Creature.checkMerge(terrainObjects,i,j,world)
                        for c in terrainObjects[i][j]["cList"]:
                            if c.__class__.__name__ == 'Grower':
                                if gameMode == "play":
                                    c.move(terrainObjects, i, j, 1.0, scl, world)
                                c.moveBranches(0.005)
                                c.recurseBranches()
                                
                            elif c.__class__.__name__ == 'Bubbles':
                                with pushMatrix():
                                    if gameMode == "play":
                                        c.move(terrainObjects, i, j, 1.0, scl, world)
                                    translate(c.pos.x, c.pos.y, c.pos.z)
                                    if c.level != (c.num**0.5)//4:
                                        c.makeSpheres((c.num**0.5)//4)
                                        c.level = (c.num**0.5)//4
                                    c.display()
                                    
                            elif c.__class__.__name__ == 'Planar':
                                with pushMatrix():
                                    if gameMode == "play":
                                        c.move(terrainObjects, i, j, 1.0, scl, world)
                                    translate(c.pos.x, c.pos.y, c.pos.z)
                                    if c.level != c.num//4:
                                        c.reNumber()
                                        c.makeRectangles()
                                    c.display()
                                    
                            elif c.__class__.__name__ == 'Light':
                                with pushMatrix():
                                    if gameMode == "play":
                                        c.move(terrainObjects, i, j, 1.0, scl, world)
                                    translate(c.pos.x, c.pos.y, c.pos.z)
                                    if c.level != c.num:
                                        c.initLists()
                                    c.run()
                                    
                            elif c.__class__.__name__ == 'Tetrahedron':
                                with pushMatrix():
                                    if gameMode == "play":
                                        c.move(terrainObjects, i, j, 1.0, scl, world)
                                    translate(c.pos.x, c.pos.y, c.pos.z)
                                    rotateY(frameCount / 200.0)
                                    if (c.num**0.5)//3 >=2:
                                        for pt in c.vertices:
                                            pt.setMag(c.size*sin(map(frameCount%200,0,200,0.25,PI-0.25)))
                                        c.recurseTetrahedron(c.vertices,c.size*sin(map(frameCount%400,0,400,0,PI)))
                                    else:
                                        c.recurseTetrahedron(c.vertices,c.size)
                    #Resources
                    if terrainObjects[i][j]["rList"] != None:
                        resource = terrainObjects[i][j]["rList"]
                        resource.display(getAlp(xLoc, zLoc, i, j, scl,r))
                        
                        
                    #Flows    
                    if terrainObjects[i][j]["flows"] == None:
                        continue
                    else: 
                        a = terrainObjects[i][j]["flows"][0]
                        if not (a in drawnFlows):
                            drawFlow(terrainObjects, world.flowPaths, a, xLoc, zLoc, scl, r)
                            drawnFlows.add(a)
                            
        #selector (press Z to toggle) 
        select(row,cols,player.targX,player.targZ)

        #Camera reset for HUD drawing
        camera()
        strokeWeight(1)
        textSize(13.0)
        stroke(255)
        fill(255)
        textMode(MODEL)
        screenText(player.camX, player.camZ, player.camY, player.head, player.yTheta, yLoc)

def mouseClicked():
    
    global optsList, gameMode, prevMode
    
    if gameMode == "start":
        if width / 2 - 150 < mouseX < width / 2 + 150 and height / 2 + 12 < mouseY < height / 2 + 87:
            gameMode = "menu"
        if (width/2)-120 < mouseX < (width/2) + 120 and height-100 < mouseY < height - 25:
            gameMode = "tutorial"
            prevMode = "start"
            
    elif gameMode == "tutorial":
        if mouseX > width*3/4 and mouseY > height*3/4:
            gameMode = prevMode
    
    elif gameMode == "paused":
        if (width/2)-120 < mouseX < (width/2) + 120 and height-200 < mouseY < height - 125:
            gameMode = "tutorial"
            prevMode = "paused"
    
    elif gameMode == "menu":
        if (width/2)-120 < mouseX < (width/2) + 120 and height-100 < mouseY < height - 25:
            fill(20)
            noStroke()
            rect(0,0,width,height)
            fill(255)
            stroke(255)
            textAlign(CENTER)
            text("S Y N T H E S I S", width/2, height/2) #doesn't show up all too much. program lags.
            gameMode = "play"
            makeWorld(optsList)
            
        
        elif mouseX < width/2:
            for j in range(3):
                if  150+(j-1)*height/4 + height/8 < mouseY < 150 + j*height/4 + height/8:
                    if mouseY < 150 + j*height/3:
                        optsList[j] = (optsList[j] + 1)%3
                    else:
                        optsList[j] = (optsList[j] - 1)%3            
        elif mouseX > width/2:
            for j in range(3):
                if  150+(j-1)*height/4 + height/8 < mouseY < 150 + j*height/4 + height/8:
                    if mouseY < 150 + j*height/4:
                        optsList[j+3] = (optsList[j+3] + 1)%3
                    else:
                        optsList[j+3] = (optsList[j+3] - 1)%3
                        
    #Selector operation contained here (always is on, only drawing is toggled) 
    elif gameMode == "play":
        
        targX, targZ = player.targX, player.targZ
        terrainObjects = world.terrainObjects
        row, cols = world.row, world.cols
        
        if 0 < targX < row and 0 < targZ < cols:
            selected = terrainObjects[targX][targZ]["cList"]
            dX, dZ = 0, 0

            if selected == [None]:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        test = terrainObjects[targX + i][targZ + j]["cList"]
                        if test != [None]:
                            dX, dZ = i, j
                            selected = test
                            break

            ### Creatures take priority over resources ##
            if selected == [None] or selected == []:
                selected = None
                selected = terrainObjects[targX][targZ]["rList"]
                dX, dZ = 0, 0

                if selected == None:
                    for i in range(-1, 2):
                        for j in range(-1, 2):
                            test = terrainObjects[targX + i][targZ + j]["rList"]
                            if test != None:
                                dX, dZ = i, j
                                selected = test
                                break

            # Has now selected something if there is anything to select
            if type(selected) == list:
                if len(selected) == 0:
                    selected = None
                else:
                    selected = selected[0]

            # collects resource from resource, might attack a creature
            if mouseButton == LEFT:
                if selected != None:
                    player.collectItem(selected.type)
                    isDead = selected.removeResource()
                    if isDead:
                        if isinstance(selected, Resource):
                            terrainObjects[targX + dX][targZ + dZ]["rList"] = None
                        elif isinstance(selected, Creature):
                            terrainObjects[targX + dX][targZ + dZ]["cList"] = [None]


            elif mouseButton == RIGHT:
                item = player.rMap[player.active]
                hadItem = player.dropItem()
                if selected == None and hadItem:
                    resource = Resource.makeResource(terrainObjects, targX, targZ, item, world)
                    terrainObjects[targX][targZ]["rList"] = resource
                elif isinstance(selected, Creature) and hadItem:
                    added = selected.addResource(item)
                    if not added:
                        resource = Resource.makeResource(terrainObjects, targX, targZ, item, world)
                        terrainObjects[targX][targZ]["rList"] = resource
                elif hadItem:
                    selected.addResource(item)

#Drawing the selector
def select(row,cols,targX,targZ):
    global world
    
    if player.view == True:

        for i in range(targX - 1, targX + 2):
            for j in range(targZ - 1, targZ + 2):
                if 0 < i < row and 0 < j < cols:
                    fill(40, 255, 30)
                    if i == targX and j == targZ:
                        fill(40, 255, 60)
                    strokeWeight(8)
                    stroke(255)
                    with beginShape(QUADS):
                        for k in xrange(0, 2):
                            lrange = xrange(
                                0, 2) if k == 0 else xrange(1, -1, -1)
                            for l in lrange:
                                vertex((i+l)*world.scl, world.terrainObjects[i+l][j+k]["y"], (j+k) * world.scl)

#Various controls
def keyPressed():
    global player, gameMode
    targX,targZ = player.targX,player.targZ

    if gameMode == "play":
        if key in player.keyDict:
            player.keyDict[key] = not player.keyDict[key]

        elif key != ' ':
            if key in set(str(range(0, len(player.resources)+1))):
                player.active = int(key) - 1

        if key == "p":
            gameMode = "paused"

        if key == "z":
            player.view = not player.view
            
        if key == "b":
            item = player.rMap[player.active]
            if item == player.getModeVal():
                c = Creature.makeCreature(item,world,targX,world.terrainObjects[targX][targZ]['y']-20,targZ)
                if world.terrainObjects[targX][targZ]['cList'] == [None]:
                    world.terrainObjects[targX][targZ]['cList'] = [c]
                else: world.terrainObjects[targX][targZ]['cList'].append(c)
                player.rd[item] -= 10
                player.inventory()
                
    if gameMode == "paused":
        if key == "r":
            gameMode = "play"

def keyReleased():
    if key in player.keyDict:
        player.keyDict[key] = not player.keyDict[key]

#menu draw functions etc.
def drawStart():
    with pushStyle():
        textMode(MODEL)
        background(20)
        textAlign(CENTER)
        textSize(36.0)
        fill(220)
        text("S Y N T H E T I C A", width / 2, height / 2 - 75)
        textSize(24.0)
        text("B E G I N", width / 2, height / 2 + 60 + textDescent())
        noFill()
        stroke(210)
        strokeWeight(1)
        line(width / 2 - 120, height / 2 + 25,
            width / 2 + 120, height / 2 + 25)
        line(width / 2 - 120, height / 2 + 100,
            width / 2 + 120, height / 2 + 100)
        text("T U T O R I A L", width / 2, height - 60 + textDescent())
        line(width / 2 - 120, height - 25, width / 2 + 120, height - 25)
        line(width / 2 - 120, height - 100, width / 2 + 120, height - 100)
    
def drawMenu():
    fill(220)
    stroke(220)
    strokeWeight(1)
    global optsList
    
    textOptions = ['Expanse: ','Creatures: ','Biodiversity: ','Amplitude: ','Resources: ','Sight: ']
    paramDict = {0:['Small','Medium','Synthetic'], 1:['Few','Several','Synthetic'], 2:['Uniform','Variant','Synthetic'],
                 3:['Flat','Normal','Synthetic'], 4:['Barren','Several','Synthetic'],5:['Short','Normal','Synthetic']}
    
    menuText(textOptions,paramDict)
    menuArrows()
    stroke(210)
    fill(210)
    if (width/2)-120 < mouseX < (width/2) + 120 and height-100 < mouseY < height - 25:
        stroke(255)
        fill(255)
        strokeWeight(2)
        
    text("G E N E R A T E", width / 2, height - 60 + textDescent())
    line(width / 2 - 120, height - 25, width / 2 + 120, height - 25)
    line(width / 2 - 120, height - 100, width / 2 + 120, height - 100)

def menuText(textOptions,paramDict):
    for j in range(3):
        textAlign(LEFT)
        text(textOptions[j], 100, 150 + j*height/4 + textDescent())
        textAlign(CENTER)
        text(paramDict[j][optsList[j]], 300, 150 + j*height/4 + textDescent())
    for k in range(3):
        textAlign(LEFT)
        text(textOptions[k+3], 100 + width/2, 150 + k*height/4 +textDescent())
        textAlign(CENTER)
        text(paramDict[k+3][optsList[k+3]], 300 + width/2, 150 + k*height/4 + textDescent())
    noFill()
    
def menuArrows():
    for i in range(2):
        for j in range(3):
            with beginShape():
                vertex(275 + i*width/2, 100 + j*height/4)
                vertex(300 + i*width/2, 75 + j*height/4)
                vertex(325 + i*width/2, 100 + j*height/4)
            with beginShape():
                vertex(275 + i*width/2, 200 + j*height/4)
                vertex(300 + i*width/2, 225 + j*height/4)
                vertex(325 + i*width/2, 200 + j*height/4)
    
def drawTutorial():
    textOptions = ['W','A','S','D']
    paramDict = {0:['Small','Medium','Synthetic'], 1:['Few','Several','Synthetic'], 2:['Uniform','Variant','Synthetic'],
                 3:['Flat','Normal','Synthetic'], 4:['Barren','Several','Synthetic'],5:['Short','Normal','Synthetic']}


def screenText(camX, camZ, camY, head, yTheta, yLoc):
    global player, gameMode
    stroke(player.col[0],player.col[1],player.col[2])
    fill(player.col[0],player.col[1],player.col[2])
    hint(DISABLE_DEPTH_TEST)
    lights()
    textMode(SCREEN)
    textAlign(LEFT)
    text(str(int(frameRate)), 10, 10 + textAscent())
    text("FPS", 10, 30 + textAscent())
    text("X Heading: " + ("+" if head.x > 0 else "-"), 10, height - 45 + textAscent())
    text("Z Heading: " + ("+" if head.z > 0 else "-"), 10, height - 30 + textAscent())
    textAlign(RIGHT)
    text(str(player.moveSpeed), width - 10, 10 + textAscent())
    text("Range", width - 10, 30 + textAscent())
    text("Off Ground: "+str(yLoc) + "' ", width - 10, height - 45 + textAscent())
    text("View Angle: "+str(int((-yTheta) * 180 / pi)) + chr(176),
         width - 10, height - 30 + textAscent())
    textAlign(CENTER)
    text("( %s , %s , %s )"%(int(camX),int(camY),int(camZ)), width / 2, 10 + textAscent())
    text("Current Position", width / 2, 30 + textAscent())
    strokeCap(SQUARE)
    line(width / 2 - 10, height / 2, width / 2 + 10, height / 2)
    line(width / 2, height / 2 - 10, width / 2, height / 2 + 10)
    player.drawInventory()
    
    if gameMode == "paused":
        fill(0,180)
        noStroke()
        rect(0,0,width,height)
        drawPaused()
        
    hint(ENABLE_DEPTH_TEST)

def drawPaused():
    textAlign(CENTER)
    textSize(36.0)
    fill(220)
    text("S Y N T H E T I C A", width / 2, height / 2 - 75)
    textSize(24.0)
    text("P A U S E D", width/2, height/2)
    stroke(120)
    strokeWeight(1)
    line(width/2 - 200, height/2 + 10, width/2 + 200, height/2 + 10)
    textSize(16.0)
    text("ESC to desynth. R to resume.", width/2, height/2 + 30)
    line(width/2 - 200, height/2 + 10, width/2 + 200, height/2 + 40)
    textSize(18.0)
    stroke(player.col[0],player.col[1],player.col[2])
    fill(player.col[0],player.col[1],player.col[2])
    if player.mode == "basic":
        text("THE ARTEFACT IS NOT YET INITIALISED.", width/2, height/2 + 60)
    else:
        text("THE ARTEFACT IS IN %s MODE."%player.mode.upper(), width/2, height/2 + 60)
    stroke(220)
    fill(220)
    text("T U T O R I A L", width / 2, height - 160 + textDescent())
    line(width / 2 - 120, height - 125, width / 2 + 120, height - 125)
    line(width / 2 - 120, height - 200, width / 2 + 120, height - 200)
                