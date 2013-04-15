###NEW AI
#Map planets to values
#1. Outer planets in region [with connections]
#2. Planets with more [hostile] connections
#3. Planets in regions with high values
# Prioritize my own planets and enemy planets
# Don't attack if you can't win
# Attack if odds are greater than 1/2
# Move fleets to higher priority planets

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import random
import AIHelpers
import math

class PrioritizingAI:
    
    def __init__(self):
        self.allPlanets = {}
        self.myPlanets = {}
        self.theirPlanets = {}
        self.moveCount = 0

    
    # Builds a move for a given player based on a Gamestate
    def getMove(self, gs, idNum, state, cards):
        gsLocal = gs.copy()
        if(state == 1):
            self.prioritizeAllPlanets(gsLocal)
            return self.choosePlanet(gsLocal, idNum)
        result = Move(idNum)
        self.prioritizeMyPlanets(gsLocal, int(idNum))
        self.prioritizeTheirPlanets(gsLocal, int(idNum))
        result = self.generateDeployments(gsLocal, result)
        result = self.generateAttacks(gsLocal, result)
        self.moveCount += 1
        return result

    ##Choosing planets:
    # Regions with higher values
    # Inner planets in regions, because they are easier to hold
    # planets in regions with fewer outside connections
    # planets not connected to ones I already have, to get a good random sampling
    def prioritizeAllPlanets(self, myGS):
        #initialize all planets to 0 value
        for p in myGS.pList:
            if p is not None:
                self.allPlanets[p.idNum] = 0
        
        #regions with higher values
        for r in myGS.rList:
            if r is not None:
                for p in r.members:
                    self.allPlanets[p] += r.value

        #regions with few outside connections
        regions = {}
        for r in myGS.rList:
            if r is not None:
                regions[r] = AIHelpers.getOuterPlanetsInRegion(myGS, r)
        while(len(regions) > 0):
            lowestKey = min(regions, key = regions.get)
            for p in lowestKey.members:
                self.allPlanets[p] += len(regions)*2
            regions.pop(lowestKey)

    #choose the planet with the highest value
    def choosePlanet(self, myGS, playerID):
        move = Move(playerID)
        newDict = dict()
        for p in self.allPlanets.keys():
            newDict[p] = self.allPlanets[p]
        while(len(newDict) > 0):
            planet = max(newDict, key = newDict.get)
            if(int(myGS.pList[planet].owner) == 0):
                move.addMove(0,0,planet)
                break
            newDict.pop(planet)
        return move

    ##reinforcements sent from higher priority to lower, but
    #it didn't work very well.

    def prioritizeMyPlanets(self, myGS, playerID):
        self.myPlanets = dict()
        # map planetIDs to prioritized values
        for p in AIHelpers.getOwnedPlanets(myGS, playerID):
            if myGS.pList[p].owner == playerID:
                self.myPlanets[p] = 0

        # prioritize outer planets in regions
        for r in myGS.rList:
            if r is not None:
                for p in AIHelpers.getOuterPlanetsInRegion(myGS, r):
                    if p in self.myPlanets.keys():
                        self.myPlanets[p] += 1
        
        # prioritize planets with more hostile connections
        # for key, value in myPlanets.iteritems():
        for p in self.myPlanets.keys():
            self.myPlanets[p] += len(AIHelpers.getHostileConnections(myGS,myGS.pList[p]))*2

        # prioritize planets in regions with higher values
        # unless we own the region already
        for r in myGS.rList:
            if r is not None:
                for p in self.myPlanets.keys():
                    if p in r.members:
                        self.myPlanets[p] += r.value

    def prioritizeTheirPlanets(self, myGS, playerID):

        # map planetIDs to prioritized values
        self.theirPlanets = {}
        for p in myGS.pList:
            if p is not None:
                if p.owner is not playerID:
                    self.theirPlanets[p.idNum] = 0

        # prioritize inner planets in regions
        for r in myGS.rList:
            if r is not None:
                for p in r.members:
                    if p not in AIHelpers.getOuterPlanetsInRegion(myGS, r) and p in self.theirPlanets.keys():
                        self.theirPlanets[p] += 1
        
        # prioritize planets with more hostile connections (that is, connections to me)
        # this is how to use a dict --> for key, value in myPlanets.iteritems():
        mine = AIHelpers.getOwnedPlanets(myGS, playerID)
        for p in self.theirPlanets.keys():
            count = 0
            conns = AIHelpers.getHostileConnections(myGS, myGS.pList[p])
            for c in conns:
                if c in mine:
                    count += 1
            self.theirPlanets[p] += count

        # prioritize planets in regions with higher values
        for r in myGS.rList:
            if r is not None:
                for p in self.theirPlanets.keys():
                    if p in r.members:
                        self.theirPlanets[p] += r.value

    # Generates a random deployment; higher priorities get them first
    def generateDeployments(self, myGS, move):
        myPriorities = dict()
        for p in self.myPlanets.keys():
            myPriorities[p] = self.allPlanets[p]
        
        quota = myGS.getPlayerQuota(move.playerID)

        top = sum(myPriorities.values())

        soFar = 0
        #order them by highest priority to lowest
        while(len(myPriorities) > 0 and quota > 0):
            if(soFar == quota):
                break
            highestKey = max(myPriorities, key = myPriorities.get)
            highestValue = myPriorities[highestKey]
            myPriorities.pop(highestKey)

            toDeploy = int(math.ceil((highestValue/top) * quota))
            soFar += toDeploy
            if(soFar > quota):
                toDeploy -= (soFar - quota)
                soFar = quota

            dest = myGS.pList[highestKey]
            dest.numFleets += toDeploy
            move.addMove(0, dest.idNum, toDeploy)

        return move

    #Generate attacks; higher priority of theirs get attacked first
    #only attack if we're gonna win
    #can we attack from two sides?  YES
    def generateAttacks(self, myGS, move):
        theirPriorities = dict()
        for p in self.theirPlanets.keys():
            theirPriorities[p] = self.theirPlanets[p]
        
        toAttack = dict()  #this is a map of hostile planets to planets that we could potentially attack with
        alreadyDefeated = list()
        hostiles = AIHelpers.getAllHostileConnections(myGS, move.playerID)
        for i in theirPriorities:
            i = int(i)
            toAttack[i] = list()

        while(len(theirPriorities) > 0):
            source = -1
            dest = -1
            fleets = -1
        #get the highest priority one
            highestKey = max(theirPriorities, key = theirPriorities.get)
            theirPriorities.pop(highestKey)

            #are we connected to it?
            for p in hostiles:
                if str(highestKey) in hostiles[p]:
                    #do we have enough fleets to win?  FIGURE OUT HOW MANY WE NEED TO USE
                    source = int(p)
                    dest = int(highestKey)
                    if(myGS.pList[source].numFleets > (myGS.pList[dest].numFleets + 1)):
                        #let's do it!
                        fleets = min(myGS.pList[dest].numFleets+2, myGS.pList[source].numFleets - 1)
                        #print(str(source) + ", who has " + str(myGS.pList[source].numFleets) + " is attacking " + str(dest) + ", who has " + str(myGS.pList[dest].numFleets) + "fleets with " + str(fleets) + " fleets.\n")
                        move.addMove(source, dest, fleets)
                        alreadyDefeated.append(dest)
                        #update ourselves
                        myGS.pList[source].numFleets -= fleets
                        myGS.pList[dest].numFleets = 1
                    #otherwise, let's add it to what we can do later
                    else:
                        toAttack[dest].append(source)

        #all right, now find out who we can attack from two places that we couldn't from 1
        for dest in toAttack.keys():
            source = toAttack[dest]
            sm = 0
            needed = myGS.pList[dest].numFleets+2
            used = 0
            for i in source:
                sm += (myGS.pList[i].numFleets - 1)
            if sm > needed:
                #print("Sum: " + str(sm) + " Needed: " + str(needed))
                #print(str(source))
                j = 0
                while(used < needed and j < len(source)):
                    #print("Used: " + str(used) + " Needed: " + str(needed))
                    if(myGS.pList[source[j]].numFleets > 1):
                        #print(str(source[j]) + ", who has " + str(myGS.pList[source[j]].numFleets) + " is attacking " + str(dest)
                        #      + ", who has " + str(myGS.pList[dest].numFleets) + " fleets with " + str(min(myGS.pList[source[j]].numFleets -1, (needed-used))) + " fleets.\n")
                        move.addMove(source[j], dest, min(myGS.pList[source[j]].numFleets -1, (needed-used)))
                        used += myGS.pList[source[j]].numFleets -1
                        myGS.pList[source[j]].numFleets = 1
                    j += 1
                
        return move
     
#def distributePlanets():
#    minFleets = 5
#    players = gs.playerList
#    plyr = random.choice(gs.playerList)
#    planetList = list(gs.pList)
#    random.shuffle(planetList)
#    for p in planetList:
#        if p is None: continue
#        p.owner = plyr
#        p.numFleets = minFleets
#        plyr = (plyr + 1) % len(players)
#        if(plyr == 0):
#            plyr = len(players)

def setupPlanets(myGS):
    for p in myGS.pList:
        if p is not None:
            p.owner = 0

    myGS.updateRegions()

#gs = Gamestate()
#pa = PrioritizingAI()
#gs.loadXML("DemoGS.xml")
#setupPlanets(gs)
#gs.playerList.append(True)
#cds = []
#m = Move(1)
#m = pa.getMove(gs, 1, 1, cds)
#m = generateDeployments(gs, m, mine)
#m = generateAttacks(gs, m, theirs)
#print(str(gs))
#print(str(m))
#gs.pList[7].owner = 1
#m = pa.getMove(gs, 1, 1, cds)
#print(str(m))
#gs.pList[10].owner = 1
#m = pa.getMove(gs, 1, 1, cds)
#print(str(m))
