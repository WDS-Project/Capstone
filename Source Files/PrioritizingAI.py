###NEW AI
#Map planets to values
#1. Outer planets in region [with connections]
#2. Planets with more [hostile] connections
#3. Planets in regions with high values
# Prioritize my own planets and enemy planets
# Don't attack if you can't win
# Attack if odds are greater than 1/2
# Move fleets to higher priority planets

"""
Improvements to make:
Deploy more to planets with hostile connections
After a certain number of rounds, switch strategy
Path reinforcements

"""

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import random
import AIHelpers
import math
from collections import deque

class PrioritizingAI:
    
    def __init__(self, playerID):
        self.allPlanets = {}
        self.myPlanets = {}
        self.theirPlanets = {}
        self.moveCount = 0
        self.cards = []
        self.myID = int(playerID)

    
    # Builds a move for a given player based on a Gamestate
    def getMove(self, gs, state, cards):
        gsLocal = gs.copy()
        self.prioritizeAllPlanets(gsLocal)
        if(state == 1):
            return self.choosePlanet(gsLocal)
        result = Move(self.myID)
        self.prioritizeMyPlanets(gsLocal)
        self.prioritizeTheirPlanets(gsLocal)
        result = self.generateDeployments(gsLocal, result, cards)
        result = self.generateReinforcements(gsLocal, result)
        result = self.generateAttacks(gsLocal, result)
        self.moveCount += 1
        return result


    ############################################    
    ##      Prioritizing methods              ##
    ############################################


    # prioritize all planets for choosing at the beginning
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
                self.allPlanets[p] += len(regions)*5
            regions.pop(lowestKey)            


    def prioritizeMyPlanets(self, myGS):
        self.myPlanets = dict()
        # map planetIDs to prioritized values
        for p in AIHelpers.getOwnedPlanets(myGS, self.myID):
            if myGS.pList[p].owner == self.myID:
                self.myPlanets[p] = self.allPlanets[p]
                
        # prioritize outer planets in regions
        for r in myGS.rList:
            if r is not None:
                for p in AIHelpers.getOuterPlanetsInRegion(myGS, r):
                    if p in self.myPlanets.keys():
                        self.myPlanets[p] += 1

        # prioritize planets with more hostile connections
        # for key, value in myPlanets.iteritems():
        for p in self.myPlanets.keys():
            self.myPlanets[p] += len(AIHelpers.getHostileConnections(myGS,myGS.pList[p]))*5

        # take away value from regions we already own
        for r in myGS.rList:
            if r is not None:
                if(int(r.owner) == int(self.myID)):
                    for p in r.members:
                        self.myPlanets[p] -= int(r.value/2)                        

    def prioritizeTheirPlanets(self, myGS):
        # map planetIDs to prioritized values
        self.theirPlanets = {}
        for p in myGS.pList:
            if p is not None:
                if int(p.owner) is not self.myID:
                    self.theirPlanets[p.idNum] = self.allPlanets[p.idNum]

        # prioritize inner planets in regions
        for r in myGS.rList:
            if r is not None:
                for p in r.members:
                    if p not in AIHelpers.getOuterPlanetsInRegion(myGS, r) and p in self.theirPlanets.keys():
                        self.theirPlanets[p] += 1

        """ This really doesn't help because I'm going to attack anyway
        # prioritize planets with more hostile connections (that is, connections to me)
        # this is how to use a dict --> for key, value in myPlanets.iteritems():
        mine = AIHelpers.getOwnedPlanets(myGS, playerID)
        for p in self.theirPlanets.keys():
            count = 0
            conns = AIHelpers.getHostileConnections(myGS, myGS.pList[p])
            for c in conns:
                if c in mine:
                    count += 1
            self.theirPlanets[p] += count*2
        """

    #######################################
    ##      Methods for making moves     ##
    #######################################

    #choose the planet with the highest value
    def choosePlanet(self, myGS):
        move = Move(self.myID)
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


    def generateReinforcements(self, myGS, move):

        """
        Get the front lines
        Move all troops one up on the path to them
        If the front lines never change, eventually they will all get there
        Have a done array
        """

        #Get the front lines
        frontLines = AIHelpers.getOuterPlanets(myGS, self.myID)
        #for f in frontLines:
        #    print(str(f.idNum))

        done = []

        #Loop through the paths
        for planet in frontLines:
            paths = findPaths(planet.idNum, self.myPlanets.keys(), myGS)
            #print(str(paths))
            for trail in paths:
                if paths[trail] is not None:
                    for p in range(len(paths[trail])-3):
                        #if this planet isn't a frontLine too
                        source = paths[trail][p]
                        if myGS.pList[source] not in frontLines and source not in done:
                            done.append(source)
                            dest = paths[trail][p+1]
                            fleets = myGS.pList[source].numFleets - 1
                            if fleets > 0:
                                move.addMove(source, dest, fleets)
                                myGS.pList[source].numFleets -= fleets
                                myGS.pList[dest].numFleets += fleets
                        
        """
        myPriorities = dict()
        for i in self.myPlanets.keys():
            myPriorities[i] = self.myPlanets[i]

        while(len(myPriorities) > 0):
            highestKey = max(myPriorities, key = myPriorities.get)
            highestValue = myPriorities[highestKey]
            myPriorities.pop(highestKey)

            for i in myPriorities.keys():
                #print("Highest priority fleets: " + str(highestValue) + " We're looking at: " + str(myGS.pList[i].numFleets))
                if myGS.pList[i].numFleets > highestValue:
                    #make sure they're connected
                    if(myGS.isConnected(i, highestKey)):
                        fleets = myGS.pList[i].numFleets - highestValue
                        #print("Sending " + str(fleets) + " fleets from " + str(i) + ", who has " + str(myGS.pList[i].numFleets) + " fleets.")
                        move.addMove(i, highestKey, myGS.pList[i].numFleets - highestValue)
                        myGS.pList[highestKey].numFleets += fleets
                        myGS.pList[i].numFleets -= fleets
        """
        
        return move

    # Generates deployments; higher priorities get them first
    def generateDeployments(self, myGS, move, cards):
        quota = myGS.getPlayerQuota(self.myID)

        #turn in cards if possible
        if(self.moveCount % 3 == 0):
            cardCheck = AIHelpers.checkCards(cards)
            if cardCheck > -1:
                AIHelpers.turninCards(cards, move, cardCheck)
                quota += AIHelpers.getTurninValue(myGS.turninCount)
                myGS.turninCount += 1
        
        myPriorities = dict()
        for p in self.myPlanets.keys():
            myPriorities[p] = self.myPlanets[p]

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
        hostiles = AIHelpers.getAllHostileConnections(myGS, self.myID)
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
                    #do we have enough fleets to win?
                    source = int(p)
                    dest = int(highestKey)
                    if(myGS.pList[source].numFleets > myGS.pList[dest].numFleets+1):
                        #let's do it!
                        fleets = min(myGS.pList[dest].numFleets+1, myGS.pList[source].numFleets - 1)
                        #print(str(source) + ", who has " + str(myGS.pList[source].numFleets) + " is attacking " + str(dest) + ", who has " + str(myGS.pList[dest].numFleets) + "fleets with " + str(fleets) + " fleets.\n")
                        move.addMove(source, dest, fleets)
                        alreadyDefeated.append(dest)
                        #update ourselves
                        myGS.pList[source].numFleets -= fleets
                    #otherwise, let's add it to what we can do later
                    else:
                        toAttack[dest].append(source)

        #all right, now find out who we can attack from two places that we couldn't from 1
        for dest in toAttack.keys():
            if dest not in alreadyDefeated:
                source = toAttack[dest]
                sm = 0
                needed = myGS.pList[dest].numFleets+1
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
                            fleets = min(myGS.pList[source[j]].numFleets -1, (needed-used))
                            move.addMove(source[j], dest, fleets)
                            used += fleets
                            myGS.pList[source[j]].numFleets -= fleets
                        j += 1
        return move
     
def distributePlanets():
    minFleets = 5
    players = newGs.playerList
    plyr = random.choice(newGs.playerList)
    planetList = list(newGs.pList)
    random.shuffle(planetList)
    for p in planetList:
        if p is not None:
            p.owner = plyr
            p.numFleets = minFleets
            plyr = (plyr + 1) % len(players)
            if(plyr == 0):
                plyr = len(players)

def setupPlanets(myGS):
    for p in myGS.pList:
        if p is not None:
            p.owner = 0
    myGS.updateRegions()

#pass in the targest planetID and a list of planet IDs that you own
def findPaths(target, myPlanets, gs):
    #print("we own: " + str(myPlanets))
    
    visited = {}
    for p in myPlanets:
        visited[p] = False

    paths = {}
    sumP = {}
    for p in myPlanets:
        paths[p] = list([gs.pList[p].numFleets])

    q = deque()
    q.append(target)

    while(len(q) > 0):
        current = q.popleft()
        #print("Current = " + str(current))
        visited[current] = True
        conns = gs.getConnections(current)
        #print("Connected to: " + str(conns))
        for p in myPlanets:
            if str(p) in conns and visited[p] is False:
                #print(str(p) + " is connected to it and it hasn't been visited.")
                q.append(p)
                #print("Appended: " + str(q))
                total = paths[p][0] + paths[current][len(paths[current])-1]
                paths[p] = list([current]) + paths[current][:(len(paths[current])-1)] + list([total])
                #print("Path from " + str(p) + " to " + str(target) + ": " + str(paths[p]))

    for v in visited:
        if(visited[v] == False):
            paths[v] = None

    return paths
        
    

#newGs = Gamestate()
#pa = PrioritizingAI(1)
#newGs.loadXML("RiskGS.xml")
#newGs.playerList.append(True)
#distributePlanets()
#newGs.updateRegions()
#print(str(newGs))
#pa.prioritizeAllPlanets(newGs)
#pa.prioritizeMyPlanets(newGs)
#paths = findPaths(32, pa.myPlanets.keys(), newGs)
#print(str(paths))

#cds = [0,0,0]
#m = Move(1)
#m = pa.getMove(newGs, 0, cds)
#m = pa.generateDeployments(newGs, m)
#m = generateReinforcements(newGs, m) 
#m = generateAttacks(gs, m, theirs)
#print(str(gs))
#print(str(m))
