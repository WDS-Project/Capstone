# Contains helper methods for AI scripts.
#
# WDS Capstone

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move

# Returns a list of planets owned by the given player
def getOwnedPlanets(gs, idNum):
    ownedPlanets = []
    for planet in gs.pList:
        if planet is None: continue
        if planet.owner is idNum:
            ownedPlanets.append(planet.idNum)
    return ownedPlanets

# Returns true if this planet has hostile neighbors.
def isOuterPlanet(gs, planet):
    connectIDs = gs.getConnections(planet.idNum)
    for con in connectIDs:
        if planet.owner is not gs.pList[int(con)].owner:
            return True
    else: # If the loop falls through, all planets are friendly.
        return False

# Returns a list of all outer planets owned by a player.
def getOuterPlanets(gs, playerID):
    resultList = []
    for planet in gs.pList:
        if planet is None: continue
        if planet.owner == playerID and isOuterPlanet(gs, planet):
            resultList.append(planet)
    return resultList
def getInnerPlanets(gs, playerID): # Same thing, but backwards
    resultList = []
    for planet in gs.pList:
        if planet is None: continue
        if planet.owner == playerID and not isOuterPlanet(gs, planet):
            resultList.append(planet)
    return resultList

# Returns a list of IDs of hostile planets connected to this one
def getHostileConnections(gs, planet):
    resultList = []
    connectIDs = gs.getConnections(planet.idNum)
    for con in connectIDs:
        if planet.owner is not gs.pList[int(con)].owner:
            resultList.append(con)
    return resultList

# Returns a list of all hostile connections for a given player
def getAllHostileConnections(gs, playerID):
    resultList = {}
    for planet in gs.pList:
        if planet is None: continue
        if planet.owner is not playerID:
            continue
        temp = getHostileConnections(gs, planet)
        if len(temp) > 0:
            resultList[planet.idNum] = temp
    return resultList

# Calculates the odds (in %) that the attackers will win
def calculateOdds(attFleets, defFleets):
    # HIGHLY preliminary. I'm attempting to approximate retreating, basically.
    attackOdds = (attFleets * (7/8)) / defFleets
    defendOdds = defFleets / (attFleets * (7/8))
    return attackOdds / (attackOdds + defendOdds)

# Adds a connection to the connection list.
def addConnection(cList, start, end):
    if start == end: return
    if int(start) > int(end):
        temp = start
        start = end
        end = temp
    cList.append(str(start) + "," + str(end))

# Returns a list of Planet objects owned by the given player
def getOwnedPlanets(gs, idNum):
    ownedPlanets = []
    for p in gs.pList:
        if p is None:
            continue
        if p.owner is idNum:
            ownedPlanets.append(p.idNum)
    return ownedPlanets

# returns a set of planet IDs that are outer in the region,
# that is, that connect to a planet outside it
# pass in a Gamestate and a Region object
def getOuterPlanetsInRegion(gs, region):
    outers = set()
    for p in region.members:
        for c in gs.getConnections(p):
            c = int(c)
            if c not in region.members:
                outers.add(p)
    return outers

def checkCards(cards):
    for i in range(1, 4):
        if cards[i] >= 3:
            cards[i] -= 3
            move.addMove(-1, i, 0)
            return True
        elif cards[i] == 2 and cards[0] >= 1:
            cards[i] -= 2
            cards[0] -= 1
            move.addMove(-1, i, 1)
            return True
        elif cards[i] == 1 and cards[0] >= 2:
            cards[i] -= 1
            cards[0] -= 2
            move.addMove(-1, i, 2)
            return True
    if cards[0] >= 3: # All wildcards
        cards[0] -= 3
        move.addMove(-1, 1, 3)
        return True

    # Otherwise, no pair is possible.
    return False
        
