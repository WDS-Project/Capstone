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
	
	// Getters & Setters
	/** Returns the unique ID of this region. */
	public int getID() { return idNum; }
	/** Returns the list of members of this region. */
	public int[] getMembers() { return members; }
	/** Returns the value (number of bonus fleets) for this region. */
	public int getValue() { return value; }
	/** Sets the owner of this region. (Note: 0 = unowned.) */
	public void setOwner(int owner) { this.owner = owner; } 
	
	// Other
	/** Returns true if the given planet is a member of this region. */
	public boolean isMember(int planetID) {
		for (int i = 0; i < members.length; i++)
			if (planetID == members[i])
				return true;
		
		// planet not found
		return false;
	}
}
