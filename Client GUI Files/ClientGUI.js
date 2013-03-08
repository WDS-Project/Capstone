/* This is the Javascript for displaying the GUI for the WDS game.
* Also includes code for storing game data, validating moves by the player,
* loading various kinds of XML, and communication with the server.
*
* Author: WDS Project	
*/

// ********* How to load an XML string into the stuff we want. *********
// *** Step 1: Load the XML into a Javascript object. ***
// Incidentally, our target is TestGS3.xml (as always), reproduced here in glorious massive string form.
/*var gsString = '<?xml version="1.0" encoding="UTF-8"?><Gamestate><Players numPlayers="2" activePlayer="1" turnNumber="0" cycleNumber="0"/>' +
'<PlanetList><Planet idNum="1" name="Florida" owner="1" numFleets="5" color="#ffee33" position="135,125" radius="30" /><Planet idNum="2" name="Aruba"' +
' owner="1" numFleets="5" color="#aabbcc" position="700,450" radius="35" /><Planet idNum="3" name="Manitoba" owner="1" numFleets="5" color="#00ffaa"'+
' position="600,250" radius="25" /><Planet idNum="4" name="Sparta" owner="2" numFleets="5" color="#aa00ee" position="175,400" radius="25" /><Planet'+
' idNum="5" name="Akihabara" owner="2" numFleets="5" color="#55cc11" position="400,450"	radius="30" /></PlanetList><ConnectionList><connection>1,2</connection>'+
'<connection>1,3</connection><connection>1,4</connection><connection>1,5</connection><connection>2,3</connection><connection>2,4</connection>'+
'<connection>2,5</connection><connection>3,4</connection><connection>3,5</connection><connection>4,5</connection></ConnectionList><RegionList>'+
'<Region idNum="1" name="Eastern U.S." value="5" owner="0" color="#44aadd"><memberList><member>1</member><member>2</member><member>3</member>'+
'<member>4</member><member>5</member></memberList></Region></RegionList></Gamestate>';

var gcString = '<?xml version="1.0" encoding="UTF-8"?><GameChange><Players activePlayer="1" cycleNumber="1" turnNumber="1"/>' +
'<Planets><Planet idNum="1" numFleets="4" owner="1"/><Planet idNum="2" numFleets="7" owner="1"/><Planet idNum="4" numFleets="1" owner="2"/>' +
'</Planets></GameChange>';*/

var drawLoop; // the game loop - see DrawLoop() below

// *** Step 2: Load self Javascript object into actual meaningful data structures. ***
var Planet = function(el) {
	var self = this;
	
	// Loads a planet from XML element el
	self.loadXML = function(el) {
		self.name = el.getAttribute("name");
		self.idNum = Number(el.getAttribute("idNum"));
		self.numFleets = Number(el.getAttribute("numFleets"));
		self.owner = Number(el.getAttribute("owner"));
		var position = el.getAttribute("position").split(',');
		self.xPos = position[0];
		self.yPos = position[1];
		self.radius = el.getAttribute("radius");
		self.color = el.getAttribute("color");
	};
	
	// Returns this object as a string.
	self.toString = function() {
		return ("Planet " + self.idNum + ", " + self.name +
			". Owner: " + self.owner + "; number of fleets: "
			+ self.numFleets + "; position: " + self.xPos + ", "
			+ self.yPos + "; color: " + self.color + ".");
	};
	
	// Tests if a point is inside this planet.
	self.isInside = function(x, y) {
		var h = Math.sqrt(Math.pow( (x - self.xPos), 2)
				+ Math.pow( (y - self.yPos), 2));
		if (h <= self.radius)
			return true;
	};
	
	// Draws this planet, including # of fleets. Draws differently depending
	// on whether this planet is selected or not.
	self.draw = function(ctx, view, isSelection) {
		ctx.save();
		ctx.fillStyle = self.color;
		ctx.strokeStyle = (isSelection ? '#f11' : '#fff');
		ctx.lineWidth = (isSelection ? 3 : 2);
		
		ctx.beginPath();
		ctx.arc(self.xPos - view.offsetX, self.yPos - view.offsetY,
			self.radius, 0, 2*Math.PI, true);
		ctx.fill();
		ctx.stroke();
		ctx.closePath();
		ctx.restore();
		
		// Draw number of fleets.
		ctx.save();
		ctx.beginPath();
		var fontSize = (isSelection ? 28 : 25);
		ctx.font = fontSize + 'pt Calibri';
		ctx.fillStyle = 'red';
		ctx.fillText(self.numFleets, self.xPos - view.offsetX - fontSize/3,
			self.yPos - view.offsetY + fontSize/3);
		ctx.fill();
		ctx.closePath();
		ctx.restore();
	};
	
	// Basic setup
	if (!el) { // if el isn't defined; this shouldn't happen
		self.name = "";
		self.idNum = 0;
		self.numFleets = 0;
		self.owner = 0;
	} else {
		self.loadXML(el);
	}
};
var Region = function(el) {
	var self = this;
	
	// Loads a region from an XML element
	self.loadXML = function(el) {
		self.name = el.getAttribute("name");
		self.idNum = Number(el.getAttribute("idNum"));
		self.value = Number(el.getAttribute("value"));
		self.owner = Number(el.getAttribute("owner"));
		self.color = el.getAttribute("color");
		var memberListEl = el.getElementsByTagName("memberList")[0];
		var memberList = memberListEl.getElementsByTagName("member");
		for (var i = 0; i < memberList.length; i++) {
			var m = memberList[i];
			self.members[Number(m.childNodes[0].data)] = true;
		}
		self.members.length = memberList.length;
	};
	
	// Returns this region as a string
	self.toString = function() {
		return ("Region " + self.idNum + ", " + self.name +
			". Owner: " + self.owner + "; value: " + self.value +
			". List of members: " + self.members + ".");
	};
	
	// Basic setup
	self.members = {};
	if (!el) {
		self.name = "";
		self.idNum = 0;
		self.value = 0;
		self.owner = 0;
	} else {
		self.loadXML(el);
	}
};
var Connection = function(el) {
	var self = this;
	
	// Returns this connection as a string
	self.toString = function() {
		return "(" + self.p1 + ", " + self.p2 + "); direct = " + self.direct
			+ " and status = " + self.status + ".";
	};
	
	// Tests if a point is inside this connection (only if active).
	self.isInside = function(xClick, yClick) {
		if (self.direct == 0) return false; // connection inactive
		var p = {x:xClick, y:yClick};
		var rPts = self.shapes[self.direct].rPts;
		var tPts = self.shapes[self.direct].tPts;
		return (self.pointIsInside(tPts[0], tPts[1], tPts[2], p)
			|| self.pointIsInside(rPts[0], rPts[1], rPts[2], p)
			|| self.pointIsInside(rPts[0], rPts[2], rPts[3], p));
	};
	// Determines if a point is within a triangle by converting to barycentric
	// coordinates.
	self.pointIsInside = function(p1, p2, p3, p) {
		var alpha = ((p2.y - p3.y)*(p.x - p3.x) + (p3.x - p2.x)*(p.y - p3.y)) /
		((p2.y - p3.y)*(p1.x - p3.x) + (p3.x - p2.x)*(p1.y - p3.y));
		var beta = ((p3.y - p1.y)*(p.x - p3.x) + (p1.x - p3.x)*(p.y - p3.y)) /
		((p2.y - p3.y)*(p1.x - p3.x) + (p3.x - p2.x)*(p1.y - p3.y));
		var gamma = 1.0 - alpha - beta;
		return (alpha > 0 && beta > 0 && gamma > 0);
	};
	
	// Calculates all shapes this connection might be asked to draw based
	// on a list of planets.
	self.findAllShapes = function(pList) {
		self.shapes = [null];
		var p1 = pList[self.p1]; // gets the planet object associated
		var p2 = pList[self.p2]; // with index p1 or p2
		
		// Find shapes...
		self.shapes[1] = {};
		var result = self.findShapes(p1, p2);
		self.shapes[1].rPts = result[0];
		self.shapes[1].tPts = result[1];
		
		// ... then repeat for the opposite order.
		self.shapes[2] = {};
		result = self.findShapes(p2, p1);
		self.shapes[2].rPts = result[0];
		self.shapes[2].tPts = result[1];
	};
	
	// Calculates a specific pair of shapes.
	self.findShapes = function(p1, p2) {
		var sel = {x:Number(p1.xPos), y:Number(p1.yPos)}; // selected planet
		var tar = {x:Number(p2.xPos), y:Number(p2.yPos)}; // target planet
		
		// dx & dy are components of the unit vector representing
		// the slope between sel and tar
		var dx = sel.x - tar.x;
		var dy = sel.y - tar.y;
		var dist = Math.sqrt(dx*dx + dy*dy);
		dx /= dist; 
		dy /= dist;
		
		// *** This section finds the points of the triangle. ***
		var len = 30; // length of sides of the triangle
		var k = .80; // distance down the line to draw the triangle - here, 80% of the way to tar
		
		// array of points of the triangle
		var tPts = [{x:0, y:0}, {x:0, y:0}, {x:0, y:0}, {x:0, y:0}];
		// tPts[0] => point of the triangle pointing to tar
		// tPts[1], tPts[2] => the other two points of the triangle
		// tPts[3] => point opposite tPts[0]; only used to calculate tPts[1] & tPts[2]
		
		// tPts[0] is found by interpolating between sel and tar
		tPts[0].x = sel.x + k * (tar.x - sel.x);
		tPts[0].y = sel.y + k * (tar.y - sel.y);
		
		// tPts[3] is found by "backing up" from tPts[0] along <dx, dy>
		tPts[3].x = tPts[0].x + dx * len;
		tPts[3].y = tPts[0].y + dy * len;
		
		// tPts[1] & tPts[2] are computed using <dx, dy> and pts[3]
		tPts[1].x = tPts[3].x + (len/2)*dy;
		tPts[1].y = tPts[3].y - (len/2)*dx;
		tPts[2].x = tPts[3].x - (len/2)*dy;
		tPts[2].y = tPts[3].y + (len/2)*dx;
		
		// *** This section finds the points of the rectangle. ***
		var rPts = [{x:0, y:0}, {x:0, y:0}, {x:0, y:0}, {x:0, y:0}];
		
		// First calculates the two points near the planet.
		var rLen = len * .4; // thickness of the rectangle
		rPts[0].x = sel.x + (rLen/2)*dy;
		rPts[0].y = sel.y - (rLen/2)*dx;
		rPts[1].x = sel.x - (rLen/2)*dy;
		rPts[1].y = sel.y + (rLen/2)*dx;
		
		// Then calculates the two points near the triangle.
		rPts[2].x = tPts[3].x - (rLen/2)*dy;
		rPts[2].y = tPts[3].y + (rLen/2)*dx;			
		rPts[3].x = tPts[3].x + (rLen/2)*dy;
		rPts[3].y = tPts[3].y - (rLen/2)*dx;
		
		return [rPts, tPts];
	};
	
	// Draws this connection on a canvas. Ignores whether this connection
	// is active or not; alse see drawActive()
	self.draw = function(ctx, view) {
		var p1 = gs.pList[self.p1];
		var p2 = gs.pList[self.p2];
		
		ctx.save();
		ctx.strokeStyle = '#F0F';
		ctx.lineWidth = 3;
		ctx.beginPath(); // You NEED THIS for it to draw successfully
		ctx.moveTo(p1.xPos - view.offsetX, p1.yPos - view.offsetY);
		ctx.lineTo(p2.xPos - view.offsetX, p2.yPos - view.offsetY);
		ctx.stroke();
		ctx.closePath();
		ctx.restore();
	};
	
	// If this connection is active, it gets drawn differently.
	self.drawActive = function(ctx, view) {
		// self.direct should be 1 (p1 selected) or 2 (p2 selected)
		if (self.direct == 0) return;
		var rPts = self.shapes[self.direct].rPts;
		var tPts = self.shapes[self.direct].tPts;
		
		// Set the style properties (differs depending on whether this
		// connection is friendly or hostile).
		ctx.fillStyle = (self.status == 1 ? '#0F3' : '#F30');
		ctx.strokeStyle = (self.status == 1 ? '#0A1' : '#A10');
		ctx.lineWidth = 3;
		
		// Draw the rectangle first.
		ctx.beginPath();
		ctx.moveTo(rPts[0].x - view.offsetX, rPts[0].y - view.offsetY);
		ctx.lineTo(rPts[1].x - view.offsetX, rPts[1].y - view.offsetY);
		ctx.lineTo(rPts[2].x - view.offsetX, rPts[2].y - view.offsetY);
		ctx.lineTo(rPts[3].x - view.offsetX, rPts[3].y - view.offsetY);
		ctx.lineTo(rPts[0].x - view.offsetX, rPts[0].y - view.offsetY);
		ctx.fill();
		ctx.stroke();
		ctx.closePath();
		
		// Draw the triangle by cycling through all 3 points
		ctx.beginPath();
		ctx.moveTo(tPts[0].x - view.offsetX, tPts[0].y - view.offsetY);
		ctx.lineTo(tPts[1].x - view.offsetX, tPts[1].y - view.offsetY);
		ctx.lineTo(tPts[2].x - view.offsetX, tPts[2].y - view.offsetY);
		ctx.lineTo(tPts[0].x - view.offsetX, tPts[0].y - view.offsetY);
		ctx.fill();
		ctx.stroke();
		ctx.closePath();
	};
	
	// Basic setup
	var conStr = el.childNodes[0].data;
	var connects = conStr.split(',');
	self.p1 = connects[0];
	self.p2 = connects[1];
	self.direct = 1; // 0 => inactive; 1 => p1 active; 2 => p2 active
	self.status = 0; // 1 => friendly connection; 2 => hostile; 0 => uninitialized
};
var Gamestate = function() {
	var self = this;
	
	// Increments the turn counter.
	self.nextTurn = function() {
		// Finds the next valid active player
		self.activePlayer++;
		while (self.playerList[self.activePlayer] != 0)
			self.activePlayer++;
		
		// Increments the turn counter
		self.turnNumber++;
		
		// Increments the cycle number (in theory)
		if (self.activePlayer == self.playerList[1])
			self.cycleNumber++;
	};
	
	// Returns the Gamestate as a giant string mess. When do we use this? I don't know.
	self.toString = function() {
		// First, the Gamestate itself.
		var gs_str = ("Current Gamestate is as follows:\n" +
			"--------------------------------\n");
		gs_str += ("Turn Number: " + self.turnNumber +
			", Cycle Number: " + self.cycleNumber + "\n");
		gs_str += "Active Player: " + self.activePlayer + "\n";
		
		// Then, planets...
		var planet_str = ("\nList of Planets:\n" +
			"--------------------------------\n");
		for (var i = 1; i < self.pList.length; i++)
			planet_str += self.pList[i].toString() + "\n";
                
                // ... connections...
                var connect_str = ("\nList of Connections:\n" +
                	"--------------------------------\n");
                for (var i = 1; i < self.cList.length; i++)
                	connect_str += self.cList[i].toString() + "\n";
                
                // ... and regions.
                var region_str = ("\nList of Regions:\n" +
                	"--------------------------------\n");
                for (var i = 1; i < self.rList.length; i++)
			region_str += self.rList[i].toString() + "\n";
                
                result = (gs_str + planet_str + connect_str + region_str +
                	"--------------------------------\n");
                return result;
	};
	
	// Returns a deep copy of this Gamestate.
	self.copy = function() {
		var gs = new Gamestate();
		gs.activePlayer = self.activePlayer;
		gs.turnNumber = self.turnNumber;
		gs.cycleNumber = self.cycleNumber;
		gs.playerList = self.playerList.slice(0);
		gs.pList = self.pList.slice(0);
		gs.cList = self.cList.slice(0);
		gs.rList = self.rList.slice(0);
		return gs;
	};
	
	// Updates the owners of all Regions.
	self.updateRegions = function() {
		var testOwner;
		var j = 1; // planet ID to be checked
		for (var i = 1; i < self.rList.length; i++) {
			testOwner = -1;
			while (self.rList[i].members[ j ] ) {
				var currOwner = self.pList[j].owner;
				if (testOwner == -1)
					testOwner = currOwner;
				else if (testOwner != currOwner)
					testOwner = 0;
				j++; // check next planet
			}
			
			self.rList[i].owner = testOwner;
		}
	};
	
	// Updates the status of all Connections.
	self.updateConnections = function() {
		for (var i = 1; i < self.cList.length; i++) {
			var con = self.cList[i];
			if (self.pList[con.p1].owner == self.pList[con.p2].owner)
				con.status = 1; // indicates friendly connection
			else
				con.status = 2; // indicates hostile connection
		}
	};
	
	// Updates this Gamestate based on a Gamechange.
	self.update = function(change) {
		self.turnNumber = change.turnNumber;
		self.cycleNumber = change.cycleNumber;
		self.activePlayer = change.activePlayer;
		for (var i = 0; i < change.changes.length; i++) {
			var p = self.pList[change.changes[i][0]];
			p.owner = change.changes[i][1];
			p.numFleets = change.changes[i][2];
		}
		// 5. Set player colors - HIGHLY PRELIMINARY
		for (var i = 1; i < self.pList.length; i++)
			self.pList[i].color = ( (self.pList[i].owner == 1) ? 'cyan' : 'yellow');
		self.updateRegions();
		self.updateConnections();
	};
	
	// Returns the number of fleets the given player can deploy.
	self.getPlayerQuota = function(playerID) {
		var quota = 5;
		for (var i = 1; i < self.rList.length; i++)
			if (self.rList[i].owner == playerID)
			quota += self.rList[i].value;
		return quota;
	};
	
	// Updates all connections' states to reflect the currently selected planet.
	self.setActivePlanet = function(selectID) {
		for (var i = 1; i < self.cList.length; i++) {
			var con = self.cList[i];
			if (con.p1 == selectID)
				con.direct = 1;
			else if (con.p2 == selectID)
				con.direct = 2;
			else
				con.direct = 0;
		}
	};
	
	// Loads a Gamestate based on an XML string.
	self.loadXML = function(xmlString) {
		if (window.DOMParser) { // i.e. is it Firefox or Chrome
			parser = new DOMParser();
			xmlDoc = parser.parseFromString(xmlString, "text/xml");
		} else {
			alert("XML parser not found!");
			return;
		}
		
		// 1. Load Player data.
		var players = xmlDoc.getElementsByTagName("Players")[0];
		self.activePlayer = Number(players.getAttribute("activePlayer"));
		self.turnNumber = Number(players.getAttribute("turnNumber"));
		self.cycleNumber = Number(players.getAttribute("cycleNumber"));
		
		// 2. Load Planet data.
		var planetListEl = xmlDoc.getElementsByTagName("PlanetList")[0];
		var planetList = planetListEl.getElementsByTagName("Planet");
		for (var i = 0; i < planetList.length; i++)
			self.pList.push(new Planet(planetList[i]));
		
		// 3. Load Connection data.
		var conListEl = xmlDoc.getElementsByTagName("ConnectionList")[0];
		var conList = conListEl.getElementsByTagName("connection");
		for (var i = 0; i < conList.length; i++) {
			var con = new Connection(conList[i]);
			con.findAllShapes(self.pList);
			self.cList.push(con);
		}
		
		// 4. Load Region data.
		var regionListEl = xmlDoc.getElementsByTagName("RegionList")[0];
		var regionList = regionListEl.getElementsByTagName("Region");
		for (var i = 0; i < regionList.length; i++)
			self.rList.push(new Region(regionList[i]));
		
		// 5. Set player colors - HIGHLY PRELIMINARY
		for (var i = 1; i < self.pList.length; i++)
			self.pList[i].color = ( (self.pList[i].owner == 1) ? 'cyan' : 'yellow');
		
		self.updateConnections();
	};
	
	// Sets the active player. Prints an error if the ID provided is invalid.
	self.setActivePlayer = function(id) {
		if (!(id in self.getActivePlayers()))
			alert("Error: invalid player number.");
		else
			self.activePlayer = id;
	};
	
	// Default setup. Sets all fields to default values.
	self.playerList = [0];
	self.activePlayer = 0;
	self.turnNumber = 0;
	self.cycleNumber = 0;
	self.pList = [null];
	self.rList = [null];
	self.cList = [null];
};
var Gamechange = function() {
	var self = this;
	
	// Returns this object as a string.
	self.toString = function() {
		result = ("Gamechange:\n" + "-----------\n")
		result += ("Turn Number: " + self.turnNumber + ", Cycle Number: " +
			self.cycleNumber + "\nActive Player: " + self.activePlayer +"\n")
		result += ("\nList of changes:\n"+ "----------------\n")
		for (var i = 0; i < self.changes.length; i++)
			result += self.changes[i] + "\n";
		
		return result
	};
	
	// Loads a Gamechange from XML.
	self.loadXML = function(xmlString) {
		if (window.DOMParser) { // i.e. is it Firefox or Chrome
			parser = new DOMParser();
			xmlDoc = parser.parseFromString(xmlString, "text/xml");
		} else {
			alert("XML parser not found!");
			return;
		}
		
		// Load player data...
		var players = xmlDoc.getElementsByTagName("Players")[0];
		self.activePlayer = Number(players.getAttribute("activePlayer"));
		self.turnNumber = Number(players.getAttribute("turnNumber"));
		self.cycleNumber = Number(players.getAttribute("cycleNumber"));
		
		// ...and the change list.
		var planetListEl = xmlDoc.getElementsByTagName("Planets")[0];
		var changeList = planetListEl.getElementsByTagName("Planet");
		for (var i = 0; i < changeList.length; i++) {
			var change = changeList[i];
			var idNum = Number(change.getAttribute("idNum"));
			var owner = Number(change.getAttribute("owner"));
			var numFleets = Number(change.getAttribute("numFleets"));
			self.changes.push( [idNum, owner, numFleets] );
		}
	};
	
	// Default setup. Initializes all fields to default values.
	self.activePlayer = 0;
	self.turnNumber = 0;
	self.cycleNumber = 0;
	self.changes = [];
};
var Move = function(playerID) {
	var self = this;
	
	// Returns this Move as a string.
	self.toString = function() {
		var result = self.playerID + '/';
		for (var i = 0; i < self.moves.length; i++) {
			var m = self.moves[i];
			result += m[0] + ':' + m[1] + ':' + m[2] + '/'; 
		}
		return result;
	};
	
	// Adds a move to this Move object.
	self.addMove = function(sourceID, destID, numFleets) {
		self.moves.push( [sourceID, destID, numFleets] );
	};
	
	// Clears all moves from this object.
	self.clear = function() {
		self.moves = [];
	};
	
	// Sets fields to default values.
	self.playerID = playerID;
	self.moves = [];
};
/***********
This is a class that handles the interaction of the client with the server.

@author Alana
*/

var Client = function() {
	var self = this;
	//self.gs = new Gamestate();
	self.playerID = 1; //the human player is always player 1
	self.request;	//this is the xmlHTTP request, which is reinstantiated every time
	self.serverIPandPort = "localhost:12345"; //CHANGE THIS!!!
	self.deployment = true; //for move states
	self.count = 0; //for counting up to quota
	self.currentMove = new Move(self.playerID);
	
	// This function connects to the server and defines a game
	// based on the parameters chosen by the user.
	
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
		self.request.open("POST", "http://" + self.serverIPandPort + "/definegame/", true)
			self.request.send(definition);
			
			self.request.onreadystatechange=function()
			{
				if (self.request.status==200 && self.request.readyState == 4) {
					response = self.request.responseText;
					window.localStorage.setItem("gsString", response);
					location.href = "gamepage.html";
				} else if (self.request.status != 200) {
					if(confirm("A connection to the server could not be established.\n Try again?"))
						self.connect();
				}
			}

		}
	
	// A round of requests, that is, make a move if it's our turn, if not,
	// request a gamechange.
	
	self.go = function(){
		//if it's not our turn, send a gamechange request
		if(gs.activePlayer != self.playerID) {
			self.request = new XMLHttpRequest();
			self.request.open("POST", "http://" +self.serverIPandPort + "/gamechange/", true);
			self.request.send(self.playerID);
			self.request.onreadystatechange=function() {
				if (self.request.status==200 && self.request.readyState == 4) {
					response = self.request.responseText;
					self.dealWithResponse(response);
				} else if (self.request.status != 200) {
					alert("Response status: " + self.request.status);
					if(confirm("We did not successfully receive the gamechange.\n Try again?"))
					self.go();
				}
			}
		}
		//if it is, everything will wait on the user to click the
		//"Submit" button, which will cause a move to be made, and the move is automatically
		//in deployment phase
	}
	
	// Deal with responses from server
	self.dealWithResponse = function(res) {
		if(res == "eliminated")
			alert("Sorry, you lost.");
		else if (res == ("winner:" + self.playerID))
			alert("You have conquered all the planets!");
		
		var gc = new Gamechange();
		gc.loadXML(res);
		gs.update(gc);
	}
	
	self.deploy = function(source) {
		//see if the planet we clicked on is one of our own
		//if not, just ignore the click
		var planet = gs.pList[source];
		if(planet.owner != self.playerID) 
			return;
				
		//self.deployment is true; set this to false if quota expended or the user ends the phase
		var quota = gs.getPlayerQuota(self.playerID);
		
		if(self.deployment) { 
			//display a pop-up and get number of fleets
			var fleets = prompt("Enter number of fleets to deploy to " + planet.name);
			
			if(fleets == null)
				return;
			
			fleets = Number(fleets);
			
			if(isNaN(fleets)){
				alert("ENTER A NUMBER DUMMY!");
				return;
			}
			
			if(fleets > quota || fleets < 1) {
				alert("You must deploy between 1 and " + quota + " fleets.");
				return;
			}
			
			self.count += fleets;
			planet.numFleets += fleets;
			
			self.currentMove.addMove(0, source, fleets);
			
			document.getElementById("move_list").innerHTML += 
			("Deployed " + fleets + " fleets to " + planet.name + "<br><br>");
			
			document.getElementById("footer").innerHTML = "Click on another planet to deploy more fleets, " +
				"or click End Deployment to move to attack phase. " +
				"<br>Remaining fleets: " + (quota - self.count);
		}
		
		if(self.count == quota)
			self.endDeploy();
	}
	
	self.endDeploy = function() {
		self.deployment = false;
		self.count = 0;
		
		document.getElementById("submitButton").value = "Submit Move";
		document.getElementById("submitButton").onclick = client.submitMove;
		
		document.getElementById("footer").innerHTML = "Click on a planet you own to see connected planets.<br>" +
			"Click on an arrow to attack.";
	}
	
	self.addMove = function(connection) {			
		var source, dest;
		if(connection.direct == 1) {
			source = connection.p1;
			dest = connection.p2;
		}
		else if(connection.direct == 2) {
			source = connection.p2;
			dest = connection.p1;
		}
		
		if(gs.pList[source].owner != self.playerID)
			return; //do nothing
		
		var fleets;
		if(connection.status == 1) 
			fleets = prompt("Enter number of fleets to use to reinforce " + gs.pList[dest].name);
		else
			fleets = prompt("Enter number of fleets to use to attack " + gs.pList[dest].name);
		
		if(fleets == null)
			return;
		
		fleets = Number(fleets);
		
		if(isNaN(fleets)){
			alert("ENTER A NUMBER DUMMY!");
			return;
		}
		
		if(fleets > gs.pList[source].numFleets) {
			document.getElementById("footer").innerHTML = "Not enough fleets on " + gs.pList[source].name;
			return;
		} else
			gs.pList[source].numFleets -= fleets;
		
		self.currentMove.addMove(source, dest, fleets);
		
		if(connection.status == 1) {
			document.getElementById("move_list").innerHTML += 
				("Reinforce " + gs.pList[dest].name + " with " + fleets + " fleets <br><br>");
		} else {
			document.getElementById("move_list").innerHTML += 
				("Attack " + gs.pList[dest].name + " with " + fleets + " fleets <br><br>");
		}
		
	}
	
	self.submitMove = function() {
		self.request = new XMLHttpRequest();
		self.request.open("POST", "http://" + self.serverIPandPort + "/move/", true)
		var move = self.currentMove.toString();
		self.request.send(move);
		
		self.request.onreadystatechange=function() {
			if (self.request.status==200 && self.request.readyState == 4) {
				response = self.request.responseText;
				self.dealWithResponse(response);
				self.go();
			} else if (self.request.status != 200) {
				if(confirm("We did not successfully receive the gamechange.\n Try again?"))
				self.submitMove();
			}
		}
		
		// Reset for deployment
		self.deployment = true;
		self.currentMove.clear();
		document.getElementById("submitButton").value = "End Deployment";
		document.getElementById("submitButton").onclick = client.endDeploy;
		
		document.getElementById("footer").innerHTML = "Click on another planet to deploy more fleets, " +
				"or click End Deployment to move to attack phase. " +
				"<br>Remaining fleets: " + (gs.getPlayerQuota(self.playerID));
				
		document.getElementById("move_list").innerHTML = "<b>Player Controls</b> <br>" +
			"<b>_____________________________________</b><br><br>";
	}
};


