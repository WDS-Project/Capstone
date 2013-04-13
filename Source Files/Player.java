
/**
 * This class is a representation of a Player to the Engine,
 * either human or AI.
 * @author Alana Weber
 */

public class Player {
	private int ID;
	private int status;
	private int cardCount = 0;
	private int[] cards = new int[3]; // card count per type
	public static final int MAX_CARDS = 5;

	/**
	 * Constructor for Player
	 * @param id  ID for Player
	 */
	public Player(int id) {
		ID = id;
		status = 1; // Player is active by default
		cards[0] = 0; // Type 0 card
		cards[1] = 0; // Type 1 card
		cards[2] = 0; // Type 2 card
	}

	// Getters and setters 
	public int getID() { return ID; }
	public int getStatus() { return status; }
	public void setStatus(int i) { status = i; }
	public void addCards(int type, int num) {
		cards[type] += num;
		cardCount += num;
	}
	public void removeCards(int type, int num) {
		cards[type] -= num;
		cardCount -= num;
	}
	public int[] getCards() { return cards; }
	public int getCardCount() { return cardCount; }
}

