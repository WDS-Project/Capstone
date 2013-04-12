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
from Mapmaker import Mapmaker
import sys
import random, math
from datetime import datetime

# Remember to import any AI scripts you want to use.
import RandomAI, RandomAIBetter, AggressiveAI, PrioritizingAI

# Returns a pointer to the getMove method of the specified AI type
def findAIType(diff):
    # List of AIs matched with difficulties.
    if (diff == 0):
        move = RandomAI.getMove
    elif (diff == 1):
        move = RandomAIBetter.getMove
    elif (diff == 2):
        move = AggressiveAI.getMove
    elif (diff == 3):
        move = PrioritizingAI.getMove
    else: # Undefined AI type
        raise Exception("Error: AI not found.")
    return move

# Prepares to simulate a game.
# - numAIs: number of AI players
# - diffs: array containing difficulties of each AI
def setup(numAIs, diffs):
    # Load AI players
    for i in range(numAIs):
        players[i+1] = [None, True] # [getMove, status]
        # This finds the getMove function for the given difficulty
        players[i+1][0] = findAIType(diffs[i])

    # Setup gamestate
    distributePlanets()
    gs.updateRegions()

def playGame():
    print("Started!")
    winner = 0
    rounds = 0
    currElim = 0
    
    while (winner == 0):
        rounds += 1
        #print("Round " + str(rounds) + "...")
        for p in players:
            # If player is not active, ignore it
            if not players[p][1]: continue
            #print("Player "+str(p)+" is moving.")
            
            # Gets a move from the AI
            m = players[p][0](gs, p, 3)
            #print("Player " + str(p) + "'s move is: " + str(m))
            processMove(m)
            gs.updateRegions()

        # After each move, check player status
        for j in players:
            # Check only if the player is actually active
            if (players[j][1] and checkElimination(j, currElim)):
                currElim += 1
        winner = checkWin()
        #input("WINNER = "+str(winner)+"; PRESS ENTER TO CONTINUE...")
    
    print("Game over: "+str(rounds)+" rounds elapsed.")
    return winner

def processMove(m):
    #print("Processing move: " + str(gs))
    quota = gs.getPlayerQuota(m.playerID)
    while(m.hasNext()):
        miniMove = m.next()
        dest = miniMove[1] 
        fleets = miniMove[2]
        source = miniMove[0]

        # Deployment
        if (source == 0):
            if(fleets > quota):
                print("Illegal move: quota exceeded. Quota: " + str(quota)
                      + " Fleets: " + str(fleets) + "\n")
                # If an AI makes an illegal move, it forfeits its turn
                return
            else:
                quota -= fleets
                gs.pList[dest].numFleets += fleets
            continue

        # Now we check if the planets are valid
        if (not gs.isConnected(source, dest)):
            print("Illegal move: planets " + str(source) + " and "
                  + str(dest) + " are not connected")
            return
        # ... and if there are sufficient fleets
        if (fleets >= gs.pList[source].numFleets):
            print("Illegal move: not enough fleets ("+str(fleets)+" requested,"
                  +" but planet "+str(source)+" only has " +
                  str(gs.pList[source].numFleets)+".)")
            return

        # Reinforcement
        if(m.playerID == gs.pList[dest].owner):
            gs.pList[source].numFleets -= fleets
            gs.pList[dest].numFleets += fleets
            
        # Attack
        else:
            stats.avgAttacks[m.playerID] += 1
            stats.avgFleets[m.playerID] += fleets
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

# This method for testing purposes only
def processAttackNonRandom(sourceFleets, destFleets):
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

# Calculates the results of an attack. The result is in the following format:
# [attacker fleets remaining, defending fleets remaining]
def processAttack(sourceFleets, destFleets):
    #print("Processing attack: " + str(sourceFleets) + " vs. " + str(destFleets) + "\n")
    retreating = False
    sourceOrig = sourceFleets

    while(destFleets > 0 and not(retreating)):
        smaller = min(sourceFleets, destFleets)
        for i in range(smaller):
            sNum = random.randint(1,6)
            dNum = random.randint(1,6)
            if(sNum > dNum):
                destFleets -= 1
            elif(dNum > sNum):
                sourceFleets -= 1

        # Retreating calculation
        if(sourceFleets *4 < sourceOrig):
            if(random.randint(0,1) == 0):
                retreating = True

    return [sourceFleets, destFleets]

def checkElimination(playerID, currElim):
    for p in gs.pList:
        if p is not None and p.owner is int(playerID):
            return False
    else:
        players[playerID][1] = False # sets player status to False (inactive)
        stats.elimOrder[playerID][currElim] += 1
        return True
    
def checkWin():
    active = None
    for p in players:
        if players[p][1] is False: continue # Player not active

        # If we get here, there is at least 1 active player
        
        # If we haven't already found an active player, now we have
        if active is None:
            active = p
        else:
            # Otherwise, there's more than one active player, and
            # therefore no winner
            return 0
    return active # return ID of remaining active player

def distributePlanets():
    # New fancy stuff!
    count = len(gs.pList) - 1
    pPtr = random.randint(1, len(players))
    minFleets = 5
    for p in gs.pList:
        if p is None: continue
        p.owner = 0
    
    while count > 0:
            # Gets a choice from the AI
            m = players[pPtr][0](gs, pPtr, 1)
            mini = m.next()
            target = mini[2]

            gs.pList[target].owner = pPtr
            gs.pList[target].numFleets = minFleets

            # INDEXING
            pPtr -= 1
            pPtr = (pPtr + 1) % len(players)
            pPtr += 1

            count -= 1

def run(diffList, gsMap='RiskGS.xml', numGames=50,
        numPlanets=None, numRegions=None):
    # Reset global results variables
    baseGS = Gamestate()
    players = {}
    stats.__init__()
    for d in range(1, len(diffList)+1):
        stats.victories.append(0)
        stats.avgAttacks.append(0)
        stats.avgFleets.append(0)
        stats.elimOrder.append([])
        for d2 in range(1, len(diffList)):
            stats.elimOrder[d].append(0)
    startTime = datetime.now()

    # Selects whether to load a map or make a new one
    if gsMap is None:
        print("No map given; generating a new one... ")

        # If we aren't given # planets or regions, figure them out
        # "by hand"
        if numPlanets is None:
            numPlanets = len(stats.victories) * 5 # 5 planets per player
        if numRegions is None:
            numRegions = math.ceil(numPlanets / 5) # ~5 planets per region
        m.generate(numPlanets, numRegions)
        print("Map generation complete.")
        gs.loadXML(m.out.toxml())
        print("----------------------------")
    else:
        gs.loadXML(gsMap)
    
    # Run the games
    if True:
    #try:
        for i in range(1, int(numGames)+1):
            print("\nGame "+str(i), end=': ')

            # Play the game & store the results
            setup(len(diffList), diffList)
            winner = playGame()
            stats.victories[winner] += 1
    #except:
    #    pass # for allowing a keyboard interrupt

    # Calculate final results
    totalTime = datetime.now() - startTime
    for a in range(1, len(diffList)+1):
        stats.avgAttacks[a] /= i
        stats.avgFleets[a] /= (stats.avgAttacks[a] * i)

    # Print the final results
    print("\n\nSimulations completed: "+str(i),
          "Elapsed time: "+str(totalTime),
          "Average time per game: "+str(totalTime / i),
          "Wins: "+str(stats.victories)+"\n", sep='\n')

def printInstructions():
    print("""-----------------------------
To use this utility: run(...)
--> diffList: array containing difficulty codes of AIs
--> [gsMap]: gamestate file to use (default: RiskGS.xml)
(Note: if gsMap is None, a map will be automatically generated instead,
according to m.params. See m.printParams() for more information.)
--> [numPlanets], [numRegions]: parameters for map creation if gsMap is None
--> [numGames]: number of games to simulate (default: 50)
-----------------------------
After games have been run, view the results in the following variables:
--> stats: log of all statistics; use stats.printStats() to view
--> gs: final gamestate of the final game
--> [m]: mapmaker used to generate the map (if applicable)
-----------------------------""")

# Class for storing the results of a series of games
class Statistics:
    def __init__(self):
        self.victories = [None] # total number of victories
        self.avgFleets = [None] # avg num fleets per attack
        self.avgAttacks = [None] # avg num of attacks per game
        self.elimOrder = [None] # record of time eliminated per player

    def printStats(self):
        print("Victories: " + str(self.victories))
        print("-----------------------------------")
        print("Avg fleets per attack:")
        for i in range(1, len(self.avgFleets)):
            print("Player "+str(i)+": %.2f" % self.avgFleets[i])
        print("-----------------------------------")
        print("Avg attacks per game:")
        for i in range(1, len(self.avgAttacks)):
            print("Player "+str(i)+": %.1f" % self.avgAttacks[i])
        print("-----------------------------------")
        print("Elimination order:")
        for i in range(1, len(self.avgAttacks)):
            print("Player "+str(i)+": "+str(self.elimOrder[i]))
        print("-----------------------------------")

# These global variables are used by all methods. This way they can be
# queried at runtime in the interpreter.
gs = Gamestate()
m = Mapmaker()
players = {}
stats = Statistics()

if __name__ == '__main__':
    printInstructions()
    run([0, 1, 2], numGames=10)
    #run([0, 1, 2], numGames=10)
    #run([1, 2, 2], gsMap=None, numGames=10)
    
    
