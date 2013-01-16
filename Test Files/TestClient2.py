import http
from http import client

conn1 = http.client.HTTPConnection("localhost:12345")
conn2 = http.client.HTTPConnection("localhost:12345")
conn1.request("POST", "/definegame/", "2/0/")
conn2.request("POST", "/join/", "1/")
r1 = conn1.getresponse()
r1.read()
r2 = conn2.getresponse()
r2.read()
conn1.request("POST", "/move/", "1/0:1:3/")
conn2.request("POST", "/gamechange", "2/")
