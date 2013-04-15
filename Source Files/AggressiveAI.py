# This AI script attacks as aggresively as possible,
# but with no real plan.
#
# WDS Project

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import random
import AIHelpers

class AggressiveAI:
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
        self.generateDeployments(gsLocal, result, cards)
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

    # Generates a random deployment to an outer planet
    def generateDeployments(self, gsLocal, move, cards):
        outerPlanets = AIHelpers.getOuterPlanets(gsLocal, move.playerID)
        if len(outerPlanets) < 1: return
        deployCount = gsLocal.getPlayerQuota(move.playerID)

        # See if we can turn in some cards
        chk = AIHelpers.checkCards(cards)
        if chk > -1:
            AIHelpers.turninCards(cards, move, chk)
            deployCount += AIHelpers.getTurninValue(gsLocal.turninCount)
            gsLocal.turninCount += 1

        # Make the move
        dest = random.choice(outerPlanets)
        dest.numFleets += deployCount # update the local Gamestate
        move.addMove(0, dest.idNum, deployCount)
        return
