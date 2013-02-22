/* This is the Javascript for displaying the GUI for the WDS game.
* Also includes code for storing game data, validating moves by the player,
* loading various kinds of XML, and communication with the server.
*
* Author: WDS Project	
*/

// ********* How to load an XML string into the stuff we want. *********
// *** Step 1: Load the XML into a Javascript object. ***
// Incidentally, our target is TestGS3.xml (as always), reproduced here in glorious massive string form.
var gsString = '<?xml version="1.0" encoding="UTF-8"?><Gamestate><Players numPlayers="2" activePlayer="1" turnNumber="0" cycleNumber="0"/>' +
'<PlanetList><Planet idNum="1" name="Florida" owner="1" numFleets="5" color="#ffee33" position="35,25" radius="30" /><Planet idNum="2" name="Aruba"' +
' owner="1" numFleets="5" color="#aabbcc" position="300,50" radius="35" /><Planet idNum="3" name="Manitoba" owner="1" numFleets="5" color="#00ffaa"'+
' position="50,150" radius="25" /><Planet idNum="4" name="Sparta" owner="2" numFleets="5" color="#aa00ee" position="75,300" radius="25" /><Planet'+
' idNum="5" name="Akihabara" owner="2" numFleets="5" color="#55cc11" position="300,350"	radius="30" /></PlanetList><ConnectionList><connection>1,2</connection>'+
'<connection>1,3</connection><connection>1,4</connection><connection>1,5</connection><connection>2,3</connection><connection>2,4</connection>'+
'<connection>2,5</connection><connection>3,4</connection><connection>3,5</connection><connection>4,5</connection></ConnectionList><RegionList>'+
'<Region idNum="1" name="Eastern U.S." value="5" owner="0" color="#44aadd"><memberList><member>1</member><member>2</member><member>3</member>'+
'<member>4</member><member>5</member></memberList></Region></RegionList></Gamestate>';

var gcString = '<?xml version="1.0" encoding="UTF-8"?><GameChange><Players activePlayer="1" cycleNumber="1" turnNumber="1"/>' +
'<Planets><Planet idNum="1" numFleets="4" owner="1"/><Planet idNum="2" numFleets="7" owner="1"/><Planet idNum="4" numFleets="1" owner="2"/>' +
'</Planets></GameChange>';


// *** Step 2: Load that Javascript object into actual meaningful data structures. ***
var Planet = function(el) {
	var that = this;
	
	// Loads a planet from XML element el
	that.loadXML = function(el) {
		that.name = el.getAttribute("name");
		that.idNum = Number(el.getAttribute("idNum"));
		that.numFleets = Number(el.getAttribute("numFleets"));
		that.owner = Number(el.getAttribute("owner"));
	};
	
	// Returns this object as a string.
	that.toString = function() {
		return ("Planet " + that.idNum + ", " + that.name +
			". Owner: " + that.owner + "; number of fleets: "
			+ that.numFleets + ".");
	};
	
	// Basic setup
	if (!el) { // if el isn't defined or something
		that.name = "";
		that.idNum = 0;
		that.numFleets = 0;
		that.owner = 0;
	} else {
		that.loadXML(el);
	}
};
var Region = function(el) {
	var that = this;
	
	// Loads a region from an XML element
	that.loadXML = function(el) {
		that.name = el.getAttribute("name");
		that.idNum = Number(el.getAttribute("idNum"));
		that.value = Number(el.getAttribute("value"));
		that.owner = Number(el.getAttribute("owner"));
		var memberListEl = el.getElementsByTagName("memberList")[0];
		var memberList = memberListEl.getElementsByTagName("member");
		for (var i = 0; i < memberList.length; i++) {
			var m = memberList[i];
			that.members[Number(m.childNodes[0].data)] = true;
		}
	};
	
	// Returns this region as a string
	that.toString = function() {
		return ("Region " + that.idNum + ", " + that.name +
			". Owner: " + that.owner + "; value: " + that.value +
			". List of members: " + that.members + ".");
	};
	
	// Basic setup
	that.members = {};
	if (!el) {
		that.name = "";
		that.idNum = 0;
		that.value = 0;
		that.owner = 0;
	} else {
		that.loadXML(el);
	}
};
var Gamestate = function() {
	var that = this;
	
	// Increments the turn counter.
	that.nextTurn = function() {
		// Finds the next valid active player
		that.activePlayer++;
		while (that.playerList[that.activePlayer] != 0)
			that.activePlayer++;
		
		// Increments the turn counter
		that.turnNumber++;
		
		// Increments the cycle number (in theory)
		if (that.activePlayer == that.playerList[1])
			that.cycleNumber++;
	};
	
	// Returns the Gamestate as a giant string mess. When do we use this? I don't know.
	that.toString = function() {
		// First, the Gamestate itself.
		var gs_str = ("Current Gamestate is as follows:\n" +
			      "--------------------------------\n");
		gs_str += ("Turn Number: " + that.turnNumber +
			   ", Cycle Number: " + that.cycleNumber + "\n");
		gs_str += "Active Player: " + that.activePlayer + "\n";
		
		// Then, planets...
		var planet_str = ("\nList of Planets:\n" +
				  "--------------------------------\n");
		for (var i = 1; i < that.pList.length; i++)
			planet_str += that.pList[i].toString() + "\n";
                
                // ... connections...
                var connect_str = ("\nList of Connections:\n" +
                		   "--------------------------------\n");
                for (var i = 1; i < that.cList.length; i++)
                	connect_str += that.cList[i] + "\n";
                
                // ... and regions.
                var region_str = ("\nList of Regions:\n" +
                		  "--------------------------------\n");
                for (var i = 1; i < that.rList.length; i++)
			region_str += that.rList[i].toString() + "\n";
                
                result = (gs_str + planet_str + connect_str + region_str +
                	  "--------------------------------\n");
                return result;
	};
	
	// Returns a deep copy of this Gamestate.
	that.copy = function() {
		var gs = new Gamestate();
		gs.activePlayer = that.activePlayer;
		gs.turnNumber = that.turnNumber;
		gs.cycleNumber = that.cycleNumber;
		gs.playerList = that.playerList.slice(0);
		gs.pList = that.pList.slice(0);
		gs.cList = that.cList.slice(0);
		gs.rList = that.rList.slice(0);
		return gs;
	};
	
	// Updates the owners of all Regions.
	that.updateRegions = function() {
		var testOwner;
		for (var i = 1; i < that.rList.length; i++) {
			testOwner = -1;
			for (var j = 0; j < that.rList[i].members.length; i++) {
				var currOwner = that.rList[i].members[j];
				if (testOwner == -1)
					testowner = currOwner;
				else if (testOwner != currOwner)
					testowner = 0;
			}
			
			that.rList[i].owner = testOwner;
		}
	};
	
	// Updates this Gamestate based on a Gamechange.
	that.update = function(change) {
		that.turnNumber = change.turnNumber;
		that.cycleNumber = change.cycleNumber;
		that.activePlayer = change.activePlayer;
		for (var i = 0; i < change.changes.length; i++) {
			var p = that.pList[change.changes[0]];
			p.owner = change.changes[1];
			p.numFleets = change.changes[2];
		}
		that.updateRegions();
	};
	
	// Returns the number of fleets the given player can deploy.
	that.getPlayerQuota = function(playerID) {
		var quota = 5;
		for (var i = 1; i < that.rList.length; i++)
			if (that.rList[i].owner == playerID)
				quota += that.rList[i].value;
		return quota;
	};
	
	// Loads a Gamestate based on an XML string.
	that.loadXML = function(xmlString) {
		if (window.DOMParser) { // i.e. is it Firefox or Chrome
			parser = new DOMParser();
			xmlDoc = parser.parseFromString(xmlString, "text/xml");
		} else {
			alert("XML parser not found!");
			return;
		}
		
		// 1. Load Player data.
		var players = xmlDoc.getElementsByTagName("Players")[0];
		that.activePlayer = Number(players.getAttribute("activePlayer"));
		that.turnNumber = Number(players.getAttribute("turnNumber"));
		that.cycleNumber = Number(players.getAttribute("cycleNumber"));
		
		// 2. Load Planet data.
		var planetListEl = xmlDoc.getElementsByTagName("PlanetList")[0];
		var planetList = planetListEl.getElementsByTagName("Planet");
		for (var i = 0; i < planetList.length; i++)
			that.pList.push(new Planet(planetList[i]));
		
		// 3. Load Connection data.
		var conListEl = xmlDoc.getElementsByTagName("ConnectionList")[0];
		var conList = conListEl.getElementsByTagName("connection");
		for (var i = 0; i < conList.length; i++)
			that.cList.push(conList[i].childNodes[0].data);
		
		// 4. Load Region data.
		var regionListEl = xmlDoc.getElementsByTagName("RegionList")[0];
		var regionList = regionListEl.getElementsByTagName("Region");
		for (var i = 0; i < regionList.length; i++)
			that.rList.push(new Region(regionList[i]));
	};
	
	// Default setup. Sets all fields to default values.
	that.playerList = [0];
	that.activePlayer = 0;
	that.turnNumber = 0;
	that.cycleNumber = 0;
	that.pList = [null];
	that.rList = [null];
	that.cList = [null];
	
	// Sets the active player. Prints an error if the ID provided is invalid.
	that.setActivePlayer = function(id) {
		if (!(id in that.getActivePlayers()))
			alert("Error: invalid player number.");
		else
			that.activePlayer = id;
	};
};
var Gamechange = function() {
	var that = this;
	
	// Returns this object as a string.
	that.toString = function() {
		result = ("Gamechange:\n" + "-----------\n")
		result += ("Turn Number: " + that.turnNumber + ", Cycle Number: " +
			that.cycleNumber + "\nActive Player: " + that.activePlayer +"\n")
		result += ("\nList of changes:\n"+ "----------------\n")
		for (var i = 0; i < that.changes.length; i++)
			result += that.changes[i] + "\n";
		
		return result
	};
	
	// Loads a Gamechange from XML.
	that.loadXML = function(xmlString) {
		if (window.DOMParser) { // i.e. is it Firefox or Chrome
			parser = new DOMParser();
			xmlDoc = parser.parseFromString(xmlString, "text/xml");
		} else {
			alert("XML parser not found!");
			return;
		}
		
		// Load player data...
		var players = xmlDoc.getElementsByTagName("Players")[0];
		that.activePlayer = Number(players.getAttribute("activePlayer"));
		that.turnNumber = Number(players.getAttribute("turnNumber"));
		that.cycleNumber = Number(players.getAttribute("cycleNumber"));
		
		// ...and the change list.
		var planetListEl = xmlDoc.getElementsByTagName("Planets")[0];
		var changeList = planetListEl.getElementsByTagName("Planet");
		for (var i = 0; i < changeList.length; i++) {
			var change = changeList[i];
			var idNum = Number(change.getAttribute("idNum"));
			var owner = Number(change.getAttribute("owner"));
			var numFleets = Number(change.getAttribute("numFleets"));
			that.changes.push( [idNum, owner, numFleets] );
		}
	};
	
	// Default setup. Initializes all fields to default values.
	that.activePlayer = 0;
	that.turnNumber = 0;
	that.cycleNumber = 0;
	that.changes = [];
};
var Move = function(playerID) {
	var that = this;
	
	// Returns this Move as a string.
	that.toString = function() {
		var result = that.playerID + '/';
		for (var i = 0; i < that.moves.length; i++) {
			var m = that.moves[i];
			result += m[0] + ':' + m[1] + ':' + m[2] + '/'; 
		}
		return result;
	};
	
	that.addMove = function(sourceID, destID, numFleets) {
		move.push( [sourceID, destID, numFleets] );
	};
	
	// Sets fields to default values.
	that.playerID = playerID;
	that.moves = [];
};



var gs = new Gamestate();
gs.loadXML(gsString);
alert(gs.toString());
var gc = new Gamechange();
gc.loadXML(gcString);
alert(gc.toString());

// Other things to do:
// - Communicate with the server using XMLHttpRequests
// - Display the data we parsed through
// - Allow user input of various kinds
