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
        
        /**
         * Check to see if anyone has won the game yet.
         * @return  ID of the player who has won, or -1 if no one has
         */
        public int checkWin() {
            int winner = -1;
            
            //check to see if one Player owns all the Planets
            int candidate = gs.getPlanets()[0].getOwner(); //grab the ID of the owner of the first planet
            for(Planet p : gs.getPlanets()) {
                if (p.getOwner() == candidate) winner = candidate; //check to see if all other planets
                else winner = -1;                                   //are owned by this player
            }
            
            return winner;
            //Is there any other way someone can win??
        }
	
        /**
         * Process a move coming from a Player. Note that this is in its preliminary stages.
         * This method is really long.
         * @param move  The move from the User
         * @return 
         */
        public GameChange processMove(Move move) {
            GameChange gc = new GameChange(0,0,0); //TODO Replace these 0's with the turn variables
            
            //make sure the Player ID is valid
            boolean validPlayer = false;
            for(int p : gs.getPlayerList()) {
                if (move.getPlayerID() == p && move.getPlayerID() != 0)
                    validPlayer = true;
            }
            if(!validPlayer)
                throw new RuntimeException("Invalid player.");
            
            //TODO make sure that it is indeed that player's turn
                    
           //loop through the mini Moves
            while(move.hasNext()) {
                int[] miniMove = move.next();
                
                //validate the mini-Move
                if(miniMove.length != 3)
                    throw new RuntimeException("Invalid move.");
                
                //name variables for ease of use
                //TODO check for invalid Planet IDs
                Planet source = gs.getPlanetByID(miniMove[0]);
                Planet dest = gs.getPlanetByID(miniMove[1]);
                int numFleets = miniMove[2];
                int player = move.getPlayerID();
                
                //Source = Dest: Deployment
                if(source.getIDNum() == dest.getIDNum()) {
                    //for right now, check that the Planet is neutral
                    if(source.getOwner() != 0)
                        throw new RuntimeException("Invalid move. Attempt to deploy to non-neutral Planet.");
                    source.addFleets(numFleets);
                    source.setOwner(player);
                    gc.addChange(source);
                }                
                //Source owner = Dest owner: Reinforcement
                else if(source.getOwner() == dest.getOwner()) {
                    source.addFleets((-1)*numFleets);
                    dest.addFleets(numFleets);
                    gc.addChange(source);
                    gc.addChange(dest);
                }
                //Source != planet: Attack
                //Assume a defender victory is never possible because of the retreat policy
                else {
                    int[] results = processAttack(numFleets, dest.getFleets());
                    if(results[1] == 0) {//the attacker has won
                        dest.setOwner(source.getOwner());
                        dest.setFleets(results[0]);
                        source.addFleets((-1)*numFleets);
                        gc.addChange(source);
                        gc.addChange(dest);
                    }
                    else { //the attacker retreated
                        source.setFleets(results[0]);
                        dest.setFleets(results[1]);
                        gc.addChange(source);
                        gc.addChange(dest);
                    }
                }
                
            }
            
            int winner = checkWin();
            //TODO what to do if someone has won? Call some sort of endGame() method
            
            //update the Gamestate
            gs.update(gc);
            
            return gc;
        }
}
