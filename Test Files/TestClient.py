# This script is built to act as a stand-in for
# a full GUI or AI client. It operates from the
# command line, and submits Moves to the server
# based on XML data.
#
# Josh Polkinghorn

# Uses TestGS3.xml, Moves_1.txt, and Moves_2.txt
import http
from http import client

# /definegame/
# /gamechange/
# /move/
# /join/

# Here's the sequence for making an HTTP request:
# h1 = http.client.HTTPConnection(url, port)
# h1.request(method, url)
# response = h1.getresponse()
# r = response.read()
# h1.request(...) ==> repeat from here on

### Main Script ###

# Move Format:
# <player_ID>/<IP_addr>/<source>:<dest>:<num_fleets>/etc.

# 1. Establish connection to server
addr = input("Enter address of server (enter for default): ")
if addr is "":
    addr = "localhost:12345"
port = input("Enter port number (enter for default): ")
if port is "":
    port = 12345

print("Now connecting to server...")
conn = http.client.HTTPConnection(addr)

# 2. Connection established. Send start game request
check = input("Are we first? Y/N: ")
if check == 'y' or check == 'Y':
    conn.request("POST", "/definegame/", "2/0/")
else:
    conn.request("GET", "/join/1/")

r = conn.getresponse()
print("Result: ", r.read())
input("Waiting...") # Wait for second script to connect

# 2.5. Open file, start getting moves.
num = input("Player 1 or 2? ")
if num == '1':
    f = open("Moves_1.txt")
else:
    f = open("Moves_2.txt")

# 3. Game started. Send first move
k = 'hi'
while(k != ""):
    move = f.readline()
    move = move[:-1] # remove '\n'
    conn.request("POST", "/move/", move)
    r = conn.getresponse()
    print("Result: ", r.read())
    k = input("Press something to continue (enter to stop): ")

# And now repeat, I guess
