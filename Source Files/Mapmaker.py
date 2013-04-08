# Contains functions for generating new XML gamestates.
# For more details, see Mapmaker.printInstructions().
#
# Josh Polkinghorn

from MapData import Gamestate, Planet, Region
import random
import math
import operator
import queue

class Mapmaker:
    def __init__(self):
        self.gs = Gamestate()
        self.params = MapmakerParameters()
        self.MIN_RADIUS = 15
        self.MAX_RADIUS = 30

    # Writes the currently stored Gamestate to a file.
    def write(self, file):
        if len(self.gs.pList) == 1:
            raise Exception("Error: no gamestate stored. Use "+
                  "\"this.generate(...)\" to generate a map.")
        try:
            f = open(file+".xml", mode='w')
            f.write(self.gs.writeToXML().toprettyxml())
            print("Successfully wrote to file.")
        except:
            raise Exception("Error: unable to open file.")
        return

    def printParams(self):
        self.params.printParams()

    def printInstructions():
        print("""To generate maps: m.generate(...)
--> numPlanets: number of planets
--> numRegions: number of regions
--> [aspectRatio]: size of the world as (x/y) (default: 1.0)
--> [minDistance]: minimum distance between planets in pixels (default: 75)
--> [connectivity]: avg. # of connections per planet (default: 2.0)
--> [elasticity]: randomness in generating connections (default: 1.05)
--> [seed]: random seed to use (default: random)""")

    # Generates a map from the stored parameters.
    def generateFromParameters(self):
        return self.generate(self.params.numPlanets,
                             self.params.numRegions,
                             self.params.aspectRatio,
                             self.params.minDistance,
                             self.params.connectivity,
                             self.params.elasticity,
                             self.params.seed)
    
    def generate(self, numPlanets, numRegions, aspectRatio=1.0,
                 minDistance=75, connectivity=2.0, elasticity=1.05, seed=None):
        # Step 0: Input validation
        if (numRegions > numPlanets / 3):
            raise Exception("Error: too few planets for that many regions.")
        if (aspectRatio < 0):
            raise Exception("Error: invalid aspect ratio.")

        # Declares needed variables
        self.gs = Gamestate() # clear the existing gamestate
        rList = [None]
        cList = [None]
        if seed is not None:
            random.seed(seed)

        # -----------------------------------------------------
        # Step 1: Calculate the size of the map to be generated
        # -----------------------------------------------------
        
        # Planets are (at most) MAXRADIUS*2 in diameter, so we need at least
        # that much space per planet, plus the minimum distance between them
        neededSpace = numPlanets * ((self.MAX_RADIUS*2 + minDistance)**2)

        # sizeX * sizeY >= neededSpace; so sizeX = sizeY * aspectRatio;
        # therefore, sizeY * (sizeY * aspectRatio) >= neededSpace
        sizeY  = math.sqrt(neededSpace / aspectRatio)+1
        sizeY *= random.uniform(1, 1.75) # makes the size somewhat random
        sizeY  = int(sizeY)
        sizeX  = int(sizeY * aspectRatio)
        self.gs.xSize = sizeX
        self.gs.ySize = sizeY

        # ---------------------------------------------
        # Step 2: Generate a random sampling of planets
        # ---------------------------------------------
        self.gs.pList = generatePlanets(numPlanets, sizeX, sizeY,
                                        self.MIN_RADIUS, self.MAX_RADIUS,
                                        minDistance)
        # Adds a visual buffer around the planets
        for p in self.gs.pList:
            if p is None: continue
            p.xPos += 100
            p.yPos += 100
        self.gs.xSize = sizeX = sizeX + 200
        self.gs.ySize = sizeY = sizeY + 200

        # ---------------------------------------------------
        # Step 3: Generate random connections & validate them
        # ---------------------------------------------------
        valid = False
        dists = findDistances(self.gs.pList) # we reuse this later
        while not valid:
            self.gs.cList = generateConnections(self.gs.pList, dists, 
                                                connectivity, elasticity)
            
            # Ensures that any planet can be reached from any other planet
            connected = set()
            toSearch = queue.Queue()
            connected.add(self.gs.pList[1].idNum) # Seed the queue
            for con in self.gs.getConnections(self.gs.pList[1].idNum):
                toSearch.put(con)
            while not toSearch.empty():
                test = int(toSearch.get())
                # If we haven't searched this planet already...
                if test not in connected:
                    # ... add it
                    connected.add(test)
                    for con in self.gs.getConnections(self.gs.pList[test].idNum):
                        toSearch.put(con)

            # If these are equal, all planets are fully connected
            if len(connected) is len(self.gs.pList) - 1:
                valid = True
        # end while valid

        # -------------------------------------
        # Step 4: Find regions covering planets
        # -------------------------------------
        self.gs.rList = generateRegions(self.gs.pList, dists, numRegions)

        # Region values are calculated here because they depend on the
        # entire Gamestate.
        for r in self.gs.rList:
            if r is None: continue
            # Value depends on two things: first, the number of planets
            # in the region...
            score = len(r.members)

            # ... and second, the number of unique connections between this
            # region and other regions.
            allCons = []
            for m in r.members:
                allCons.extend(self.gs.getConnections(m))
            # Get the set of all planets connected to this region
            uniqueCons = set(allCons)
            for con in uniqueCons:
                # Increment score if the connection is external
                if con not in r.members:
                    score += 1
            
            r.value = math.floor(score / 3) + 1
            #print("Value for this region is "+str(r.value))

        # --------------------------------
        # Step 5: Breathe a sigh of relief
        # --------------------------------
        # Finally, output resulting gamestate
        self.out = self.gs.writeToXML()
        return self.out

# ----------------------------------
# ---       Helper Methods       ---
# ----------------------------------

# Returns a random hex color in the format "#F0F0F0"
def getRandomColor():
    result = str(hex(random.randint(0, 16777215)))
    result = '#' + result[2:].zfill(6)
    return result

# -------
# Planets
# -------

# Given a set of parameters, generates a list of Planets
def generatePlanets(numPlanets, sizeX, sizeY, minRad, maxRad, minDistance):
    print("Generating planets...", end=' ')
    pList = [None]
    for i in range(numPlanets):
        addSuccess = False # flag if this planet has been added successfully
        while not addSuccess:
            rad = random.randint(minRad, maxRad)
            x = random.randint(rad, sizeX-rad)
            y = random.randint(rad, sizeY-rad)
            p1 = Planet(i+1, x, y, rad)

            # Ensure minimum distance between planets
            for p2 in pList:
                if p2 is None or p1 is p2: continue
                # Calculates the distance between these two planets
                dist = math.sqrt( (p1.xPos - p2.xPos)**2 +
                                  (p1.yPos - p2.yPos)**2 )
                dist -= (p1.radius + p2.radius)

                # If dist is insufficient, reseed the planet
                if dist < minDistance:
                    break
            else: # If the for loop isn't exited with the break...
                pList.append(p1) # ...then the planet is safe to add.
                # Color only needs to be calculated once.
                p1.color = getRandomColor()
                addSuccess = True

    print("Done.")
    return pList

# -----------
# Connections
# -----------

# Generates a random set of connections between planets.
# - dists: the output of findDistances(pList)
# - connectivity: average connections per planet
#       (minimum of 2.0; maximum of numPlanets-1)
# - elasticity: randomness in determining distance
#       (1.0 indicates no randomness; higher means more random)
def generateConnections(pListIn, dists, connectivity, elasticity):
    # Validate parameters
    if (connectivity < 2.0) or (connectivity >= len(pListIn) - 1):
        raise Exception("Error: illegal connectivity: "+str(connectivity)+
              "\nAcceptable values are [2, "+str(len(pListIn)-1)+"].")

    # Setup needed variables
    print("Generating connections...", end=' ')
    cList = set()
    pList = list(pListIn) # copies the list to avoid changing it
    totalConnections = math.ceil(len(pList) * connectivity / 2)

    # Generate connections
    while (totalConnections > len(cList)):
        random.shuffle(pList)
        for p1 in pList:
            if p1 is None: continue
            pDists = dists[p1.idNum].copy()

            # Be careful with elasticity. Not enough makes things too
            # uniform; too much looks messy and visually confusing.
            for d in pDists:
                pDists[d] *= random.uniform(1, elasticity)
            
            while len(pDists) is not 0:
                # Returns the ID of the closest Planet to p1
                tarID = min(pDists.items(), key=operator.itemgetter(1))[0]
                # If the connection is added successfully...
                if (addConnection(cList, p1.idNum, tarID)):
                    break # ... go to the next iteration.
                else: # Otherwise, remove that option and try again.
                    pDists.pop(tarID)

    print("Done.")
    return cList

# Finds the distances between all Planets in a given list.
# Returns a 2D dictionary, where dists[a][b] = distance(a, b)
def findDistances(pList):
    result = {}
    for p1 in pList:
        if p1 is None: continue
        result[p1.idNum] = {}
        for p2 in pList:
            if p2 is None: continue
            if p1 is p2:
                dist = 0.0
            else:
                dist = math.sqrt( (p1.xPos - p2.xPos)**2 +
                                  (p1.yPos - p2.yPos)**2 )
            if (dist < 0):
                raise Exception("Error: distance between",p1,"and",p2,"is",str(dist))
            result[p1.idNum][p2.idNum] = dist
        result[p1.idNum].pop(p1.idNum) # gets rid of the self-referencing dist
    return result

# Special code for storing connections
def addConnection(cList, p1, p2):
    if p1 > p2:
        temp = p1
        p1 = p2
        p2 = temp
    # Error handling shoudn't be necessary in this case, but it's there anyway
    if p1 == p2:
        raise Exception("Error: connections must have different"+
                        " start and end points.")
    if p1 == 0 or p2 == 0:
        raise Exception("Error: Cannot connect to planet 0.")

    # Adds the connection, checking to see if it was added successfully
    size = len(cList)
    cList.add(str(p1) + ',' + str(p2))
    return (size < len(cList))

# -------
# Regions
# -------

# Finds semi-random minimal regions covering all planets.
# - dists: the output of findDistances(pList)
def generateRegions(pListIn, dists, numRegions):
    print("Generating regions... ", end='')
    
    # First, we find a random starting planet.
    # ----------------------------------------
    start = None
    while start is None:
        start = random.choice(pListIn)
    startPlanet = start.idNum

    # Then we find the planets farthest away from planets we've already found
    # -----------------------------------------------------------------------
    selectedPlanets = set()
    selectedPlanets.add(startPlanet)
    # While we still need more planets...
    while len(selectedPlanets) < numRegions:
        cumDists = [0]
        # ... loop through all the remaining planets...
        for p in pListIn:
            if p is None: continue
            # (skip already added planets)
            if p.idNum in selectedPlanets:
                cumDists.append(0)
                continue
            distSum = 0
            # ... and find the total distance between that planet...
            for sp in selectedPlanets:
                # ... and every previously selected planet.
                distSum += dists[sp][p.idNum]
            cumDists.append(distSum)
        # Now find the planet with the greatest distance.
        toAdd = cumDists.index(max(cumDists))
        # Ugh this is a mess
        selectedPlanets.add(toAdd)
    # Now we have n planets a maximum distance apart.
    
    # TESTING PURPOSES ONLY
    for sp in selectedPlanets:
        pListIn[sp].color = 'white'
    # NO SERIOUSLY GUYS

    # Now we can setup the initial region list.
    # -----------------------------------------
    rList = [None]
    regionIsFull = [None]
    for sp in selectedPlanets:
        rList.append(Region(len(rList)))
        rList[len(rList)-1].addMember(sp)
        regionIsFull.append(False) # i.e. not full yet
    
    # Next we assign a minimum number of planets to each region.
    # ----------------------------------------------------------
    for i in range(1, 3):
        for r in rList: # For each region...
            if r is None: continue
            # ... find the next closest planet...
            closest = getClosestPlanet(dists, selectedPlanets, r.members)
            # ... and add it to the region.
            r.addMember(closest)
            selectedPlanets.add(closest)
    
    # Now we assign the remaining planets.
    # ------------------------------------
    # This gets a set of all unassigned planets
    unassigned = set(range(1, len(pListIn))).difference(selectedPlanets)
    while len(unassigned) > 0:
        toAdd = unassigned.pop()
        targetRegion = getClosestRegion(dists, toAdd, rList)
        selectedPlanets.add(toAdd)
        rList[targetRegion].addMember(toAdd)
    
    # Whew.
    # -----
    # Anyway, as a final flourish, throw some colors on them.
    for r in rList:
        if r is not None:
            r.color = getRandomColor()

    print("Done.")
    return rList

# Finds the planet with the smallest total distance to
# the members of a given region.
# - dists: output of findDistances
# - selected: set of planets to ignore
# - members: list of planets for distance checking
def getClosestPlanet(dists, selected, members):
    totalDists = [None]
    for planet in dists.keys():
        if planet in selected: # First, ignore already selected planets
            totalDists.append(-1)
        else: # Each planet starts with zero distance
            totalDists.append(0)
            for m in members:
                totalDists[planet] += dists[planet][m]
    
    # Selects the shortest positive distance
    minDist = min(x for x in totalDists if x is not None and x > 0)
    return totalDists.index(minDist)

# Finds the region closest to the target planet.
def getClosestRegion(dists, target, rList):
    totalDists = [None] # between target and rList
    for r in rList:
        if r is None: continue
        totalDists.append(0)
        for m in r.members:
            totalDists[len(totalDists)-1] += dists[target][m]
    avgDists = list(totalDists)
    for i in range(1, len(avgDists)):
        avgDists[i] /= len(rList[i].members)

    # Selects the shortest distance
    minDist = min(x for x in avgDists if x is not None)
    return avgDists.index(minDist)

# -----------------------------------------------------------
# This class provides easy encapsulation for all the possible
# Mapmaker parameters.
#------------------------------------------------------------
class MapmakerParameters:
    def __init__(self):
        self.numPlanets = 10
        self.numRegions = 2
        self.aspectRatio = 1.0
        self.minDistance = 75
        self.connectivity = 2.0
        self.elasticity = 1.05
        self.seed = None

    def printParams(self):
        print("Parameters for Mapmaker object:",
              "-------------------------------",
              "--> numPlanets: "+str(self.numPlanets),
              "--> numRegions: "+str(self.numRegions),
              "--> aspectRatio: "+str(self.aspectRatio),
              "--> minDistance: "+str(self.minDistance),
              "--> connectivity: "+str(self.connectivity),
              "--> elasticity: "+str(self.connectivity),
              "--> seed: "+str(self.seed), sep='\n')
        print("For more details on each parameter, see",
              "Mapmaker.printInstructions().")

if __name__ == '__main__':
    m = Mapmaker()
    Mapmaker.printInstructions()
    #test = m.generate(15, 3, connectivity=2.0)
    #try:
    #    print(test.toprettyxml())
    #except:
    #    print(test)
    
