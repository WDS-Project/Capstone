import java.util.Random;

/** 
 * Contains methods and data pertaining to running a game. As you might
 * expect, there are a lot of them.
 * 
 * @author WDS Project
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
		
		return new int[] {sourceFleets, destFleets};
	}
        
        /**
         * Check to see if anyone has won the game yet.
         * @return  ID of the player who has won, or -1 if no one has
         */
        public int checkWin() {
        	// Special case: if only one player is left, that player wins by default.
        	// As long as players are turned inactive when they lose all their planets,
        	// this method is completely reliable. (Use Gamestate.checkPlayerStatus(); )
        	if (gs.getActivePlayers().length <= 1) return gs.getActivePlayers()[0];
        	else return -1;
        }
	
        /**
         * Process a move coming from a Player. Note that this is in its preliminary stages.
         * This method is really long.
         * 
         * @param move the move from some player
         * @return a GameChange describing the changes made by the Move
         */
        public GameChange processMove(Move move) {
            GameChange gc = new GameChange(0,0,0); //TODO Replace these 0's with the turn variables
            
            // make sure the Player ID is valid
            /* boolean validPlayer = false;
            for(int p : gs.getActivePlayers()) {
                if (move.getPlayerID() == p && move.getPlayerID() != 0)
                    validPlayer = true;
            }
            if(!validPlayer)
                throw new RuntimeException("Invalid player."); */
            // Actually, let's just check that the player who submitted the move is the active
            // player. Then, as long as activePlayer is right, the player must be active.
            if (move.getPlayerID() != gs.getActivePlayer())
            	throw new RuntimeException("That isn't the active player!");
            
            //TODO make sure that it is indeed that player's turn
            
                    
           // loop through the mini Moves
            while(move.hasNext()) {
                int[] miniMove = move.next();
                
                // validate the mini-Move
                if(miniMove.length != 3)
                    throw new RuntimeException("Invalid Move format.");
                if (miniMove[2] <= 0)
                	throw new RuntimeException("Can't move zero troops");
                
                // Grab these two, but before we can get source, we have to check case #1
                Planet dest = gs.getPlanetByID(miniMove[1]);
                int numFleets = miniMove[2];
                
                // 1. If Source == 0 --> Deployment (because planet ID's are indexed at 1,
                // so 0 means deployment because it comes from nowhere)
                if(miniMove[0] == 0) {
                	// TODO rules for deployments, like checking a player's quota
                	dest.addFleets(numFleets);
                    gc.addChange(dest);
                    continue;
                }
                Planet source = gs.getPlanetByID(miniMove[0]); // Safe to find source Planet
                              
                // 2. If Source owner == Dest owner --> Reinforcement
                if(source.getOwner() == dest.getOwner()) {
                    source.addFleets((-1)*numFleets);
                    dest.addFleets(numFleets);
                    gc.addChange(source);
                    gc.addChange(dest);
                }
                // 3. Otherwise --> Attack. Two cases: attacker victory, or not.
                else {
                    int[] results = processAttack(numFleets, dest.getFleets());
                    if(results[1] == 0) { // the attacker has won
                        dest.setOwner(source.getOwner());
                        dest.setFleets(results[0]);
                        source.addFleets((-1)*numFleets);
                        gc.addChange(source);
                        gc.addChange(dest);
                    } else { // the attacker retreated (or all died, I suppose)
                        source.addFleets(results[0] - numFleets);
                        dest.setFleets(results[1]);
                        gc.addChange(source);
                        gc.addChange(dest);
                    }
                }
            } // end miniMove loop
            
            int winner = checkWin();
            //TODO what to do if someone has won? Call some sort of endGame() method
            
            // update the Gamestate
            gs.update(gc);
            
            return gc;
        }
}
