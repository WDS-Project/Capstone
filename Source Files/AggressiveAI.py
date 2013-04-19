# This AI script attacks as aggresively as possible,
# but with no real plan.
#
# WDS Project

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import random, math
import AIHelpers

class AggressiveAI:
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
        self.generateDeployments(gsLocal, result, cards)
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
        # Gets all vaguely useful moves
        ownedPlanets = AIHelpers.getOwnedPlanets(gsLocal, self.idNum)
        outerPlanets = AIHelpers.getOuterPlanets(gsLocal, self.idNum)
        connections = AIHelpers.getAllHostileConnections(gsLocal, self.idNum)

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

            # Sends 75%(ish) of the available fleets
            numFleets = math.ceil(source.numFleets * .75) - 1
            move.addMove(source.idNum, dest.idNum, numFleets)
            source.numFleets -= numFleets
            moveCount -= 1
            connections.pop(start)

        return

    # Generates a random deployment to an outer planet
    def generateDeployments(self, gsLocal, move, cards):
        outerPlanets = AIHelpers.getOuterPlanets(gsLocal, self.idNum)
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
