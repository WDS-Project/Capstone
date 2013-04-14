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
import RandomAI, RandomAIBetter, AggressiveAI, PrioritizingAI
import traceback # for printing errors to the log
# add more imports for different AI difficulty levels

#command line args: playerID, difficulty, sessionID, serverIPaddr:port
#global variables: difficulty, sessionID, serverIPandPort, gs
#this client writes its status to a text file log called, conveniently,
#"log#.txt"

#Difficulties: 0 = Random, <more here>

class AIClient:

    # self-explanatory constructor 
    def __init__(self, diff, sID, IPnPort):
        self.log = open('log'+str(diff)+'.txt', 'w')
        self.state = 1 # i.e. choosing planets -- MODERATELY PRELIMINARY
        self.difficulty = diff
        self.sessionID = sID
        self.serverIPandPort = IPnPort
        self.cards = [0, 0, 0]
        self.log.write(str("AI created. Difficulty: " + self.difficulty + "\n"))

    # join a game given a session ID, also load gamestate and playerID
    def connect(self):
        try:
            self.log.write(str("Connecting to " + self.serverIPandPort + "... "))
            connection = http.client.HTTPConnection(self.serverIPandPort)
            self.log.write(str("Found the server. " + self.serverIPandPort + "\n"))
            req = "/join/"
            self.log.write(str("Request is " + req + self.sessionID + "/\n"))
            self.log.write(self.difficulty+" "+self.sessionID+" "+self.serverIPandPort)
            connection.request("POST", req, self.sessionID)
            self.log.write(str("Made request to join session " + self.sessionID + "\n"))
            response = str(connection.getresponse().read())
            response = response[2:len(response)-1]
            self.log.write("Response is: " + response + "\n")
            index = response.index("n")
            self.playerID = response[:index-1]
            response = response[(index+1):]
            self.gs = Gamestate()
            self.log.write("Loading gamestate... ")
            self.gs.loadXML(response)
            self.log.write("Gamestate loaded.\n")
        except Exception:
            traceback.print_exc(file=self.log)

    # a round of requests; ie, make a move if it's our turn, if not, request
    # a gamechange
    def go(self):
        self.log.write(str("Turn: " + str(self.gs.activePlayer) + " My ID: " + str(self.playerID) + "\n"))
        if (int(self.gs.activePlayer) != int(self.playerID)):
            self.log.write("It's not our turn.")
            connection = http.client.HTTPConnection(self.serverIPandPort)
            connection.request("POST", "/gamechange/", self.playerID)
            self.log.write(" Sending gamechange request...\n")
        elif (int(self.gs.activePlayer) == int(self.playerID)):
            self.log.write("It's our turn.\n")
            if (self.difficulty == '0'):
                self.log.write("AI type: Random.\n")
                m = RandomAI.getMove(self.gs, self.playerID, self.state, self.cards)
            elif (self.difficulty == '1'):
                self.log.write("AI type: RandomBetter.\n")
                m = RandomAIBetter.getMove(self.gs, self.playerID, self.state, self.cards)
            elif (self.difficulty == '2'):
                self.log.write("AI type: Aggressive.\n")
                m = AggressiveAI.getMove(self.gs, self.playerID, self.state, self.cards)
            elif (self.difficulty == '3'):
                self.log.write("AI type: Prioritizing.\n")
                m = PrioritizingAI.getMove(self.gs, self.playerID, self.state, self.cards)
            else: #empty move
                m = str(self.playerID) + "/"
                
            move = str(m)
            self.log.write(str("Move: " + move + " \n"))
            connection = http.client.HTTPConnection(self.serverIPandPort)
            connection.request("POST", "/move/", move)

        response = connection.getresponse().read()
        self.dealWithResponse(response)

    # if the game is over (for us), exit, if not, load updated gamestate 
    def dealWithResponse(self, response):
        self.log.write(str("Response is: " + str(response) + "\n"))
        if(response is "eliminated" or response is ("winner:" + self.playerID)):
            self.log.close()
            sys.exit(0)
        else:
            # Track card information
            if int(self.gs.activePlayer) == int(self.playerID):
                idx1 = str(response).find("#CARDS:") + 8
                idx2 = str(response).rfind("]")
                cardStrs = str(response)[idx1:idx2].split(', ')
                for i in range(3):
                    self.cards[i] = int(cardStrs[i])
                self.log.write("New card info: " + str(self.cards)+"\n")
            # FYI, all of the casting to string is to combat encoding issues.

            # Now load the gamechange
            gc = Gamechange()
            gc.loadXML(response)
            self.gs.update(gc)

        if (self.state == 1):
            # This is super hamfisted, but meh.
            stillChoosing = False
            for p in self.gs.pList:
                if p is None: continue
                if p.owner is 0:
                    stillChoosing = True
            if not stillChoosing:
                self.state = 3

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


    



