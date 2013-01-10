import org.w3c.dom.*;

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
	
	/*** Functions ***/
	// Constructor
	/** Default constructor. */
	public Planet(int idNum, String color, String name, int xPos, int yPos, int radius) {
		this.idNum = idNum;
		this.color = color;
		this.name = name;
		this.xPos = xPos;
		this.yPos = yPos;
		this.radius = radius;
	}
	
	/** Constructor to load a planet from XML. */
	public Planet(Element n) {	
		loadXML(n);
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
	
	/** Changes the owner of this planet. Note that this method will not
	 * check whether the new owner is a valid player ID or not.
	 * 
	 * @param o ID of the new owner
	 */
	public void setOwner(int o) { owner = o; }
	
	/** Sets the number of fleets on this planet to a specific number.
	 * @param newFleets new total number of fleets on this planet  */
	public void setFleets(int newFleets) { numFleets = newFleets; }
	
	/** Adds a given number of fleets to this planet. To subtract,
	 * add a negative number of fleets. Note that if numFleets has
	 * a minimum value of 1.
	 * 
	 * @param plusFleets the number of fleets to add
	 */
	public void addFleets(int plusFleets) {
		numFleets += plusFleets;
		if (numFleets < 1)
			numFleets = 1;
	}
	
	// Other
	/** Returns a string representation of this object, including all attributes. */
	@Override
	public String toString() {
		return "Planet " + idNum + ", " + name + ". Position: ("+xPos+", "+yPos+"); color: "+color
			+"; radius: "+radius+"; owner: "+owner+"; number of fleets: "+numFleets
			+".";
		//return "Hi I am a planet.";
	}
	
	/**
	 * This method creates a Planet from an XML Node according to specifications.
	 * For more information, see Gamestate.loadXML().
	 * 
	 * @param n the Planet node to be read
	 */
	public void loadXML(Element n) {
		this.idNum = Integer.parseInt(n.getAttribute("idNum"));
		this.color = n.getAttribute("color");
		this.name = n.getAttribute("name");
		String position = n.getAttribute("position");
		int mPos = position.indexOf(',');
		this.xPos = Integer.parseInt(position.substring(0, mPos));
		this.yPos = Integer.parseInt(position.substring(mPos+1));
		this.owner = Integer.parseInt(n.getAttribute("owner"));
		this.numFleets = Integer.parseInt(n.getAttribute("numFleets"));
		this.radius = Integer.parseInt(n.getAttribute("radius"));
	}
	
	/**
	 * Given a node of an XML document, saves this Planet as an
	 * XML element.
	 * 
	 * @param parentNode root node on which to save this Planet
	 */
	public void saveToXML(Node parentNode) {
		Document doc = parentNode.getOwnerDocument();
		
		Element planetNode = doc.createElement("Planet");
		planetNode.setAttribute("idNum", idNum+"");
		planetNode.setAttribute("color", color);
		planetNode.setAttribute("name", name);
		planetNode.setAttribute("position", xPos + "," + yPos);
		planetNode.setAttribute("owner", owner+"");
		planetNode.setAttribute("numFleets", numFleets+"");
		planetNode.setAttribute("radius", radius+"");
		
		parentNode.appendChild(planetNode);
	}
}
