# This AI script locates all possible moves and selects
# one of them at random.
#
# WDS Project

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import random
import AIHelpers

class RandomAIBetter:
    def __init__(self):
        # Random-family AIs don't really need to remember anything.
        # They're kinda terrible.
        return
    
    # Builds a move for a given player based on a Gamestate
    def getMove(self, gs, idNum, state, cards):
        if (state == 1): # i.e. choosing
            return self.choosePlanet(gs, idNum)
        # Otherwise, just return a move.
        gsLocal = gs.copy() # makes a local copy so we don't change the external gs
        result = Move(idNum)
        self.generateDeployments(gsLocal, result)
        self.generateMoves(gsLocal, result)
        return result

    # Chooses a random unowned planet.
    def choosePlanet(self, gs, idNum):
        result = Move(idNum)
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
        #print("Generating random moves in RandomAIBetter...")
        #print("GSLocal: "+str(gsLocal))
        # I really hope this works better
        ownedPlanets = AIHelpers.getOwnedPlanets(gsLocal, move.playerID)
        outerPlanets = AIHelpers.getOuterPlanets(gsLocal, move.playerID)
        #$print("List of outer planets:")
        #$for p in outerPlanets:
        #   print("--> "+str(p))

        # Gets all vaguely useful moves
        connections = []
        #for p in outerPlanets: # for each outer planet...
            # get all hostile connections
        #    pConnects = AIHelpers.getHostileConnections(gsLocal, p)
        #    for conn in pConnects:
        #        AIHelpers.addConnection(connections, p.idNum, conn)
        connections = AIHelpers.getAllHostileConnections(gsLocal, move.playerID)

        #print("Connections to be searched: "+str(connections))
        moveCount = (len(ownedPlanets) / 3) + 1 # minimum of one move
        while (moveCount > 0 and len(connections) > 0):
            start = int(random.choice(list(connections))) # random source planet ID
            end = int(random.choice(connections[start])) # random hostile target
            source = gsLocal.pList[start]
            dest = gsLocal.pList[end]

            # Checks if this is a valid source planet
            if (source not in outerPlanets):
                #print(str(source.idNum)+" is not an outer planet. Remove & retry...")
                connections.pop(start)
                continue # only make one move per planet
            if(source.numFleets == 1):
                connections.pop(start)
                #print("Not enough fleets available on planet "+str(source.idNum)+". Remove & retry...")
                continue

            # generates a random number of fleets, 1 <= n < total fleets available
            randFleets = random.randint(1, source.numFleets - 1)
            move.addMove(source.idNum, dest.idNum, randFleets)
            source.numFleets -= randFleets
            moveCount -= 1
            connections.pop(start)
            #print("Added a move: ",str(start),str(end),str(randFleets))

        #print("Done. Result: " + str(move))
        return

    # Generates a set of random deployments based on outer planets
    def generateDeployments(self, gsLocal, move):
        outerPlanets = AIHelpers.getOuterPlanets(gsLocal, move.playerID)
        deployCount = gsLocal.getPlayerQuota(move.playerID)
        
        while (deployCount > 0 and len(outerPlanets) > 0):
            dest = random.choice(outerPlanets) # a random outer planet
            numFleets = random.randint(1, deployCount) # a random number of fleets
            dest.numFleets += numFleets # update the local Gamestate
            move.addMove(0, dest.idNum, numFleets)
            deployCount -= numFleets
            outerPlanets.remove(dest) # only one deploy per planet (at most)
            
        return
