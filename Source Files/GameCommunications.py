# Contains methods and stuff for communications
# between the client and the server.
#
# Josh Polkinghorn

from Gamestate import Gamestate, Planet, Region
from xml.dom.minidom import parse, parseString
import sys

# Example Gamechange XML:
# b'<?xml version="1.0" encoding="UTF-8"?><GameChange>
# <Players activePlayer="1" cycleNumber="1" turnNumber="1"/>
# <Planets><Planet idNum="1" numFleets="4" owner="1"/>
# <Planet idNum="2" numFleets="7" owner="1"/>
# <Planet idNum="4" numFleets="1" owner="2"/>
# </Planets></GameChange>'

class Gamechange:
    def __init__(self):
        self.activePlayer = 0
        self.turnNumber = 0
        self.cycleNumber = 0
        self.changes = []
        return

    def __str__(self):
        result = ("Gamechange:\n" +
                  "-----------\n")
        result += ("Turn Number: " + str(self.turnNumber) + ", Cycle Number: " +
                   str(self.cycleNumber) + "\nActive Player: " +
                   str(self.activePlayer) +"\n")
        result += ("\nList of changes:\n" +
                   "----------------\n")
        for change in self.changes:
            result += str(change) + "\n"

        return result
                   

    def loadXML(self, xmlString):
        dom = parseString(xmlString)
    
        # Player data
        players = dom.getElementsByTagName("Players")[0]
        self.activePlayer = int(players.getAttribute("activePlayer"))
        self.turnNumber = int(players.getAttribute("turnNumber"))
        self.cycleNumber = int(players.getAttribute("cycleNumber"))
        
        # Change list
        planetListEl = dom.getElementsByTagName("Planets")[0]
        changeList = planetListEl.getElementsByTagName("Planet")
        for change in changeList:
            idNum = int(change.getAttribute("idNum"))
            owner = int(change.getAttribute("owner"))
            numFleets = int(change.getAttribute("numFleets"))
            self.changes.append( (idNum, owner, numFleets) )
        
        return dom

class Move:
    def __init__(self, playerID):
        self.playerID = int(playerID)
        self.moves = []
        self.currentMiniMove = 0

    def __str__(self):
        result = str(self.playerID) + "/"
        for m in self.moves:
            result += str(m[0])+":"+str(m[1])+":"+str(m[2])+"/"
        return result

    def addMove(self, sourceID, destID, numFleets):
        self.moves.append( (sourceID, destID, numFleets) )

    def hasNext(self):
        if(self.currentMiniMove >= len(self.moves)):
            return False
        return True

    def next(self):
        self.currentMiniMove += 1
        return self.moves[self.currentMiniMove-1]
