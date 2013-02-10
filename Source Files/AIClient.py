#join game
#load gamestate from server
#set the playerID
#start move loop

#Note: This version is compatible with Python 2.7

import httplib  #for HTTP connections
import sys      #for command-line arguments
from Gamestate import Gamestate, Planet, Region
from GameCommunications import Gamechange, Move
import RandomAI

#command line args: playerID, difficulty, sessionID, serverIPaddr:port
#global variables: difficulty, sessionID, serverIPandPort, gs, currentPlayer

class AIClient:

    # self-explanatory constructor 
    def __init__(self, diff, sID, IPnPort):
        self.difficulty = diff
        self.sessionID = sID
        self.serverIPandPort = IPnPort

    # join a game given a session ID, also load gamestate and playerID
    def connect(self):
        connection = httplib.HTTPConnection(self.serverIPandPort)
        connection.request("POST", "http://" + self.serverIPandPort +
                           "/join/", self.sessionID)
        response = connection.getresponse().read()
        index = response.index("\n")
        self.playerID = response[:index]
        response = response[index:]
        self.gs = Gamestate()
        gs.loadXML(response)

    # a round of requests; ie, make a move if it's our turn, if not, request
    # a gamechange
    def go(self):
        if(gs.activePlayer != self.playerID):
            connection = httplib.HTTPConnection(self.serverIPandPort)
            connection.request("POST", "http://" + self.serverIPandPort +
                               "/gamechange/", self.playerID)
        elif(gs.activePlayer == self.playerID):
            m = RandomAI.getMove(self.playerID)
            move = str(m)
            connection = httplib.HTTPConnection(self.serverIPandPort)
            connection.request("POST", "http://" + self.serverIPandPort +
                               "/move/", move)

        response = connection.getresponse().read()
        dealWithResponse(response)

    # if the game is over (for us), exit, if not, load updated gamestate 
    def dealWithResponse(self, response):
        if(response is "eliminated" or response is "winner"):
            sys.exit(0)
        else:
            gc = Gamechange()
            gc.loadXML(response)
            self.gs.update(gc)

    # yeah ... this doesnt tell us much
    def __str__(self):
        print "player ID: " + self.playerID + " session ID: " + sessionID

def main(args):
        ai = AIClient(args[1], args[2], args[3])
        ai.connect()
        while(True):
            go()

# I still don't know why this nonsense is here
if __name__ == "__main__":
    sys.exit(main(sys.argv))


    



