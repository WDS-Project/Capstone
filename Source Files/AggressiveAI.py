# This AI script attacks as aggresively as possible,
# but with no real plan.
#
# WDS Project

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import random
import AIHelpers

# Builds a move for a given player based on a Gamestate
def getMove(gs, idNum):
    gsLocal = gs.copy() # makes a local copy so we don't change the external gs
    result = Move(idNum)
    generateDeployments(gsLocal, result)
    generateMoves(gsLocal, result)
    return result

# Generates a set of random attacks based on owned planets
def generateMoves(gsLocal, move):
    # Gets all vaguely useful moves
    ownedPlanets = AIHelpers.getOwnedPlanets(gsLocal, move.playerID)
    outerPlanets = AIHelpers.getOuterPlanets(gsLocal, move.playerID)
    connections = AIHelpers.getAllHostileConnections(gsLocal, move.playerID)

    moveCount = (len(ownedPlanets) / 3) + 1 # minimum of one move
    while (moveCount > 0 and len(connections) > 0):
        start = int(random.choice(list(connections))) # random source planet ID
        end = int(random.choice(connections[start])) # random hostile target
        source = gsLocal.pList[start]
        dest = gsLocal.pList[end]

        # Checks if this is a valid source planet
        if (source not in outerPlanets):
            connections.pop(start)
            continue # only make one move per planet
        if(source.numFleets == 1):
            connections.pop(start)
            continue

        move.addMove(source.idNum, dest.idNum, source.numFleets - 1)
        source.numFleets = 1
        moveCount -= 1
        connections.pop(start)

    return

# Generates a random deployments to an outer planet
def generateDeployments(gsLocal, move):
    outerPlanets = AIHelpers.getOuterPlanets(gsLocal, move.playerID)
    deployCount = gsLocal.getPlayerQuota(move.playerID)
    dest.numFleets += deployCount # update the local Gamestate
    move.addMove(0, dest.idNum, deployCount)
    return
