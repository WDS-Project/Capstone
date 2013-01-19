How to talk to the Server:

Define a game:
/definegame/<number of human players>/<number of AI players>/<difficulty of AI 1>/difficulty of AI 2>/etc.
All input should be integers.  This is a POST request.

Join a game:
/join/<session ID>
Session ID is an integer.

Move:
/move/<playerID>/<miniMoves>

GameChange:
/gamechange/<playerID>