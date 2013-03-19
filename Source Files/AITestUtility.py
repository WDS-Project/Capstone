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
import sys
import random
from datetime import datetime
import RandomAI, RandomAIBetter
# import scripts here

# diffs being a list of difficulties
def setup(gsName, numAIs, diffs):
    gs.loadXML(gsName)
    for i in range(numAIs):
        players[i+1] = [diffs[i], True] # [difficulty code, status]
        moves.append(0)
    #print("Players loaded: " + str(players) + "\n")
    distributePlanets()
    #print("Planets distributed: " + str(gs) + "\n")

def playGame():
    print("Game Started!")
    
    winner = 0
    k = 0
    while (winner == 0):
        k += 1
    #for k in range(10):
        #print("Round " + str(k) + "...")
        for p in players:
            #print("Player list: " + str(players))
            # If player is not active, ignore it
            if not players[p][1]: continue
            #print("Player "+str(p)+" is moving.")
            diff = players[p][0]
            if (diff == 0):
                m = RandomAI.getMove(gs, p)  #ADD ELIFS HERE
            elif (diff == 1):
                m = RandomAIBetter.getMove(gs, p)
            else: #empty move
                print("Error: AI not found.", file=sys.stderr)
                return
            #print("Player " + str(i) + "'s move is: " + str(m))
            processMove(m)
            moves[p] += 1
        for j in players:
            if(checkElimination(j)):
                elimOrder.append(j)
        winner = checkWin()
        #input("WINNER = "+str(winner)+"; PRESS ENTER TO CONTINUE...")
    print("Game over: "+str(k)+" rounds elapsed.")
    #print("Winner: "+str(winner)+"; player list: "+str(players))
    return winner

def printStats():
    print(str("Winner: " + winner), file=sys.stdout)
    eliminationStr = ""
    for i in range(len(elimOrder)):
        eliminiationStr += str(elimOrder[i] + " ")
    print(str("Order of elimination: " + eliminationStr), file=sys.stdout)

def processMove(m):
    #print("Beginning of move: " + str(gs))
    quota = gs.getPlayerQuota(m.playerID)
    while(m.hasNext()):
        miniMove = m.next()
        #print("miniMove: " + str(miniMove))
        dest = miniMove[1] 
        fleets = miniMove[2]

        #deployment
        if(miniMove[0] == 0):
            if(fleets > quota):
                print("Illegal move: quota exceeded. Quota: " + str(quota) + " Fleets: " + str(fleets) + "\n")
                return #turn is passed up for illegal action
            quota -= fleets
            gs.pList[dest].numFleets += fleets
            continue

        source = miniMove[0]

        if(not(gs.isConnected(source, dest))):
            print("Illegal move: planets " + str(source) + " and " + str(dest) + " are not connected")
            return #another illegal action

        if(fleets >= gs.pList[source].numFleets):
            print("Illegal move: not enough fleets ("+str(fleets)+" requested,"
                  +" but planet "+str(source)+" only has " +
                  str(gs.pList[source].numFleets)+".)")
            return #another illegal action

        #reinforcement
        if(gs.pList[source].owner == gs.pList[dest].owner):
            gs.pList[source].numFleets -= fleets
            gs.pList[dest].numFleets += fleets
        #attack
        else:
            results = processAttack(fleets, gs.pList[dest].numFleets)
            #attacker won
            if(results[1] == 0):
                gs.pList[dest].owner = gs.pList[source].owner
                gs.pList[dest].numFleets += results[0]
                gs.pList[source].numFleets -= fleets
            #attacker retreated or took the ultimate stand
            else:
                gs.pList[source].numFleets += (results[0] - fleets)
                gs.pList[dest].numFleets = results[1]


def processAttack(sourceFleets, destFleets):
    #print("Processing attack: " + str(sourceFleets) + " vs. " + str(destFleets) + "\n")
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

def checkElimination(playerID):
    for p in gs.pList:
        if p is not None and p.owner is int(playerID):
            return False
    else:
        print("Player " + str(playerID) + " eliminated.")
        players[playerID][1] = False # sets player status to False (inactive)
        return True
    
def checkWin():
    active = None
    for p in players:
        status = players[p][1]
        if status is False: continue

        # If we get here, status is nonzero -> at least 1 active player
        if active is None:
            # If we haven't already found an active player, now we have
            active = p
        else:
            return 0 # otherwise, no winner
    return active # return ID of remaining active player

def distributePlanets():
    minFleets = 5
    plyr = random.choice(list(players.keys()))
    planetList = list(gs.pList)
    random.shuffle(planetList)
    for p in planetList:
        if p is None: continue
        p.owner = plyr
        p.numFleets = minFleets
        plyr = (plyr + 1) % len(players)
        if(plyr == 0):
            plyr = len(players)

if __name__ == '__main__':
    startTime = datetime.now()
    numGames = 100
    victories = [None, 0, 0]
    for i in range(numGames):
        print("\n---------------\nRound "+str(i+1))
        players = {}
        gs = Gamestate()
        moves = []
        moves.append(None)
        elimOrder = []

        #setup("AIGS.xml", 2, [0,0])
        #setup("DemoGS.xml", 2, [1, 0])
        setup("GenGS1.xml", 2, [1, 0])
        winner = playGame()
        victories[winner] += 1
    totalTime = datetime.now() - startTime
    print("\n\nElapsed time: "+str(totalTime)+
          "\nAverage time per game: "+str(totalTime / numGames) )
    print("Wins: "+str(victories))
    
