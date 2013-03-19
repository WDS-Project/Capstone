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


