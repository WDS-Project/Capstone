#join game
#load gamestate from server
#set the playerID
#start move loop

#Note: This version is compatible with Python 3.2

import http
from http import client #for HTTP connections
import sys      #for command-line arguments
from Gamestate import Gamestate, Planet, Region
from GameCommunications import Gamechange, Move
import RandomAI
import traceback # for printing errors to the log

#command line args: playerID, difficulty, sessionID, serverIPaddr:port
#global variables: difficulty, sessionID, serverIPandPort, gs
#this client writes its status to a text file log called, conveniently,
#"ailog.txt"

class AIClient:

    # self-explanatory constructor 
    def __init__(self, diff, sID, IPnPort):
        self.log = open('X:\Capstone\Repository\Capstone\log'+str(diff)+'.txt', 'w')
        self.log.write("AI created.\n")
        self.difficulty = diff
        self.sessionID = sID
        self.serverIPandPort = IPnPort

    # join a game given a session ID, also load gamestate and playerID
    def connect(self):
        try:
            self.log.write(str("Connecting to " + self.serverIPandPort + "... \n"))
            connection = http.client.HTTPConnection(self.serverIPandPort)
            self.log.write(str("Found the server. " + self.serverIPandPort + "\n"))
            req = "/join/"
            self.log.write(str("Request is " + req + self.sessionID + "/\n"))
            connection.request("POST", req, self.sessionID)
            self.log.write(str("Made request to join session " + self.sessionID + "\n"))
            response = str(connection.getresponse().read())
            response = response[2:len(response)-1]
            self.log.write("Response is: " + response + "\n")
            index = response.index("n")
            self.playerID = response[:index-1]
            response = response[(index+1):]
            self.gs = Gamestate()
            self.log.write("Loading gamestate ...\n")
            self.gs.loadXML(response)
            self.log.write("Gamestate loaded.\n")
        except Exception:
            traceback.print_exc(file=self.log)

    # a round of requests; ie, make a move if it's our turn, if not, request
    # a gamechange
    def go(self):
        self.log.write(str("Turn: " + str(self.gs.activePlayer) + " My ID: " + str(self.playerID) + "\n"))
        if(int(self.gs.activePlayer) != int(self.playerID)):
            self.log.write("It's not our turn.\n")
            connection = http.client.HTTPConnection(self.serverIPandPort)
            connection.request("POST", "/gamechange/", self.playerID)
            self.log.write("Therefore I have sent a gamechange request.\n")
        elif(int(self.gs.activePlayer) == int(self.playerID)):
            self.log.write("It's our turn.\n")
            m = RandomAI.getMove(self.gs, self.playerID)
            move = str(m)
            self.log.write(str("Move: " + move + " \n"))
            connection = http.client.HTTPConnection(self.serverIPandPort)
            connection.request("POST", "/move/", move)

        response = connection.getresponse().read()
        self.dealWithResponse(response)

    # if the game is over (for us), exit, if not, load updated gamestate 
    def dealWithResponse(self, response):
        self.log.write(str("Response is: " + response + "\n"))
        if(response is "eliminated" or response is ("winner:" + self.playerID)):
            self.log.close()
            sys.exit(0)
        else:
            gc = Gamechange()
            gc.loadXML(response)
            self.gs.update(gc)

    # yeah ... this doesnt tell us much
    def __str__(self):
        print("player ID: " + self.playerID + " session ID: " + sessionID)

def main(args):
    ai = AIClient(args[1], args[2], args[3])
    try:
        ai.connect()
        while(True):
                ai.go()
    except Exception:
        traceback.print_exc(file=ai.log)
        ai.log.close()
    ai.log.close()

# I still don't know why this nonsense is here
if __name__ == "__main__":
    sys.exit(main(sys.argv))


    



