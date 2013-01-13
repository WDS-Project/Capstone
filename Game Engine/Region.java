import java.util.Arrays;
import org.w3c.dom.*;

/**
 * This class contains all data and methods associated with
 * one region object. A region consists mainly of a list of
 * planets determined by the map.
 * 
 * @author Josh Polkinghorn
 */
public class Region {
	/*** Fields ***/
	private int idNum,
				value,
				owner = 0;
	private String name,
				   color;
	private int[] members;
	
	/*** Methods ***/
	// Constructor
	/** Default constructor. */
	public Region(int idNum, int value, String name, String color, int[] members) {
		this.idNum = idNum;
		this.value = value;
		this.name = name;
		this.color = color;
		this.members = members;
	}
	
	/** Constructor to load a region from XML. */
	public Region(Element n) {
		loadXML(n);
	}

	// Getters & Setters
	/** Returns the unique ID of this region. */
	public int getID() { return idNum; }
	/** Returns the list of members of this region. */
	public int[] getMembers() { return members; }
	/** Returns the value (number of bonus fleets) for this region. */
	public int getValue() { return value; }
	/** Returns a String containing the name of this region. */
	public String getName() { return name; }
	/** Returns the ID of the player who owns this region. (Note: 0 = unowned.) */
	public int getOwner() { return owner; }
	/** Sets the owner of this region. (Note: 0 = unowned.) */
	public void setOwner(int owner) { this.owner = owner; } 
	
	// Other
	/** Returns true if the given planet is a member of this region. */
	public boolean hasMember(int planetID) {
		for (int i = 0; i < members.length; i++)
			if (planetID == members[i])
				return true;
		
		// planet not found
		return false;
	}
	
	/** Returns a String representation of this object, including all attributes. */
	@Override
	public String toString() {
		return "Region "+idNum+", "+name+". Color: "+color+"; value: "+value+"; owner: "+owner+
			   "; members: "+Arrays.toString(members)+".";
	}
	
	/**
	 * This method creates a Region from an XML Node according to specifications.
	 * For more information, see Gamestate.loadXML().
	 * 
	 * @param n the Region node to be read
	 */
	public void loadXML(Element n) {
		this.idNum = Integer.parseInt(n.getAttribute("idNum"));
		this.color = n.getAttribute("color");
		this.name = n.getAttribute("name");
		// owner is checked elsewhere
		this.value = Integer.parseInt(n.getAttribute("value"));
		
		// Now we build the members list.
		Node mList = n.getFirstChild();
		int mCount = 0;
		while (mList.getNodeType() != Node.ELEMENT_NODE)
			mList = mList.getNextSibling();
		for (Node kid = mList.getFirstChild(); kid != null; kid = kid.getNextSibling())
			// For each connection...
			if (kid.getNodeType() == Node.ELEMENT_NODE)
				mCount++; // If it's a planet, increment our planet count by one
		members = new int[mCount];
		mCount = 0;
		for (Node kid = mList.getFirstChild(); kid != null; kid = kid.getNextSibling())
			// Repeat, this time actually recording the members.
			if (kid.getNodeType() == Node.ELEMENT_NODE)
				members[mCount++] = Integer.parseInt(kid.getTextContent());
	}
	
	/**
	 * Given a node of an XML document, saves this Region as an
	 * XML element.
	 * 
	 * @param parentNode root node on which to save this Planet
	 */
	public void saveToXML(Node parentNode) {
		Document doc = parentNode.getOwnerDocument();
		
		Element regionNode = doc.createElement("Region");
		regionNode.setAttribute("idNum", idNum+"");
		regionNode.setAttribute("name", name);
		regionNode.setAttribute("value", value+"");
		regionNode.setAttribute("owner", owner+"");
		regionNode.setAttribute("color", color);
		
		// Create one child element for each member.
		Element membList = doc.createElement("memberList");
	    for (int i = 0; i < members.length; i++) {
	    	Element membEl = doc.createElement("member");
	    	membEl.setTextContent(members[i]+"");
	    	membList.appendChild(membEl);
	    }
	    regionNode.appendChild(membList);
		parentNode.appendChild(regionNode);
	}
}
