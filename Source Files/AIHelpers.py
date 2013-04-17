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

# Checks to see if cards contains a valid turnin.
def checkCards(cards):
    # Check case for all the same
    for i in range(len(cards)):
        if cards[i] >= 3:
            return i

    # Check for all different
    if cards[0] >= 1 and cards[1] >= 1 and cards[2] >= 1:
        return 3

    # Otherwise, no pair is possible.
    return -1

# Adds a move to reflect turning in cards.
def turninCards(cards, move, turninType):
    if turninType < 3:
        cards[turninType] -= 3
        move.addMove(-1, 0, turninType)

    elif turninType == 3:
        cards[0] -= 1
        cards[1] -= 1
        cards[2] -= 1
        move.addMove(-1, 0, 3)

    else: # Shouldn't get here
        raise Exception("Error: invalid card turnin type.")
# Returns the value of a given turnin
def getTurninValue(turninCount):
    if (turninCount < 6):
        return (2 * turninCount) + 5;
    else:
        return 15 + turninCount;
    
