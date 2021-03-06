# This AI script locates all possible moves and selects
# one of them at random.
#
# WDS Project

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import AIHelpers
import random

class RandomAI:
    def __init__(self, idNum):
        # Random-family AIs don't really need to remember anything.
        # They're kinda terrible.
        self.idNum = int(idNum)
        return
    
    # Builds a move for a given player based on a Gamestate
    def getMove(self, gs, state, cards):
        gsLocal = gs.copy() # don't change the external gs
        if (state == 1): # i.e. choosing
            return self.choosePlanet(gsLocal)
        # Otherwise, just return a move.
        result = Move(self.idNum)
        self.generateDeployments(gsLocal, result)
        self.generateMoves(gsLocal, result)
        return result

    # Chooses a random unowned planet.
    def choosePlanet(self, gs):
        result = Move(self.idNum)
        unownedPlanets = []
        for p in gs.pList:
            if p is None: continue
            if p.owner is 0:
                unownedPlanets.append(p.idNum)
            
        target = random.choice(unownedPlanets)
        result.addMove(0, 0, target)
        return result

    # Generates a set of random attacks based on owned planets
    def generateMoves(self, gsLocal, move):
        ownedPlanets = AIHelpers.getOwnedPlanets(gsLocal, self.idNum)

        # Gets all possible moves
        connections = []
        for p in ownedPlanets: # for each owned planet...
            pConnects = gsLocal.getConnections(p) # get all connections
            for conn in pConnects:
                connections.append(str(p) + "," + str(conn)) 

        moveCount = (len(ownedPlanets) / 3) + 1 # minimum of one move
        while (moveCount > 0 and len(connections) > 0):
            temp = random.randint(0, len(connections)-1)
            start, end = connections[temp].split(",") # gets a random connection
            sourceID = int(start)
            destID = int(end)

            if (sourceID not in ownedPlanets):
                connections.pop(temp)
                continue # only make one move per planet

            # generates a random number of fleets, 1 <= n < total fleets available
            if(gsLocal.pList[sourceID].numFleets == 1):
                connections.pop(temp)
                continue
            randFleets = random.randint(1, gsLocal.pList[sourceID].numFleets - 1)
            move.addMove(sourceID, destID, randFleets)
            gsLocal.pList[sourceID].numFleets -= randFleets
            moveCount -= 1
            ownedPlanets.remove(sourceID)
        
        return

    # Generates a set of random deployments based on owned planets
    def generateDeployments(self, gsLocal, move):
        ownedPlanets = AIHelpers.getOwnedPlanets(gsLocal, self.idNum)
        deployCount = gsLocal.getPlayerQuota(self.idNum)
        
        while (deployCount > 0 and len(ownedPlanets) > 0):
            temp = random.randint(0, len(ownedPlanets)-1)
            destID = ownedPlanets[temp] # a random owned planet
            numFleets = random.randint(1, deployCount) # a random number of fleets
            gsLocal.pList[destID].numFleets += numFleets # update the local Gamestate
            move.addMove(0, destID, numFleets)
            deployCount -= numFleets
            ownedPlanets.remove(destID) # only one deploy per planet (at most)
            
        return


