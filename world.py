#creates the world based on pre-set starting parameters, and a random seed that may
#(or may not) be defined in the setup() function.

class World():
    
    paramDict = {0:[100,250,500], 1:[10,50,100], 2:[3,15,50],#row/cols, numCreatures, numBiomes
                 3:[50,250,400], 4:[2,8,12], 5:[25,32,42]} #amplitude,rdensity,seed
    
    
    def __init__(self,optsList):
        self.scl = 32 #25 ## SIZE OF EACH MESH QUAD
        self.tScl = World.paramDict[3][optsList[3]] #400 ## POSSIBLE PERLIN AMPLITUDE
        self.row = World.paramDict[0][optsList[0]] #100 ## NUMBER OF TERRAIN X CHUNKS
        self.cols = World.paramDict[0][optsList[0]] #100 ## NUMBER OF TERRAIN Y CHUNKS
        self.drawRadius = World.paramDict[5][optsList[5]] # As far as the eye can see
        
        self.numBiomes = World.paramDict[2][optsList[2]]
        self.biomeOptions = ['desert','mountain','jungle','plains']
        self.numCreatures = World.paramDict[1][optsList[1]]
        self.resourceDensity = World.paramDict[4][optsList[4]]
        self.flowNum = 500 ## Number of rivers
        self.initWorld()
        
    #potential optimisation: have them be empties instead of Nones?
        
    def initWorld(self): #creates the basis for a ton of empty containers that will later be indexed
        #self.noiseShift = [[random.uniform(-scl/4,scl/4) for i in range(row+1)] for j in range (cols+1)] 
              #noiseshift could move the terrain to make it less regular, when active. 
        self.noiseShift = [[0 for i in range(self.row+1)] for j in range (self.cols+1)]
        self.terrain = [[map(noise((float(i)/10),float(j)/10),0,1,-self.tScl,self.tScl) 
                         for i in range(self.row+1)] 
                         for j in range (self.cols+1)]
        self.biomeColor = [[(0,0) for i in range(self.row+1)] for j in range (self.cols+1)]
        self.biomeVals = [[0 for i in range(self.row+1)] for j in range (self.cols+1)]
        self.biomeList = []
        self.creatureList = [[[None] for i in range(self.row+1)] for j in range (self.cols+1)]
        self.resourceList = [[None for i in range(self.row+1)] for j in range (self.cols+1)]
        self.flowPaths = [[] for i in range(self.flowNum)]
        self.terrainObjects = [[dict() for i in range(self.row+1)] for j in range (self.cols+1)]
    