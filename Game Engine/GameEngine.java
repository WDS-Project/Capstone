import java.util.Random;

/** 
 * Contains methods and data pertaining to running a game.
 * 
 * @author Tycherin
 *
 */
public class GameEngine {
	/*** Fields ***/
	private Gamestate gs;
	// Other things go here...
	
	/*** Methods ***/
	/**
	 * Calculates the result of combat between two opposing forces.
	 * 
	 * @param sourceFleets the number of attacking fleets
	 * @param destFleets the number of defending fleets
	 * @return an array containing the number of fleets remaining for [source,
	 *    dest]. Note that (source + dest) > 0, and if dest = 0, then the
	 *    planet in question changes ownership.
	 */
	public static int[] processAttack(int sourceFleets, int destFleets) {
		boolean retreating = false; // flag for attackers to retreat
		int smaller;
		Random rand = new Random();
		int sourceOrig = sourceFleets;
		
		// Combat loop
		while (destFleets > 0 && !retreating) {
			smaller = Math.min(sourceFleets, destFleets);
			// Run one match for each pair
			int sNum, dNum;
			for (int i = 0; i < smaller; i++) {
				sNum = rand.nextInt(7);
				dNum = rand.nextInt(7);
				if (sNum > dNum)
					destFleets--;
				else if (dNum > sNum)
					sourceFleets--;
			}
			
			// Determine if the attackers retreat or not.
			// *** NOTE: This part is highly preliminary, and should be balanced thoroughly.
			if (sourceFleets * 4 < sourceOrig) { // if the attackers have lost 3/4 or more...
				if (rand.nextInt(2) == 0) // ...then there is a 50% chance of the attackers
					retreating = true;    // retreating each round.
			}
		} // end combat loop
		
		int[] result = new int[2];
		result[0] = sourceFleets;
		result[1] = destFleets;
		return result;
	}
	
}
