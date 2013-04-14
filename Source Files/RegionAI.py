# This AI script focuses on taking and holding regions.
#
# author: Josh Polkinghorn

from Gamestate import Gamestate, Planet, Region
from GameCommunications import Move
import AIHelpers

# Builds a move for a given player number based on a Gamestate
def getMove(gs, idNum, state, cards):
    if state == 1: # i.e. we're choosing planets
        return choosePlanet(gs, idNum)

    # Otherwise, build & return a normal move.
    gsLocal = gs.copy() # Leave external GS alone
    result = Move(idNum)
    generateDeployments(gsLocal, result)
    generateMoves(gsLocal, result)
    return result

# Chooses a planet to own.
def choosePlanet(gs, idNum):
    # TODO implement

    # For now, copypasta'd from RandomAI
    result = Move(idNum)
    unownedPlanets = []
    for p in gs.pList:
        if p is None: continue
        if p.owner is 0:
            unownedPlanets.append(p.idNum)
        
    target = random.choice(unownedPlanets)
    result.addMove(0, 0, target)
    return result

# Generates a set of attacks seeking to control regions.
def generateMoves(gsLocal, move):
    # TODO implement
    return

# Deploys fleets to planets, prioritizing controlling regions
# and holding regions already owned.
def generateDeployments(gsLocal, move):
    # TODO implement
    return

    
