
import httplib
import sys

playerID = sys.argv[1]
connection = httplib.HTTPConnection("localhost:12345")
connection.request("POST", "http://localhost:12345/start/", "1")
res = connection.getresponse()
response = res.read()
while(1):
	print response
	responses = response.partition(':')
	print responses
	go = raw_input("Go? ");
	print "Turn: ", responses[0].strip(), "ID: ", playerID
	if responses[0] == playerID and go == 'y':
		print "That's my playerID!"
		connection = httplib.HTTPConnection("localhost:12345")
		connection.request("POST", "http://localhost:12345/talk/", playerID + ":move")
		resp = connection.getresponse()
		print resp.status
		response = resp.read()
		print response
	else:
		connection = httplib.HTTPConnection("localhost:12345")
		connection.request("POST", "http://localhost:12345/talk/", playerID + ":ready")
		resp = connection.getresponse()
		print resp.status
		response = resp.read()
