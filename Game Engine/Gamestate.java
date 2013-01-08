import java.util.Iterator;
import java.util.TreeSet;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.*;

/** 
 * A complete Java description of the current gamestate.
 * A gamestate contains all the information needed to
 * both display the game in the GUI and play it.
 * 
 * @author Josh Polkinghorn
 */
public class Gamestate {
	/*** Fields ***/
	private int[] playerList;
	private int activePlayer,
				turnNumber;
	private Planet[] pList;
	private Region[] rList;
	private TreeSet<Connection> cList = new TreeSet<Connection>();
	
	/*** Methods ***/
	// Constructors
	/** 
	 * Default constructor. Initializes blank arrays of Planets,
	 * Regions, and players.
	 * 
	 * @param numPlanets the number of planets on this map
	 * @param numRegions the number of regions on this map
	 * @param numPlayers the total number of players in this game
	 */
	public Gamestate(int numPlanets, int numRegions, int numPlayers) {
		/* Note that I'm not 100% sure what this method would be used for
		   outside of testing purposes. You can't actually directly use the
		   pList or rList because none of the objects are initialized, but
		   it seemed like too much work to implement a whole suite of new
		   methods to build them remotely. Just wait for the XML constructor
		   to be done, really. */
		playerList = new int[numPlayers];
		for (int i = 0 ; i < numPlayers; i++)
			playerList[i] = i + 1; // because player 0 = neutral
		
		pList = new Planet[numPlanets];
		rList = new Region[numRegions];
	}
	
	/** 
	 * This method creates a gamestate based on a given XML file. For more
	 * information, see loadXML().
	 * 
	 * @param xmlPath the filename for the XML file to be read into a Gamestate 
	 */
	public Gamestate(String xmlPath) {
		loadXML(xmlPath);
	}
	
	// Getters & Setters
	/** Returns the complete list of planets in this game. */
	public Planet[] getPlanets() { return pList; }
	/** Returns a specific Planet object. */
	public Planet getPlanetByID(int planetID) { return pList[planetID]; }
	/** Returns the complete list of regions in this game. */
	public Region[] getRegions() { return rList; }
	/** Returns a specific Region object. */
	public Region getRegionByID(int regionID) { return rList[regionID]; }
	/** Returns the list of valid player ID's. */
	public int[] getPlayerList() { return playerList; }
	/** Returns the ID of the currently active player. */
	public int getActivePlayer() { return activePlayer; }
	/** Returns the current turn number. */
	public int getTurnNumber() { return turnNumber; }
	/** Sets the player ID of the current active player. Note that this 
	 * method will fail if the given ID is not on the list of players. */
	public void setActivePlayer(int playerID) { 
		for (int i = 0; i < playerList.length; i++)
			if (playerList[playerID] != 0)
				activePlayer = playerID;
	}
	/** Increments the turn counter by one. */
	public void nextTurn() { turnNumber++; }
	
	// Inner class storing the information about a connection.
	private class Connection implements Comparable{
		public int start;
		public int end;
		
		public Connection(int start, int end) {
			if (start > end) { // Swap to put in the right order
				int temp = start;
				start = end;
				end = temp;
			}
			if (start == end)
				throw new RuntimeException("Connection can't have the same start and end points.");
			this.start = start;
			this.end = end;
		}
		
		@Override
		public boolean equals(Object o) { return (compareTo(o) == 0); }
		
		public int compareTo(Object o) {
			if (o.getClass() != this.getClass())
				return -1;
			Connection other = (Connection)o;
			if (this.start != other.start)
				return (this.start - other.start);
			else if (this.end != other.end)
				return (this.end - other.end);
			return 0;
		}
		
		public String toString() {
			return "(" + start + ", " + end + ")";
		}
	}
	
	// Other methods
	/** Updates a planet after combat.
	 * @param newFleets new number of fleets 
	 * @param newOwner new owner ID
	 */
	public void updatePlanet(int planetID, int newFleets, int newOwner) {
		Planet p = pList[planetID];
		p.setFleets(newFleets);
		p.setOwner(newOwner);
	}
	
	/** 
	 * For all regions, checks to make sure that the current owner
	 * of that region does, in fact, own all the planets in the region.
	 */
	public void updateRegions() {
		for (int i = 0; i < rList.length; i++) {
			int[] members = rList[i].getMembers();
			
			// Checks the owner of the first planet in the region.
			int regionOwner = pList[members[0]].getOwner();
			for (int j = 1; j < members.length; j++) {
				if (pList[members[j]-1].getOwner() != regionOwner)
					regionOwner = 0;
			}
			
			// If all were owned by the same player, then the region is owned
			// by that player; if not, then it is unowned (player 0).
			rList[i].setOwner(regionOwner);
		}
	}
	
	/** Returns a complete String representation of the current gamestate, including 
	 * information on all Planets and Regions. */
	@Override
	public String toString() {
		// Gamestate
		String gsDescript = "Current Gamestate is as follows:\n" +
						    "--------------------------------\n" +
						    "Turn Number: " + turnNumber + "\n" +
						    "Active Player: " + activePlayer + "\n";
		// Planets
		String planetDescript = "\nList of Planets:\n" +
								"--------------------------------\n";
		for (int i = 0; i < pList.length; i++)
			planetDescript += pList[i].toString() + "\n";
		// Connections
		String connectionsDescript = "\nList of Connections:\n" +
									 "--------------------------------\n";
		for (Iterator<Connection> i = cList.iterator(); i.hasNext(); )
			connectionsDescript += i.next().toString() + "\n";
		// Regions
		String regionDescript = "\nList of Regions:\n" +
								"--------------------------------\n";
		for (int i = 0; i < rList.length; i++)
			regionDescript += rList[i].toString() + "\n";
		
		// return everything
		return gsDescript + planetDescript + connectionsDescript +
			   regionDescript + "--------------------------------";
	}
	
	/** 
	 * Verifies the validity of the current Gamestate. This includes:
	 * - All planets belong to one and only one region
	 * - All planets are owned by players that are active
	 * - All planets have fleets > 0
	 * 
	 * @return true if the Gamestate is properly built.
	 */
	public boolean verify() {
		// TODO implement
		return true;
	}

	// *** XML Methods ***	
	/**
	 * This method creates a Gamestate from an XML file according to specifications.
	 * It can be called either on a fresh Gamestate or on an existing one (in which
	 * case it will overwrite the previous version). This will completely translate
	 * the information in the XML file into a Java object.
	 * 
	 * @param xmlPath the filename for the XML file to be read into a Gamestate
	 */
	public void loadXML(String xmlPath) {
		// 1. Load XML from the file
		DocumentBuilderFactory dbFactory = DocumentBuilderFactory.newInstance();
		try {
			DocumentBuilder dBuilder = dbFactory.newDocumentBuilder();
			Document doc = dBuilder.parse(xmlPath);
			NodeList root = doc.getChildNodes().item(0).getChildNodes(); // root = <Gamestate>
			
			// 2. Players
			Node playerNode = getNode("Players", root);
			activePlayer = Integer.parseInt(getNodeAttr("activePlayer", playerNode));
			int numPlayers = Integer.parseInt(getNodeAttr("numPlayers", playerNode));
			playerList = new int[numPlayers + 1]; // because player 0 = neutral
			for (int i = 1; i < numPlayers; i++)
				playerList[i] = 1; // 1 = normal player; 0 = inactive player
			
			// 3. Planets
			Node planetNode = getNode("PlanetList", root);
			int pCount = 0;
			for (Node kid = planetNode.getFirstChild(); kid != null; kid = kid.getNextSibling())
				// For each child of the PlanetList node (i.e. for each Planet)...
				if (kid.getNodeType() == Node.ELEMENT_NODE)
					pCount++; // If it's a planet, increment our planet count by one
			pList = new Planet[pCount];
			pCount = 0;
			for (Node kid = planetNode.getFirstChild(); kid != null; kid = kid.getNextSibling())
				// Repeat, this time actually building the planets.
				if (kid.getNodeType() == Node.ELEMENT_NODE)
					pList[pCount++] = new Planet(kid); // Let the Planet build itself
			
			// 4. Connections
			Node connectNode = getNode("ConnectionList", root);
			for (Node kid = connectNode.getFirstChild(); kid != null; kid = kid.getNextSibling()) {
				if (kid.getNodeType() == Node.ELEMENT_NODE) {
					String s = kid.getTextContent();
					int start = Integer.parseInt(s.substring(0, s.indexOf(',')));
					int end = Integer.parseInt(s.substring(s.indexOf(',')+1));
					cList.add(new Connection(start, end));
				}
			}
			
			// 5. Regions - almost exactly the same as #3
			Node regionNode = getNode("RegionList", root);
			int rCount = 0;
			for (Node kid = regionNode.getFirstChild(); kid != null; kid = kid.getNextSibling())
				if (kid.getNodeType() == Node.ELEMENT_NODE)
					rCount++;
			rList = new Region[rCount];
			rCount = 0;
			for (Node kid = regionNode.getFirstChild(); kid != null; kid = kid.getNextSibling())
				if (kid.getNodeType() == Node.ELEMENT_NODE)
					rList[rCount++] = new Region(kid); // and the regions build themselves too
		
		} catch (Exception e) { e.printStackTrace(); } // end of the DocumentBuilder try/catch blocks
		updateRegions();
	} // end loadXML()
	
	// XML Helper methods
	// These helper methods came from http://www.drdobbs.com/jvm/easy-dom-parsing-in-java/231002580
	protected Node getNode(String tagName, NodeList nodes) {
	    for (int i = 0; i < nodes.getLength(); i++) {
	        Node node = nodes.item(i);
	        if (node.getNodeName().equalsIgnoreCase(tagName))
	            return node;
	    }
	    return null;
	}
	protected String getNodeAttr(String attrName, Node n) {
	    NamedNodeMap attrs = n.getAttributes();
	    for (int i = 0; i < attrs.getLength(); i++ ) {
	        Node attr = attrs.item(i);
	        if (attr.getNodeName().equalsIgnoreCase(attrName))
	            return attr.getNodeValue();
	    }
	    return "";
	}
}
