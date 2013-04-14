# Contains all data and methods needed to
# represent a full game state.
#
# Josh Polkinghorn

from xml.dom.minidom import parse, parseString
import sys
import copy

class Gamestate:
    # Sets all fields to default values.
    def __init__(self):
        self.playerList = [0]
        self.activePlayer = 0
        self.turnNumber = 0
        self.cycleNumber = 0
        self.turninCount = 0
        self.pList = [None]
        self.rList = [None]
        self.cList = set()

    ### Methods ###
        
    ## Access methods ##

    # Sets the active player. Prints an error if the ID provided is invalid.
    def setActivePlayer(self, playerID):
        if playerID not in self.getActivePlayers():
            print("Error: Invalid player number.", sys.stderr)
        else:
            self.activePlayer = playerID

    # Increments the turn counter.
    def nextTurn(self):
        self.activePlayer += 1
        while self.playerList[self.activePlayer] is not 0:
            self.activePlayer += 1

        self.turnNumber += 1
        # If pID == first occurrence of status 1 (i.e. first active player)
        if playerID is self.playerList.index(1):
            self.cycleNumber += 1

    # Special code for storing connections
    def addConnection(self, p1, p2):
        if p1 > p2:
            temp = p1
            p1 = p2
            p2 = temp
        if p1 == p2:
            print("Error: connections must have different start and end points.", sys.stderr)
        if p1 == 0 or p2 == 0:
            print("Error: Cannot connect to planet 0.", sys.stderr)
        self.cList.add(str(p1) + ',' + str(p2))

    # Returns a string representation of the entire gamestate.
    def __str__(self):
        # First, the Gamestate itself.
        gs_str = ("Current Gamestate is as follows:\n" +
                  "--------------------------------\n")
        gs_str += ("Turn Number: " + str(self.turnNumber) +
                   ", Cycle Number: " + str(self.cycleNumber) + "\n")
        gs_str += "Active Player: " + str(self.activePlayer) + "\n"
        gs_str += "Turnin Count: " + str(self.turninCount) + "\n"

        # Then, planets...
        planet_str = ("\nList of Planets:\n" +
                      "--------------------------------\n")
        for p in self.pList:
            if p is not None:
                planet_str += str(p) + "\n"

        # ... connections...
        connect_str = ("\nList of Connections:\n" +
                      "--------------------------------\n")
        for c in self.cList:
            connect_str += "(" + c + ")\n"
        
        # ... and regions.
        region_str = ("\nList of Regions:\n" +
                      "--------------------------------\n")
        for r in self.rList:
            if r is not None:
                region_str += str(r) + "\n"

        result = (gs_str + planet_str + connect_str + region_str +
                  "--------------------------------\n")
        return result

    # Returns a deep copy of this gamestate.
    def copy(self):
        return copy.deepcopy(self)

    # Updates this gamestate based on a Gamechange.
    def update(self, change):
        self.turnNumber = change.turnNumber
        self.cycleNumber = change.cycleNumber
        self.activePlayer = change.activePlayer
        self.turninCount = change.turninCount
        for c in change.changes:
            p = self.pList[c[0]]
            p.owner = c[1]
            p.numFleets = c[2]
        self.updateRegions()

    # Updates the owners of all regions.
    def updateRegions(self):
        for region in self.rList:
            if region is None:
                continue
            testID = list(region.members)[0]
            testOwner = self.pList[testID].owner
            for memberID in region.members:
                if self.pList[memberID].owner is not testOwner:
                    testOwner = 0
            region.owner = testOwner

    # Returns the number of fleets the specified player can deploy.
    def getPlayerQuota(self, playerID):
        quota = 5
        for r in self.rList:
            if r is None:
                continue
            if r.owner is playerID:
                quota += r.value
        return quota
            
    ## Connection Methods ##
    
    # Adds a connection to the connection list.
    def addConnection(self, pair):
        start, end = pair.split(',')
        if start == end:
            print("Connections can't have the same start and end points.",
                  sys.stderr)
            return

        if int(start) > int(end):
            temp = start
            start = end
            end = temp
        self.cList.add(str(start) + "," + str(end))

    # Returns a list of all Planets that are connected to the specified Planet.
    def getConnections(self, pId):
        result = []
        for c in self.cList:
            start, end = c.split(',')
            if int(start) == pId:
                result.append(end)
            if int(end) == pId:
                result.append(start)

        return result

    # Returns true if two Planets are connected.
    def isConnected(self, p1, p2):
        if p1 > len(self.pList) or p2 > len(self.pList):
            print("Not a valid planet.", sys.stderr)
        if p1 > p2:
            temp = p2
            p2 = p1
            p1 = temp
        testSet = set()
        testSet.add(str(p1) + "," + str(p2))
        return self.cList.issuperset(testSet)

    ## XML Methods ##

    def loadXML(self, xmlString):
        # Will attempt to read as a string; if not, assumes it's a filename
        try:
            dom = parseString(xmlString)
        except:
            dom = parse(xmlString)

        # Dumps any existing data
        self.__init__()

        # Player data
        players = dom.getElementsByTagName("Players")[0]
        self.activePlayer = int(players.getAttribute("activePlayer"))
        self.turnNumber = int(players.getAttribute("turnNumber"))
        self.cycleNumber = int(players.getAttribute("cycleNumber"))

        # Planet List
        planetListEl = dom.getElementsByTagName("PlanetList")[0]
        planetList = planetListEl.getElementsByTagName("Planet")
        for p in planetList:
            self.pList.append(Planet(p))

        # Connection List
        conListEl = dom.getElementsByTagName("ConnectionList")[0]
        conList = conListEl.getElementsByTagName("connection")
        for c in conList:
            self.addConnection(c.childNodes[0].data)

        # Region List
        regionListEl = dom.getElementsByTagName("RegionList")[0]
        regionList = regionListEl.getElementsByTagName("Region")
        for r in regionList:
            self.rList.append(Region(r))
        self.updateRegions()
        
        return dom


# A class to store the game data for a planet.
class Planet:
    # Initializes all variables to default values.
    def __init__(self, el=None):
        if el is None:
            self.name = name
            self.idNum = int(idNum)
            self.numFleets = int(numFleets)
            self.owner = int(owner)
        else:
            self.loadXML(el)
    
    # Returns a string representation of this object.
    def __str__(self):
        return ("Planet " + str(self.idNum) + ", " + self.name +
                ". Owner: " + str(self.owner) + "; number of fleets: "
                + str(self.numFleets) + ".")

    # We'll... do these later
    def loadXML(self, el):
        self.name = el.getAttribute("name")
        self.idNum = int(el.getAttribute("idNum"))
        self.numFleets = int(el.getAttribute("numFleets"))
        self.owner = int(el.getAttribute("owner"))


# A class to store the game data for a region.
class Region:
    # Initializes all variables to default values.
    def __init__(self, el=None):
        self.members = set() # This gets initialized either way
        if el is None:
            self.name = ""
            self.idNum = 0
            self.value = 0
            self.owner = 0
        else:
            self.loadXML(el)

    # Returns a string representation of this object.
    def __str__(self):
        return ("Region " + str(self.idNum) + ", " + self.name +
                ". Owner: " + str(self.owner) + "; value: " + str(self.value) +
                ". List of members: " + str(self.members) + ".")

    def loadXML(self, el):
        self.name = el.getAttribute("name")
        self.idNum = int(el.getAttribute("idNum"))
        self.value = int(el.getAttribute("value"))
        self.owner = int(el.getAttribute("owner"))
        memberListEl = el.getElementsByTagName("memberList")[0]
        memberList = memberListEl.getElementsByTagName("member")
        for m in memberList:
            self.members.add(int(m.childNodes[0].data))


def main():
    global gs
    gs = Gamestate()
    gs.loadXML("TestGS.xml")
    print("main() finished.")

if __name__ == '__main__':
    main()
