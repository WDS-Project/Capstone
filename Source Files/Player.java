
/**
 * This class is a representation of a Player to the Engine,
 * either human or AI.
 * @author Alana Weber
 */

public class Player {
	private int ID;
	private int status;
	private int[] cards = new int[4]; // card count per type

	/**
	 * Constructor for Player
	 * @param id  ID for Player
	 */
	public Player(int id) {
		ID = id;
		status = 1; // Player is active by default
		cards[0] = 0; // Wildcard card
		cards[1] = 0; // Type 1 card
		cards[2] = 0; // Type 2 card
		cards[3] = 0; // Type 3 card
	}

	/**
	 * Getters and setters 
	 */
	public int getID() { return ID; }
	public int getStatus() { return status; }
	public void setStatus(int i) { status = i; }
	public void addCards(int type, int count) { cards[type] += count; }
	public void removeCards(int type, int count) { cards[type] -= count; }
	public int[] getCards() { return cards; }
}

