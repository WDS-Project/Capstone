
/***********
This is a class that handles the interaction of the client with the server.

@author Alana
*/

var Client = function() {
	var self = this;
	self.playerID = 1; //the human player is always player 1
	self.request;	//this is the xmlHTTP request, which is reinstantiated every time
	self.serverIPandPort = "localhost:12345" //CHANGE THIS!!!
	self.gs = new Gamestate();
	
	/**
	This function connects to the server and defines a game
	based on the parameters chosen by the user.
	*/
	self.connect = function() {
		
		//this gets the user's selected gamestate file
		var gsFile = document.getElementById("gamestate");
		var definition = gsFile.options[gsFile.selectedIndex].value + "/1/";
		
		//this collects all the AI difficulties
		var counter = 0;
		var ais = [];
		for(var i = 1; i < 6; i++) {
			var aiDiff = document.getElementById("ai"+i);
			ais[i-1] = aiDiff.options[aiDiff.selectedIndex].value;
			if(ais[i-1] > 0)
				counter++;
		}
		
		//This creates the request string
		definition += counter;
		for(var i = 0; i < counter; i++) 
			definition += "/" + ais[i];	
		definition += "/";
		
		//this sends the request string
		self.request = new XMLHttpRequest();
		if(self.request.open("POST", "http://" +self. serverIPandPort + "/definegame/", true));
		self.request.send(definition);
		
		self.request.onreadystatechange=function()
		{
			if (self.request.status==200 && self.request.readyState == 4) {
				response = self.request.responseText;
				self.gs.loadXML(response);
			}
			else {
				if(
				confirm("A connection to the server could not be established.\n Try again?"))
				self.connect();
			}
		}
	}
	
	/* A round of requests, that is, make a move if it's our turn, if not,
	request a gamechange.
	*/
	self.go = function(){
		//if it's not our turn, send a gamechange request
		if(self.gs.activePlayer != self.playerID) {
			self.request = new XMLHttpRequest();
			self.request.open("POST", "http://" + serverIPandPort + "/gamechange/", true);
			self.request.send(playerID);
		self.request.onreadystatechange=function() {
			if (self.request.status==200 && self.request.readyState == 4) {
				response = self.request.responseText;
				dealWithResponse(response);
			} else {
						if(
				confirm("We did not successfully receive the gamechange.\n Try again?"))
				self.go();
		} } }
		//if it's not, everything will wait on the user to click the
		//"Submit" button, which will cause a move to be made
	}
	
	/**
	Deal with responses from server
	*/
	self.dealWithResponses = function(res) {
		if(res == "eliminated")
			alert("Sorry, you lost.");
		else if (res == ("winner:" + playerID))
			alert("You have conquered all the planets!");
		//LOAD THE GAMECHANGE
	}
	
	self.move = function() {
		//so for this part we need an actual GUI to get info from to make a move.
		//This is getting frightening
		self.request = new XMLHttpRequest();
		self.request.open("POST", "http://" + serverIPandPort + "/move/", true)
		//GET A MOVE!
		self.request.send(move);
	}
	
};

var client = new Client();
