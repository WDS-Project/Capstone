# This AI script locates all possible moves and selects
# one of them at random.
#
# WDS Project

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import random

# Builds a move for a given player based on a Gamestate
def getMove(gs, idNum):
    result = Move(idNum)
    generateDeployments(gs, result)
    generateMoves(gs, result)
    return result

# Generates a set of random attacks based on owned planets
def generateMoves(gs, move):
    ownedPlanets = getOwnedPlanets(gs, move.playerID)

    # Gets all possible moves
    connections = []
    for p in ownedPlanets: # for each owned planet...
        pConnects = gs.getConnections(p) # get all connections
        for conn in pConnects:
            connections.append(str(p) + "," + str(conn)) 

    moveCount = 2#(len(ownedPlanets) / 3) + 1 # minimum of one move
    while (moveCount > 0 and len(connections) > 0):
        temp = random.randint(0, len(connections)-1)
        start, end = connections[temp].split(",") # gets a random connection
        sourceID = int(start)
        destID = int(end)

        if (sourceID not in ownedPlanets):
            connections.pop(temp)
            continue # only make one move per planet

        # generates a random number of fleets, 1 <= n < total fleets available
        numFleets = random.randint(1, gs.pList[sourceID].numFleets - 1)
        move.addMove(sourceID, destID, numFleets)
        moveCount -= 1
        ownedPlanets.remove(sourceID)
    
    return

# Generates a set of random deployments based on owned planets
def generateDeployments(gs, move):
    ownedPlanets = getOwnedPlanets(gs, move.playerID)
    deployCount = gs.getPlayerQuota(move.playerID)
    
    while (deployCount > 0 and len(ownedPlanets) > 0):
        temp = random.randint(0, len(ownedPlanets)-1)
        destID = ownedPlanets[temp] # a random owned planet
        numFleets = random.randint(1, deployCount) # a random number of fleets
        gs.pList[destID].numFleets += numFleets # update the local Gamestate
        move.addMove(0, destID, numFleets)
        deployCount -= numFleets
        ownedPlanets.remove(destID) # only one deploy per planet (at most)
        
    return

# Returns a list of planets owned by the given player
def getOwnedPlanets(gs, idNum):
    ownedPlanets = []
    for p in gs.pList:
        if p is None:
            continue
        if p.owner is idNum:
            ownedPlanets.append(p.idNum)
    return ownedPlanets
