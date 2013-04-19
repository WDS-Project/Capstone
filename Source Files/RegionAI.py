# This AI script focuses on taking and holding regions.
#
# author: Josh Polkinghorn

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import AIHelpers
import random, queue, math

# Problems:
# - Submitting deploys with fleets = 0


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
        self.allConnects = None
        self.idNum = int(idNum)
        self.changeList = set()
        return
    
    # Builds a move based on a Gamestate
    def getMove(self, gs, state, cards):
        gsLocal = gs.copy() # Leave external GS alone

        # Calculate connections only if we haven't already.
        if self.externalConnects is None:
            self.calculateRegionConnects(gsLocal)
        rVals = self.evaluateRegions(gsLocal)

        # Now that we know region values, we can make moves.
        if state == 1: # i.e. we're choosing planets
            return self.choosePlanet(gsLocal)

        # Otherwise, build & return a normal move.
        result = Move(self.idNum)
        self.generateMoves(gsLocal, result, cards)
        return result

    # Chooses a planet to own.
    def choosePlanet(self, gs):
        # TODO This might actually be causing problems, basically because
        # if you're only playing against 1 other player and he tries to take
        # Asia, he does it unopposed. Figuring out how to block other players'
        # strategies sounds incredibly complicated, however.
        
        # First, chooses the best region to get another planet in.
        bestVal = None
        bestIdx = None
        for i in self.totalVals:
            if gs.rList[i].owner is 0 and \
               (bestVal is None or self.totalVals[i] > bestVal):
                # Now check if there are open slots.
                hasOpenSlot = (min(gs.pList[p].owner for p in gs.rList[i].members) is 0)
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
        self.changeList = set(AIHelpers.getOwnedPlanets(gs, self.idNum))
        return result

    # Generates a set of attacks seeking to control regions.
    def generateMoves(self, gsLocal, move, cards):
        # 1. Figure out how many fleets we have to work with.
        # ---------------------------------------------------
        quota = int(gsLocal.getPlayerQuota(self.idNum))
        deployCount = 0
        ownedPlanets = set(AIHelpers.getOwnedPlanets(gsLocal, self.idNum))
        outerPlanets = AIHelpers.getOuterPlanets(gsLocal, self.idNum)
        critVal = math.floor(len(ownedPlanets) / 5) + 5 # Critical number of fleets
        # TODO possibly change to look at adjacent enemy-owned fleets as well?
        #print("Changes since last round: ")
        #print("Lost planets "+ str(self.changeList.difference(ownedPlanets))+ \
        #      "; gained planets " + str(ownedPlanets.difference(self.changeList)))
        #for p in self.changeList.difference(ownedPlanets):
        #    print(str(gsLocal.pList[p]))
        #print("ownedPlanets: " + str(list(ownedPlanets)))
        #print("self.changeList: " + str(list(self.changeList)) + " (this should be ownedPlanets for the last round)")
        print("critVal = " + str(critVal) + ", quota = " + str(quota), end='')

        
        self.changeList = ownedPlanets


        # See if we can turn in some cards
        chk = AIHelpers.checkCards(cards)
        if chk > -1:
            AIHelpers.turninCards(cards, move, chk)
            quota += AIHelpers.getTurninValue(gsLocal.turninCount)
            gsLocal.turninCount += 1

        
        # 2. Move fleets away from inner planets.
        # ---------------------------------------
        self.vacateInnerPlanets(gsLocal, move)
        # TODO Is there more to do here? Do we want to be more deliberate
        # about where we move fleets to?

        # 3. Make sure all the regions we hold are defended.
        # --------------------------------------------------
        print(" ||| Regions owned: ", end='')
        for r in gsLocal.rList:
            if r is None or r.owner is not self.idNum:
                continue # ignore regions we don't control
            print(str(r.idNum) + " ", end='')
            regionOuters = AIHelpers.getOuterPlanetsInRegion(gsLocal, r)
            regionOuters = regionOuters.intersection(outerPlanets)
            for rIdx in regionOuters:
                rPlanet = gsLocal.pList[rIdx]
                if rPlanet.numFleets < critVal:
                    toDeploy = min((quota - deployCount), (critVal - rPlanet.numFleets))
                    deployCount += toDeploy
                    rPlanet.numFleets += toDeploy
                    move.addMove(0, rPlanet.idNum, toDeploy)
                if deployCount == quota:
                    break
            if deployCount == quota:
                    break
        print()
        #gsLocal.printShort()
        self.printVals()

        # 4. Make some attacks.
        # ---------------------
        numAttacks = 0
        threshold = critVal + 2
        while numAttacks is 0 and threshold > 3:
            for oPlanet in outerPlanets: # Pick an outer planet...
                if oPlanet.numFleets > threshold: # With enough fleets...
                    for con in self.allConnects[oPlanet.idNum]: # Pick a target...
                        if gsLocal.pList[con].owner is not self.idNum: # That's hostile...

                            # If we have deployments left, use them
                            if deployCount < quota:
                                oPlanet.numFleets += (quota - deployCount)
                                move.addMove(0, oPlanet.idNum, quota - deployCount)
                                deployCount = quota

                            # Then just attack whatever.
                            # TODO make actually deliberate
                            numFleets = math.floor(oPlanet.numFleets / 2)
                            #print("Making move: source planet = {"+ str(oPlanet)+"} dest planet = {"+str(gsLocal.pList[con])+"}; numFleets = "+str(numFleets))
                            move.addMove(oPlanet.idNum, gsLocal.pList[con].idNum, numFleets)

                            # This ensures that we only count moves on the first try
                            if threshold == critVal+2:
                                numAttacks += 1
                            else:
                                numAttacks = critVal # i.e. we're done
                            break # done with this planet
                if numAttacks > (critVal / 2):
                    return
            # We'd really like to make an attack so that we can get a card.
            # If we haven't made one already, lower our standards and try again.
            if numAttacks is 0:
                threshold -= 1
            # It's possible that we won't get any attacks, even with this
            # system. If that happens, it's because we have very few fleets to
            # spare on outer planets, and there's nothing we can do about
            # that; however, this should never happen because of deployments.

        # Let's try another approach. Maybe one that, y'know, actually uses
        # those fancy region values we computed earlier?

        
        return

    # Determines which regions are connected to each other.
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

        # And because I need it, figure out all connections for all planets
        self.allConnects = {}
        for p in gs.pList:
            if p is None: continue
            consStr = gs.getConnections(p.idNum)
            cons = set()
            for c in consStr:
                cons.add(int(c))
            self.allConnects[p.idNum] = cons

        return

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
                # > -2 for each external connection
                # > +(2*value) for the value of the region
                # > -1 for each member of the region
                self.staticVals[i] = 0
                self.staticVals[i] -= len(self.regionConnects[i]) * 2
                self.staticVals[i] += r.value * 2 # Region value also factors in
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

    # Moves fleets toward the front line. Note that this changes source fleets,
    # but not dest fleets; it is therefore consistent with the GUI's behavior.
    def vacateInnerPlanets(self, gs, move):
        # Similar to AIHelpers.getOuterPlanets, but does both at once.
        innerPlanets = set()
        outerPlanets = set()
        for planet in gs.pList:
            if (planet is not None) and (planet.owner is self.idNum):
                if AIHelpers.isOuterPlanet(gs, planet):
                    outerPlanets.add(planet)
                else:
                    innerPlanets.add(planet)

        # If there are no inner planets, we're done here
        if len(innerPlanets) < 1:
            return

        # Otherwise, it's time for fancy calculations.
        dists = [None]
        for i in range(1, len(gs.pList)):
            dists.append(None)
        q = queue.Queue()
        outers = AIHelpers.getOuterPlanets(gs, self.idNum)
        for o in outers: # Seed the queue
            dists[o.idNum] = 0 # distances from any outer planet
            q.put(o.idNum)

        # This searches each planet in turn, updates the connections
        # of that planet according to that planet's distance, and
        # puts any planets that haven't been checked already in the queue.
        while not q.empty():
            nextP = q.get()
            for c in self.allConnects[nextP]:
                if gs.pList[c].owner is not self.idNum:
                    continue
                if dists[c] is None: # i.e. not yet checked
                    q.put(c)
                    dists[c] = dists[nextP] + 1
                else:
                    dists[c] = min(dists[c], dists[nextP]+1)

        # Loop through non-frontline planets...
        for planet in innerPlanets:
            if planet.numFleets > 1: # ...with extra fleets...
                # ... And move those fleets toward outer planets.
                minDist = dists[planet.idNum]
                minIdx = planet.idNum
                for c in self.allConnects[planet.idNum]:
                    if dists[c] < minDist:
                        minDist = dists[c]
                        minIdx = c

                # BLUH DONE
                if minIdx is not None:
                    move.addMove(planet.idNum, minIdx, planet.numFleets - 1)
                planet.numFleets = 1
                
        return
                

    # Prints the static, dynamic, and total region values
    def printVals(self):
        print("Region Values: [static, dynamic, total]")
        print("---------------------------------------")
        for i in range(1, len(self.staticVals)):
            print("Region "+str(i)+": ["+str(self.staticVals[i])
                  + ", "+str(self.dynamicVals[i]) + ", "
                  + str(self.totalVals[i]) + "]")


