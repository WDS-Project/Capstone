# This AI script focuses on taking and holding regions.
# It took some doing, but it's pretty awesome.
#
# author: Josh Polkinghorn

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import AIHelpers
import random, queue, math

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
        #self.changeList = set()
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
        outerPlanets = set(AIHelpers.getOuterPlanets(gsLocal, self.idNum))
        critVal = math.floor(len(ownedPlanets) / 5) + 5 # Critical number of fleets
        # TODO possibly change to look at adjacent enemy-owned fleets as well?
        #print("Changes since last round: ")
        #print("--Lost planets "+ str(self.changeList.difference(ownedPlanets))+ \
        #      "; gained planets " + str(ownedPlanets.difference(self.changeList)))
        #print("critVal = " + str(critVal) + ", quota = " + str(quota), end='')
        #self.changeList = ownedPlanets


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

        # 3. Make deployments based in region priorities.
        # -----------------------------------------------
        # Creates a dictionary where each region ID maps to a set of
        # the planets in that region we could deploy to
        allRegions = dict.fromkeys(range(1, len(gsLocal.rList)))
        for p in outerPlanets:
            for r in gsLocal.rList:
                if r is not None and p.idNum in r.members:
                    if allRegions[r.idNum] is None:
                        allRegions[r.idNum] = set()
                    allRegions[r.idNum].add(p.idNum)

        # This gets a list of tuples like so (regionID, value) sorted by value
        orderedVals = sorted(self.totalVals.items(), key=lambda x: x[1], reverse=True)
        # Start with the highest valued region
        for val in orderedVals:
            toReinforce = allRegions[val[0]]
            if toReinforce is None: continue

            # Then reinforce all the planets in that region.
            for pID in toReinforce:
                planet = gsLocal.pList[pID]
                if planet.numFleets < critVal:
                    toDeploy = min((quota - deployCount), (critVal - planet.numFleets))
                    deployCount += toDeploy
                    planet.numFleets += toDeploy
                    move.addMove(0, planet.idNum, toDeploy)
                if deployCount == quota:
                    break
            if deployCount == quota:
                    break

        # 4. Make some attacks based on those fancy region values.
        # --------------------------------------------------------
        numAttacks = 0
        attackLimit = math.ceil(critVal / 2)
        orderedVals = sorted(self.totalVals.items(), key=lambda x: x[1], reverse=True)
        while numAttacks < attackLimit and len(orderedVals) > 0:
            # Pick the best region we don't already own
            for val in orderedVals:
                rID = val[0]
                if gsLocal.rList[rID].owner is not self.idNum and \
                   canAccessRegion(gsLocal, self.idNum, rID):
                    break
            targetRegion = gsLocal.rList[rID]
            orderedVals.remove((rID, self.totalVals[rID]))

            # Skip regions we own.
            if targetRegion.owner is self.idNum:
                continue                
            
            # Figure out how many planets in this region we can hit
            allAccessible = set()
            for pID in ownedPlanets:
                for con in self.allConnects[int(pID)]:
                    allAccessible.add(con)
            allAccessible.difference_update(ownedPlanets)
            # Now we have a list of all planets we can hit that we don't own.
            targets = targetRegion.members.intersection(allAccessible)
            # ...And now it's just planets in the region we can hit.

            # If there are no targets, we can't do anything more.
            if len(targets) <= 0:
                continue

            # Now we want to make some attacks.
            while len(targets) > 0 and numAttacks < attackLimit:
                # Assuming that all went okay, we need to pick a planet to attack.
                # For now, let's just pick one at random.
                targetPlanet = random.choice(list(targets))
                #print("Target planet:", gsLocal.pList[targetPlanet])

                # Then we can attack it with our biggest planet.
                source = None
                sourceFleets = 0
                for pID in self.allConnects[targetPlanet]:
                    if gsLocal.pList[pID].owner is self.idNum and \
                       sourceFleets < gsLocal.pList[pID].numFleets:
                        source = pID
                        sourceFleets = gsLocal.pList[pID].numFleets

                # If there are enough fleets on the planet, attack.
                if sourceFleets > 1:
                    # Add any leftover fleets
                    if deployCount < quota:
                        toDeploy = (quota - deployCount)
                        deployCount += toDeploy
                        sourceFleets += toDeploy
                        move.addMove(0, source, toDeploy)
                        
                    toSend = math.floor(sourceFleets * .80)
                    move.addMove(source, targetPlanet, toSend)
                    gsLocal.pList[source].numFleets -= toSend
                    numAttacks += 1
                # Regardless, we don't need to look at that planet again.
                targets.remove(targetPlanet)
                
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
        # SUBJECT TO CHANGE AT A MOMENT'S NOTICE
        
        # Setup the lists, if they aren't already.
        if self.staticVals is None:
            self.staticVals = [None]
            self.dynamicVals = [None]
            self.totalVals = {}
            for i in range(1, len(gs.rList)):
                self.staticVals.append(None)
                self.dynamicVals.append(0)
                self.totalVals[i] = 0

        # Assess the region values
        for i in range(1, len(gs.rList)):
            r = gs.rList[i]

            # This should only get built once.
            if self.staticVals[i] is None:
                # Static Value
                # ------------
                # Components:
                # > -n^2 for total external connection
                # > +(3*value) for the value of the region
                # > -1 for each member of the region
                self.staticVals[i] = 0
                self.staticVals[i] -= len(self.externalConnects[i]) ** 2
                self.staticVals[i] += r.value * 3 # Region value also factors in
                self.staticVals[i] -= len(r.members) # num planets in region
                self.staticVals[i] *= 2

            # Dynamic Value
            # -------------
            # Components:
            # > +3 for each self owned planet
            # > -3 for each enemy owned planet
            # > -1 for each enemy fleet that's a threat to this region
            # > * percentage of planet in the region we own squared
            # (This used to factor in how many fleets each player owned in the
            # region, but that produced behavior I didn't like.)
            self.dynamicVals[i] = 0
            ownedCount = 0
            for pID in r.members:
                if gs.pList[pID].owner is self.idNum:
                    ownedCount += 1
                    self.dynamicVals[i] += 3
                    #self.dynamicVals[i] += math.floor(gs.pList[pID].numFleets / 3)
                elif gs.pList[pID].owner is 0:
                    pass # ignore unowned planets
                else:
                    self.dynamicVals[i] -= 3
                    #self.dynamicVals[i] -= math.floor(gs.pList[pID].numFleets / 3)
            # Dynamic value changes depending on what percentage of the planets
            # in the region we own
            ownedPercent = ((ownedCount+1) / len(r.members)) ** 2
            self.dynamicVals[i] = math.floor(self.dynamicVals[i] * ownedPercent * 5)
            # It is also reduced by the number of fleets that could attack
            # our planets in this region
            self.dynamicVals[i] -= countHostileBorderFleets(gs, i, self.idNum)

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

                # Finally, add the move
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

# -------------------------------
# Helper Methods and other stuff!
# -------------------------------

# Returns the number of hostile fleets adjacent to planets owned
# by a player in a region. It's useful, trust me.
def countHostileBorderFleets(gs, regionID, playerID):
    # First, find which planets the player owns.
    region = gs.rList[regionID]
    owned = set()
    for m in region.members:
        if gs.pList[m].owner is playerID:
            owned.add(m)

    # Next, build a set of all planets connected to the owned set.
    borderPlanets = set()
    for pID in owned:
        for c in gs.getConnections(pID):
            borderPlanets.add(c)

    # Finally, sum all the fleets on those planets that are hostile.
    hostileCount = 0
    for borderID in borderPlanets:
        planet = gs.pList[int(borderID)]
        if planet.owner is not playerID:
            hostileCount += planet.numFleets

    return hostileCount

# There are an awful lot of functions like this that we need.
def canAccessRegion(gs, playerID, regionID):
    # First, find which planets the player owns.
    region = gs.rList[regionID]
    owned = AIHelpers.getOwnedPlanets(gs, playerID)

    # Next, build a set of all planets connected to the owned set.
    accessiblePlanets = set()
    for planetID in owned:
        for c in gs.getConnections(planetID):
            accessiblePlanets.add(int(c))

    # Finally, determine if we can access any of the planets
    # in the given region.
    return len(region.members.intersection(accessiblePlanets)) > 0

