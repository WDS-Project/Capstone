# This AI script focuses on taking and holding regions.
#
# author: Josh Polkinghorn

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import AIHelpers
import random

class RegionAI:
    def __init__(self, idNum):
        # Note that "None" is different from "[None]".
        # "None" => uninitialized
        # "[None]" => initialized, but not filled in
        self.staticVals = None
        self.dynamicVals = None
        self.totalVals = None
        self.externalConnects = None
        self.regionConnects = None
        self.idNum = idNum
        return
    
    # Builds a move based on a Gamestate
    def getMove(self, gs, state, cards):
        gsLocal = gs.copy() # Leave external GS alone
        if self.externalConnects is None:
            self.calculateRegionConnects(gsLocal)
        rVals = self.evaluateRegions(gsLocal)
        if state == 1: # i.e. we're choosing planets
            #print("\nInside RegionAI:\n"+str(gs))
            return self.choosePlanet(gsLocal)

        # Otherwise, build & return a normal move.
        result = Move(self.idNum)
        self.generateDeployments(gsLocal, result, cards)
        self.generateMoves(gsLocal, result)
        return result

    # Chooses a planet to own.
    def choosePlanet(self, gs):
        # First, chooses the best region to get another planet in.
        bestVal = None
        bestIdx = None
        for i in self.totalVals:
            if gs.rList[i].owner is 0 and \
               (bestVal is None or self.totalVals[i] > bestVal):
                # Now check if there are open slots.
                hasOpenSlot = False
                for p in gs.rList[i].members:
                    if gs.pList[p].owner is 0:
                        hasOpenSlot = True
                if hasOpenSlot: # Store this region only if there's room in it
                    bestVal = self.totalVals[i]
                    bestIdx = i

        # Next, pick a planet in that region to choose.
        planetChoice = -1
        for t in gs.rList[bestIdx].members:
            if gs.pList[t].owner is 0:
                planetChoice = t # NOT FANCY PLZ FIX

        # That's our choice! Cut, print, that's a wrap.
        result = Move(self.idNum)
        result.addMove(0, 0, planetChoice)
        return result

    # Generates a set of attacks seeking to control regions.
    def generateMoves(self, gsLocal, move):
        # TODO implement
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
        return

    # Deploys fleets to planets, prioritizing controlling regions
    # and holding regions already owned.
    def generateDeployments(self, gsLocal, move, cards):
        # TODO implement
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

    def calculateRegionConnects(self, gs):
        self.externalConnects = [None]
        for i in range(1, len(gs.rList)):
            self.externalConnects.append(set())
            r = gs.rList[i]
            allCons = []
            for m in r.members:
                allCons.extend(gs.getConnections(m))
            uniqueCons = set(allCons)
            # Initially, externalConnects is all connects of a region
            for con in uniqueCons:
                self.externalConnects[i].add(int(con))

        # Now we figure out which regions are connected
        self.regionConnects = [None]
        for i in range(1, len(gs.rList)):
            self.regionConnects.append([None])
            for j in range(1, len(gs.rList)):
                overlap = self.externalConnects[i].intersection(gs.rList[j].members)
                if len(overlap) > 0:
                    self.regionConnects[i].append(True)
                else:
                    self.regionConnects[i].append(False)

        # Finally, strip out internal connections from externalConnects
        for i in range(1, len(gs.rList)):
            self.externalConnects[i].difference_update(gs.rList[i].members)

    # Assigns a score to each region based on size, value, number of
    # owned planets, and other things I think up
    def evaluateRegions(self, gs):
        # Setup the lists, if they aren't already.
        if self.staticVals is None:
            self.staticVals = [None]
            self.dynamicVals = [None]
            self.totalVals = {}
            for i in range(1, len(gs.rList)):
                self.staticVals.append(None)
                self.dynamicVals.append(0)
                self.totalVals[i] = 0

        # Reassess the region values
        for i in range(1, len(gs.rList)):
            r = gs.rList[i]

            # This should only get built once.
            if self.staticVals[i] is None:
                # Static Value
                # ------------
                # Components:
                # > -3 for each external connection
                # > +value for the value of the region
                # > -1 for each member of the region
                self.staticVals[i] = 0
                self.staticVals[i] -= len(self.regionConnects[i]) * 3
                self.staticVals[i] += r.value # Region value also factors in
                self.staticVals[i] -= len(r.members) # num planets in region

            # Dynamic Value
            # -------------
            # Components:
            # > +1 for friendly fleets in the region
            # > -1 for enemy fleets in the region
            # > +3 for each self owned planet
            # > -3 for each enemy owned planet
            self.dynamicVals[i] = 0
            for pID in r.members:
                if gs.pList[pID].owner is self.idNum:
                    self.dynamicVals[i] += 3
                    self.dynamicVals[i] += gs.pList[pID].numFleets
                elif gs.pList[pID].owner is 0:
                    pass # ignore unowned planets
                else:
                    self.dynamicVals[i] -= 3
                    self.dynamicVals[i] -= gs.pList[pID].numFleets

            # Total Value
            # -----------
            self.totalVals[i] = self.staticVals[i] + self.dynamicVals[i]
            
        #self.printVals()
        return

    # Prints the static, dynamic, and total region values
    def printVals(self):
        print("Region Values: [static, dynamic, total]")
        print("---------------------------------------")
        for i in range(1, len(self.staticVals)):
            print("Region "+str(i)+": ["+str(self.staticVals[i])
                  + ", "+str(self.dynamicVals[i]) + ", "
                  + str(self.totalVals[i]) + "]")


