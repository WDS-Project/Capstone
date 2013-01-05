/**
 * This class contains all data and methods associated with
 * one planet object. There are two main sets of data: graphical
 * data, which is used by the client GUI, and game data, which
 * is used in playing the game itself.
 * 
 * @author Josh Polkinghorn
 */
public class Planet {
	/*** Fields ***/
	// Graphical data
	private int xPos,
				yPos,
				radius;
	private String color;
	
	// Game data
	private String name;
	private int idNum,
				numFleets,
				owner = 0;
	private int[] connections;
	
	/*** Functions ***/
	// Constructor
	/** Default constructor. */
	public Planet(int idNum, String color, int xPos, int yPos, int radius, int[] connections) {
		this.idNum = idNum;
		this.color = color;
		this.xPos = xPos;
		this.yPos = yPos;
		this.radius = radius;
		this.connections = connections;
	}
	
	// Getters & Setters
	/** Returns the number of troops on this planet. */
	public int getFleets() { return numFleets; }
	/** Returns the name of this planet. */
	public String getName() { return name; }
	/** Returns this planet's unique ID number. */
	public int getIDNum() { return idNum; }
	/** Returns the ID number of the player who owns this planet. */
	public int getOwner() { return owner; }
	/** Returns the x position of this planet. */
	public int getXPos() { return xPos; }
	/** Returns the y position of this planet. */
	public int getYPos() { return yPos; }
	/** Returns the list of connected planets. */
	public int[] getConnections() { return connections; }
	
	/** Changes the owner of this planet. Note that this method will not
	 * check whether the new owner is a valid player ID or not.
	 * 
	 * @param o ID of the new owner
	 */
	public void setOwner(int o) { owner = o; }
	
	/** Sets the number of fleets on this planet to a specific number.
	 * 
	 * @param newFleets new total amount of fleets on this planet 
	 * @return true if newFleets is a valid number of fleets
	 */
	public boolean setFleets(int newFleets) { 
		numFleets = newFleets;
		return numFleets > 0;
	}
	
	/** Adds a given number of fleets to this planet. To subtract,
	 * add a negative number of fleets.
	 * 
	 * @param plusFleets the number of fleets to add
	 * @return true if the new total is greater than 0
	 */
	public boolean addFleets(int plusFleets) {
		numFleets += plusFleets;
		return numFleets > 0;
	}
	
	// Other
	/** Checks if this planet is connected to some neighbor.
	 * 
	 * @param neighborID ID number of potential neighbor planet
	 * @return true if this planet is connected to given planet
	 */
	public boolean isConnected (int neighborID) {
		for (int i = 0; i > connections.length; i++)
			if (connections[i] == neighborID)
				return true;
		
		// neighbor not found
		return false;
	}
}
