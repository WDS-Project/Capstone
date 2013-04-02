# Contains all data and methods needed to
# represent a full game state.
# (For use with Mapmaker.py)
#
# Josh Polkinghorn

from xml.dom.minidom import getDOMImplementation
import sys

class Gamestate:
    # Sets all fields to default values.
    def __init__(self):
        self.playerList = [0]
        self.activePlayer = 0
        self.turnNumber = 0
        self.cycleNumber = 0
        self.pList = [None]
        self.rList = [None]
        self.cList = set()
        self.xSize = 0
        self.ySize = 0

    ### Methods ###
        
    ## Access methods ##

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

        # Adds the connection, checking to see if it was added successfully
        size = len(self.cList)
        self.cList.add(str(p1) + ',' + str(p2))
        return (size < len(self.cList))

    # Returns a string representation of the entire gamestate.
    def __str__(self):
        # First, the Gamestate itself.
        gs_str = ("Current Gamestate is as follows:\n" +
                  "--------------------------------\n")
        gs_str += ("Size: (" + str(self.xSize) + ", " +
                   str(self.ySize) + ").\n" +
                   "--------------------------------\n")

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
            
    ## Connection Methods ##
    
    # Adds a connection to the connection list.
    def addConnection(self, pair):
        start, end = pair.split(',')
        if start == end:
            print("Connections can't have the same start and end points.",
                  sys.stderr)
            return

        if start > end:
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
    def writeToXML(self):
        impl = getDOMImplementation()
        resultDoc = impl.createDocument(None, "Gamestate", None)

        # 1. Define the top-level element <Gamestate>.
        root = resultDoc.documentElement
        root.setAttribute("xSize", str(self.xSize))
        root.setAttribute("ySize", str(self.ySize))

        # 2. Define (and append) the <Players> element.
        playerListEl = resultDoc.createElement("Players")
        playerListEl.setAttribute("activePlayer", str(self.activePlayer))
        playerListEl.setAttribute("turnNumber", str(self.turnNumber))
        playerListEl.setAttribute("cycleNumber", str(self.cycleNumber))
        root.appendChild(playerListEl)
        
        # 3. Define the <PlanetList>, and let the Planets create themselves.
        pListEl = resultDoc.createElement("PlanetList")
        for p in self.pList:
            if p is None:
                continue
            pEl = resultDoc.createElement("Planet")
            p.writeToXML(pEl)
            pListEl.appendChild(pEl)
        root.appendChild(pListEl)

        # 4. Define the <ConnectionList> and populate it.
        cListEl = resultDoc.createElement("ConnectionList")
        for c in self.cList:
            conEl = resultDoc.createElement("connection")
            conText = resultDoc.createTextNode(c)
            conEl.appendChild(conText)
            cListEl.appendChild(conEl)
        root.appendChild(cListEl)

        # 5. Define the <RegionList>, and let the Regions create themselves.
        rListEl = resultDoc.createElement("RegionList")
        for r in self.rList:
            if r is None:
                continue
            rEl = resultDoc.createElement("Region")
            r.writeToXML(rEl, resultDoc)
            rListEl.appendChild(rEl)
        root.appendChild(rListEl)

        # 6. Cut, print, that's a wrap.
        return resultDoc

# A class to store the game data for a planet.
class Planet:
    # Initializes all variables to default values.
    def __init__(self, idNum, xPos, yPos, rad):
        self.idNum = int(idNum)
        self.name = "TEMP" + str(idNum)
        self.numFleets = 1
        self.owner = 1
        self.xPos = int(xPos)
        self.yPos = int(yPos)
        self.radius = int(rad)
        self.color = '#F00'
    
    # Returns a string representation of this object.
    def __str__(self):
        return ("Planet " + str(self.idNum) + ", " + self.name +
                ". Owner: " + str(self.owner) + "; number of fleets: "
                + str(self.numFleets) + ". Position: (" + str(self.xPos)
                + ", " + str(self.yPos) + "). Radius: " + str(self.radius) + ".")

    # Writes this planet to an XML document <Planet> node.
    def writeToXML(self, node):
        node.setAttribute("idNum", str(self.idNum))
        node.setAttribute("name", str(self.name))
        node.setAttribute("owner", str(self.owner))
        node.setAttribute("numFleets", str(self.numFleets))
        node.setAttribute("color", str(self.color))
        node.setAttribute("position", str(self.xPos)+","+str(self.yPos))
        node.setAttribute("radius", str(self.radius))
        return


# A class to store the game data for a region.
class Region:
    # Initializes all variables to default values.
    def __init__(self, members, idNum, value):
        self.name = "PMET" + str(idNum)
        self.idNum = int(idNum)
        self.value = int(value)
        self.owner = int(-1)
        self.members = set()
        for m in members:
            self.members.add(m)

    # Returns a string representation of this object.
    def __str__(self):
        return ("Region " + str(self.idNum) + ", " + self.name +
                ". Owner: " + str(self.owner) + "; value: " + str(self.value) +
                ". List of members: " + str(self.members) + ".")

    # Writes this planet to an XML document <RegionList> node.
    def writeToXML(self, node, doc):
        node.setAttribute("idNum", str(self.idNum))
        node.setAttribute("name", str(self.idNum))
        node.setAttribute("value", str(self.idNum))
        node.setAttribute("owner", str(self.idNum))
        node.setAttribute("color", str(self.idNum))
        
        mList = doc.createElement("memberList")
        node.appendChild(mList)
        for m in self.members:
            mEl = doc.createElement("member")
            mText = doc.createTextNode(str(m))
            mEl.appendChild(mText)
            mList.appendChild(mEl)
        return



