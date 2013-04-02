# Contains functions for generating new XML gamestates.
#
# Josh Polkinghorn

from MapData import Gamestate, Planet, Region
import random
import math
import operator

class Mapmaker:
    def __init__(self):
        self.gs = Gamestate()
        self.MIN_RADIUS = 20
        self.MAX_RADIUS = 50

    # Writes the currently stored Gamestate to a file.
    def write(self, file):
        if len(self.gs.pList) == 1:
            print("Error: no gamestate stored. Use \"this.generate(...)\""+
                  " to generate a map.")
            return
        try:
            f = open(file+".xml", mode='w')
            f.write(self.gs.writeToXML().toprettyxml())
            print("Successfully wrote to file.")
        except:
            print("Error: unable to open file.")
        return
    
    def generate(self, numPlanets, numRegions, aspectRatio=1.0,
                 minDistance=75, connectivity=2.0, elasticity=1.05, seed=None):
        # Step 0: Input validation
        if (numRegions > numPlanets / 2):
            return "Error: too few planets for that many regions."
        if (aspectRatio < 0):
            return "Error: invalid aspect ratio."

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
        self.gs.cList = generateConnections(self.gs.pList, connectivity,
                                            elasticity)

       

        # -------------------------------------
        # Step 4: Find regions covering planets
        # -------------------------------------
        # TODO actually do this
        members = []
        for i in range(numPlanets+1):
            if i == 0: continue
            members.append(i)
        r = Region(members, 1, 10)
        self.gs.rList.append(r)



        # Finally, output resulting gamestate
        result = self.gs.writeToXML()
        return result

# ----------------------------------
# ---       Helper Methods       ---
# ----------------------------------

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
                p1.color = str(hex(random.randint(0, 16777215)))
                p1.color = '#' + p1.color[2:].zfill(6)
                addSuccess = True

    print("Done.")
    return pList

# -----------
# Connections
# -----------

# Generates a random set of connections between planets.
# - connectivity: average connections per planet
#       (minimum of 2.0; maximum of numPlanets-1)
# - elasticity: randomness in determining distance
#       (1.0 indicates no randomness; higher means more random)
def generateConnections(pListIn, connectivity, elasticity):
    # Validate parameters
    if (connectivity < 2.0) or (connectivity >= len(pListIn) - 1):
        print("Error: illegal connectivity: "+str(connectivity)+
              "\nAcceptable values are [1.0, "+str(len(pListIn)-1)+"].")
        return

    # Setup needed variables
    print("Generating connections...", end=' ')
    cList = set()
    pList = list(pListIn) # copies the list to avoid changing it
    totalConnections = math.ceil(len(pList) * connectivity / 2)
    dists = findDistances(pList)

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
                print("Error: distance between",p1,"and",p2,"is",str(dist))
            result[p1.idNum][p2.idNum] = dist
        result[p1.idNum].pop(p1.idNum) # gets rid of the self-referencing dist
    return result

# Special code for storing connections
def addConnection(cList, p1, p2):
    if p1 > p2:
        temp = p1
        p1 = p2
        p2 = temp
    if p1 == p2:
        print("Error: connections must have different start and end points.", sys.stderr)
    if p1 == 0 or p2 == 0:
        print("Error: Cannot connect to planet 0.", sys.stderr)

    # Adds the connection, checking to see if it was added successfully
    size = len(cList)
    cList.add(str(p1) + ',' + str(p2))
    return (size < len(cList))

if __name__ == '__main__':
    m = Mapmaker()
    print("To generate maps: m.generate(...)",
          "--> numPlanets: number of planets",
          "--> numRegions: number of regions",
          "--> [aspectRatio]: size of the world as (x/y) (default: 1.0)",
          "--> [minDistance]: minimum distance between planets in pixels (default: 75)",
          "--> [connectivity]: avg. # of connections per planet (default: 2.0)",
          "--> [elasticity]: randomness in generating connections (default: 1.05)",
          "--> [seed]: random seed to use (default: random)", sep='\n')
    #self, numPlanets, numRegions, aspectRatio=1.0,
    #minDistance=75, connectivity=2.0, elasticity=1.05, seed=None
    #test = m.generate(15, 3, connectivity=2.0)
    #try:
    #    print(test.toprettyxml())
    #except:
    #    print(test)
    
