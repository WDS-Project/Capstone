# This AI script locates all possible moves and selects
# one of them at random.
#
# WDS Project

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import random

def getMove(gs, idNum):
    result = Move(idNum)
    generateDeployments(gs, result)
    generateMoves(gs, result)
    return result

def generateMoves(gs, move):
    ownedPlanets = getOwnedPlanets(gs, move.playerID)

    # Gets all possible moves
    connections = set()
    for p in ownedPlanets:
        True
    return

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

def getOwnedPlanets(gs, idNum):
    ownedPlanets = []
    for p in gs.pList:
        if p is None:
            continue
        if p.owner is idNum:
            ownedPlanets.append(p.idNum)
    return ownedPlanets

def main():
    global gs
    gs = Gamestate()
    gs.loadXML("TestGS.xml")
    idNum = 1
    print(getMove(gs, idNum))

if __name__ == '__main__':
    main()
