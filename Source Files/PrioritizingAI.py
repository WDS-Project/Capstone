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

##Choosing planets:
# Regions with higher values
# Inner planets in regions, because they are easier to hold
# planets not connected to ones I already have, to get a good random sampling

# Builds a move for a given player based on a Gamestate
def getMove(gs, idNum):
    gsLocal = gs.copy() # makes a local copy so we don't change the external gs
    result = Move(idNum)
    mine = prioritizeMyPlanets(gs, int(idNum))
    theirs = prioritizeTheirPlanets(gs, int(idNum))
    result = generateDeployments(gsLocal, result, mine)
    result = generateAttacks(gsLocal, result, theirs)
    return result

##reinforcements sent from higher priority to lower, but
#it didn't work very well.

def prioritizeMyPlanets(myGS, playerID):

    # map planetIDs to prioritized values
    myPlanets = {}
    for p in AIHelpers.getOwnedPlanets(myGS, playerID):
        if myGS.pList[p].owner == playerID:
            myPlanets[p] = 0

    # prioritize outer planets in regions
    for r in myGS.rList:
        if r is not None:
            for p in AIHelpers.getOuterPlanetsInRegion(myGS, r):
                if p in myPlanets.keys():
                    myPlanets[p] += 1
    
    # prioritize planets with more hostile connections
    # for key, value in myPlanets.iteritems():
    for p in myPlanets.keys():
        myPlanets[p] += len(AIHelpers.getHostileConnections(myGS,myGS.pList[p]))*2

    # prioritize planets in regions with higher values
    # unless we own the region already
    for r in myGS.rList:
        if r is not None:
            for p in myPlanets.keys():
                if p in r.members:
                    myPlanets[p] += r.value

    return myPlanets

def prioritizeTheirPlanets(myGS, playerID):

    # map planetIDs to prioritized values
    theirPlanets = {}
    for p in myGS.pList:
        if p is not None:
            if p.owner is not playerID:
                theirPlanets[p.idNum] = 0

    # prioritize inner planets in regions
    for r in myGS.rList:
        if r is not None:
            for p in r.members:
                if p not in AIHelpers.getOuterPlanetsInRegion(myGS, r) and p in theirPlanets.keys():
                    theirPlanets[p] += 1
    
    # prioritize planets with more hostile connections (that is, connections to me)
    # this is how to use a dict --> for key, value in myPlanets.iteritems():
    mine = AIHelpers.getOwnedPlanets(myGS, playerID)
    for p in theirPlanets.keys():
        count = 0
        conns = AIHelpers.getHostileConnections(myGS, myGS.pList[p])
        for c in conns:
            if c in mine:
                count += 1
        theirPlanets[p] += count

    # prioritize planets in regions with higher values
    for r in myGS.rList:
        if r is not None:
            for p in theirPlanets.keys():
                if p in r.members:
                    theirPlanets[p] += r.value

    return theirPlanets

# Generates a random deployment; higher priorities get them first
def generateDeployments(myGS, move, myPriorities):
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
def generateAttacks(myGS, move, theirPriorities):
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
                    fleets = myGS.pList[source].numFleets - 1
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
        needed = myGS.pList[dest].numFleets+1
        used = 0
        for i in source:
            sm += myGS.pList[i].numFleets
        if sm > needed:
            #we can do it!
            if(used < needed):
                for i in source:
                    if(myGS.pList[i].numFleets > 1):
                        move.addMove(i, dest, myGS.pList[i].numFleets -1)
                        used += myGS.pList[i].numFleets -1
                        myGS.pList[i].numFleets = 1
            else: #it's done
                break
            
    return move
     
def distributePlanets():
    minFleets = 5
    players = gs.playerList
    plyr = random.choice(gs.playerList)
    planetList = list(gs.pList)
    random.shuffle(planetList)
    for p in planetList:
        if p is None: continue
        p.owner = plyr
        p.numFleets = minFleets
        plyr = (plyr + 1) % len(players)
        if(plyr == 0):
            plyr = len(players)

#gs = Gamestate()
#gs.loadXML("DemoGS.xml")
#gs.playerList.append(True)
#distributePlanets()
#print(str(mine))
#print(str(theirs))
#m = Move(1)
#m = generateDeployments(gs, m, mine)
#m = generateAttacks(gs, m, theirs)
#print(str(gs))
#print(str(m))
