#Input: Number of AI’s and difficulties
#--Load Gamestate
#--Load array with player numbers
#--Get move from player 1
#--Process move / update gamestate / update stats (move count, elimination order, etc)
#--Repeat
#Output: winner , move count? , order of elimination?
#---Needs to check illegalities

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Gamechange, Move
from random import randint
import random
import RandomAI
# import scripts here

# diffs being a list of difficulties
def setup(gsName, numAIs, diffs):
    gs.loadXML(gsName)
    for i in range(numAIs):
        players.append(diffs[i])
        moves.append(0)
    print("Players loaded: " + str(players) + "\n")
    distributePlanets()
    print("Planets distributed: " + str(gs) + "\n")

def playGame():
    print("They're playing ... \n")
    winner = 0
    for k in range(10):
        for i in range(1, len(players)):
            if(players[i] == 0):
                m = RandomAI.getMove(gs, i)  #ADD ELIFS HERE
            else: #empty move
                m = str(self.playerID) + "/"
            print("Player " + str(i) + ": " + str(m))
            processMove(m)
            moves[i] += 1
        for j in range(1, len(players)):
            if(checkElimination(j)):
                elimOrder.append(j)
                players.pop(j)
            winner = checkWin()
    print("Game over\n")

def printStats():
    print(str("Winner: " + winner + "\n"), file=sys.stdout)
    eliminationStr = ""
    for i in range(len(elimOrder)):
        eliminiationStr += str(elimOrder[i] + " ")
    print(str("Order of elimination: " + eliminationStr), file=sys.stdout)

def processMove(m):
    print("Beginning of move: " + str(gs))
    quota = gs.getPlayerQuota(m.playerID)
    while(m.hasNext()):
        miniMove = m.next()
        print("miniMove: " + str(miniMove))
        dest = miniMove[1] 
        fleets = miniMove[2]

        #deployment
        if(miniMove[0] == 0):
            if(fleets > quota):
                print("Illegal move: quota exceeded. Quota: " + str(quota) + " Fleets: " + str(fleets) + "\n")
                return #turn is passed up for illegal action
            quota -= fleets
        #    gs.pList[dest].numFleets += fleets
            continue

        source = miniMove[0]

        if(not(gs.isConnected(source, dest))):
            print("Illegal move: planets " + str(source) + " " + str(type(source)) + " and " + str(dest) + " are not connected")
            return #another illegal action

        if(fleets >= gs.pList[source].numFleets):
            print("Illegal move: not enough fleets")
            return #another illegal action

        #reinforcement
        if(gs.pList[source].owner == gs.pList[dest].owner):
        #    gs.pList[source].numFleets -= fleets
            gs.pList[dest].numFleets += fleets
        #attack
        else:
            results = processAttack(fleets, gs.pList[dest].numFleets)
            print(str(results))
            #attacker won
            if(results[1] == 0):
                gs.pList[dest].owner = gs.pList[source].owner
                gs.pList[dest].numFleets += results[0]
            #    gs.pList[source].numFleets -= fleets
            #attacker retreated or took the ultimate stand
            else:
                gs.pList[source].numFleets += results[0]
                gs.pList[dest].numFleets = results[1]


def processAttack(sourceFleets, destFleets):
    print("Process attack: " + str(sourceFleets) + " " + str(destFleets) + "\n")
    res = []
    if(sourceFleets > destFleets):
        res.append(sourceFleets - destFleets)
        res.append(0)
    elif(sourceFleets < destFleets):
        res.append(0)
        res.append(destFleets - sourceFleets)
    else:
        res.append(1)
        res.append(1)
    return res

    #retreating = False
    #sourceOrig = sourceFleets

    #while(destFleets > 0 and not(retreating)):
    #    print("We made it in the while loop\n")
    #    smaller = min(sourceFleets, destFleets)
    #    for i in range(smaller):
    #        sNum = randint(1,6)
    #        dNum = randint(1,6)
    #        if(sNum > dNum):
    #            destFleets -= 1
    #        elif(dNum > sNum):
    #            sourceFleets -= 1
    #
    #    if(sourceFleets *4 > sourceOrig):
    #        if(randint(0,1) == 0):
    #            retreating = True
    #print("We made it out of the while loop\n")

    #return [sourceFleets, destFleets]

def checkElimination(id):
    for i in range(1, len(gs.pList)):
        if(gs.pList[i].owner == id):
            return False
    print("Player " + str(id) + " eliminated.\n")
    return True
    
def checkWin():
    if(len(players) == 2):
        return players[1]
    return 0

def distributePlanets():
    minFleets = 1
    plyr = randint(1, (len(players)-1))
    planetIDs = []
    for i in range(len(gs.pList)-1):
        planetIDs.append(i + 1)
    random.shuffle(planetIDs)
    for i in range(len(planetIDs)):
        gs.pList[planetIDs[i]].owner = plyr
        print("Player " + str(plyr) + " owns planet " + str(planetIDs[i]) + "\n")
        gs.pList[planetIDs[i]].numFleets = minFleets
        plyr = (plyr + 1) % (len(players) - 1)
        if(plyr == 0):
            plyr = (len(players) - 1)

#PLAYERS START AT 0
players = []
players.append(None)
gs = Gamestate()
moves = []
moves.append(None)
elimOrder = []

setup("AIGS.xml", 2, [0,0])
playGame()
    
