import java.util.*;
import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CyclicBarrier;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.TransformerException;

/** 
 * Contains methods and data pertaining to running a game. As you might
 * expect, there are a lot of them.
 * 
 * @author WDS Project
 *
 */
public class GameEngine {
	/*** Fields ***/
	private Gamestate gs,
	originalGS;
	private GameChange change;
	// For players, it's an <IP:ID, Player object> map
	private TreeMap<String, Player> players;
	private CyclicBarrier roundBegin,
	roundEnd;
	private boolean randomize = true; // Flag to disable RNG for testing

	private int ID = -1;

	private boolean inProgress = false; 

	/*** Methods ***/
	// Constructor, I guess? Also related init methods.
	public GameEngine(int id) {
		// TODO Figure out what we need to go here.
		//Not much really ... The Players and Gamestate will be defined after
		//the Engine is initialized by calling methods.
		init();
		ID = id;
		System.out.println("This engine's ID number is " + id);
	}

	/** Initialize (or reinitialize) the engine. */
	private void init() {
		players = new TreeMap<String, Player>();
		// Note that the engine is unusable until players are defined.
	}

	/** Loads a Gamestate into memory for this game. */
	public void loadGamestate(String xmlPath) throws Exception {
		gs = new Gamestate(xmlPath);
		originalGS = gs.copy();
	}
	/** Resets the current Gamestate to the last Gamestate that was loaded. */ 
	public void resetGame() throws Exception { gs = originalGS.copy(); }

	// Getters & Setters
	/**
	 * Defines a Player based on an IP address and ID. This adds the player to the Player
	 * pool with a given status and increments the player pool. Note that if you
	 * try to add a duplicate, it return null.
	 * 
	 * @param IPandID   String like this: IP:ID
	 * @return the Player object that was added; null otherwise
	 */
	public Player definePlayer(String IPandID, int status) {
		// Ignore duplicate entries
		if (players.containsKey(IPandID)) return null;

		// Otherwise, add a new Player. The new Player's ID is the next one in line.
		Player newP = new Player(getNextPlayerID());
		newP.setStatus(status);
		players.put(IPandID, newP);
		//changePlayerPopulation(players.size());
		return newP;		
	}

	/**
	 * Returns the next Player ID in line. Players start at ID 1.
	 * This is in a separate method to facilitate making the IP:ID
	 * String situation.
	 * @return 
	 */
	public int getNextPlayerID() {
		return players.size() + 1;
	}

	/**Returns this session's ID.*/
	public int getID() { return ID; }

	/**Returns the current Gamestate as XML.*/
	public String getGameStateAsXML() { return gs.writeToXML(); }

	/** Returns the Player associated with a given IP address, or null if there
	 * is no player associated with that address.
	 * 
	 * @param ipAddress the address of the Player for which to search
	 * @return the Player object if found; null otherwise
	 */
	public Player findPlayer(String IPandID) {
		if (players.containsKey(IPandID))
			return players.get(IPandID);
		else
			return null;
	}
	/** Returns the player with the given ID number, which is a primary key like
	 * IP address. It returns null if there is no such player.
	 * @param idNum
	 * @return
	 */
	public Player findPlayer(int idNum) throws Exception {
		if (players.size() > idNum) return null;

		Set<String> keys = players.keySet();
		for(Iterator<String> i = keys.iterator(); i.hasNext(); ) {
			String s = i.next();
			if (players.get(s).getID() == idNum)
				return players.get(s);
		}

		// If we get here, there's a problem with our player ID numbers.
		System.out.println("Player not found.");
		throw new Exception("Error: Player ID not found... but should have been.");
	}
	/** Returns the latest GameChange. */
	public GameChange getChange() { return change; }
	/** Returns the number of players in this game session.*/
	public int getNumPlayers() { return players.size(); }
	/** Sets random combat calculation mode. */
	public void setRandomize(boolean r) { randomize = r; }

	// Game-related methods	
	/**
	 * Calculates the result of combat between two opposing forces.
	 * 
	 * @param sourceFleets the number of attacking fleets
	 * @param destFleets the number of defending fleets
	 * @return an array containing the number of fleets remaining for [source,
	 *    dest]. Note that (source + dest) > 0, and if dest = 0, then the
	 *    planet in question changes ownership.
	 */
	public static int[] processAttack(int sourceFleets, int destFleets, boolean randomize) {
		// Special settings for testing purposes: subtraction only
		if (!randomize) {
			if (sourceFleets > destFleets)
				return new int[] {(sourceFleets - destFleets), 0};
			else if (sourceFleets < destFleets)
				return new int[] {0, (destFleets - sourceFleets)};
			else
				return new int[] {1, 1}; // a draw
		}

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
		if (gs.getActivePlayers().length == 1) return gs.getActivePlayers()[0];
		else return -1;
	}

	// Server-related methods
	/**
	 * Process a move coming from a Player.
	 * 
	 * @param move the move from some player
	 * @return a GameChange describing the changes made by the Move
	 */
	public void processMove(Move move) {
		System.out.println("Processing move.");
		GameChange gc = new GameChange(gs.getActivePlayer(),
				gs.getTurnNumber(), gs.getCycleNumber());

		// Check that the player who submitted the move is the active player.
		// Then, as long as activePlayer is right, the playerID must be valid.
		if (move.getPlayerID() != gs.getActivePlayer()) {
			throw new RuntimeException("Player "+move.getPlayerID()+" tried to move, but the active"
					+" player is "+gs.getActivePlayer()+".");
		}

		//Hacker check: Make sure no one submitted a Move with the correct
		//ID and the wrong IP.
		if(findPlayer(move.getIP()+":" + move.getPlayerID()) == null) {
			throw new RuntimeException("Who are you and why are you submitting moves?!");
		}

		// loop through the mini Moves
		while(move.hasNext()) {
			int[] miniMove = move.next();

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

			// Check that the two planets in question are, in fact, connected.
			if (!gs.isConnected(source.getIDNum(), dest.getIDNum())) {
				System.out.println("Invalid move.");
				throw new RuntimeException("Invalid move: planet "+source.getIDNum()+" and "+
						dest.getIDNum()+" are not connected.");
			}

			// 2. If Source owner == Dest owner --> Reinforcement
			if(source.getOwner() == dest.getOwner()) {
				source.addFleets((-1)*numFleets);
				dest.addFleets(numFleets);
				gc.addChange(source);
				gc.addChange(dest);
			}
			// 3. Otherwise --> Attack. Two cases: attacker victory, or not.
			else {
				int[] results = processAttack(numFleets, dest.getFleets(), randomize);
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
		if(winner > 0)
			endGame(winner);

		// Store the new GameChange
		change = gc;
		// update the Gamestate
		gs.update(change);
		System.out.println("Done processing move.");
	} // end processMove()

	/**
	 * Process the request for a player, synchronizing with the other players in the round.
	 * This is intended to be called only from Player.synchronizedRequest();
	 * @throws Exception if something goes wrong with the synchronization
	 */
	protected void synchronizedRequest() throws Exception {
		// Wait for all the players to enter requests for this round (turn).
		roundBegin.await();
		// This method call sits and waits until all players have submitted their
		// requests. If the code moves beyond that line, then all players are on the
		// same page.

		// When all players have submitted their moves, executeRequests() is called
		// according to the declaration of the roundBegin barrier.

		// With that done, we wait for all the Players to report that they're finished
		// processing the last move.
		roundEnd.await();
		// Once the roundEnd barrier is overcome, we move onto the next round (turn).
	}

	/** Executes the requests of all the players. This method is highly preliminary. */
	private void executeRequests() {
		// TODO implement error handling and request checking or whatever

		/* This should actually be happening in the HandleMove handler.
		 * // First we process the move of the active player. We should probably validate this stuff somewhere.
        	Player actor = findPlayer(gs.getActivePlayer());
        	String request = actor.getRequest(); // This ought to be a Move.
        	Move m = new Move(request); // If it isn't a move, we'll get an exception.
        	processMove(m); // results are available via change */

		Set<String> keys = players.keySet();
		//If the game hasn't started yet, send everyone a Gamestate
		if(!inProgress) {
			for(Iterator<String> itKey=keys.iterator(); itKey.hasNext(); ) {
				String key = itKey.next();
				Player player = players.get(key);
				player.setResponse(gs.writeToXML()); } 
			inProgress = true; 
		}

		else {
			// If it has, send a GameChange
			for(Iterator<String> itKey=keys.iterator(); itKey.hasNext(); ) {
				String key = itKey.next();
				Player player = players.get(key);

				// Process the request for this player.
				// This would be where we process the players' requests...
				try {
					player.setResponse(change.writeToXML());
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		}

		// Now everyone's threads are released and they all move on to roundEnd.
		// The next thing to happen should be finalResultsAvailable().
	}

	/** Do whatever needs to be done to get ready for the next round (turn). */
	private void finalResultsAvailable() {
		// I don't think we actually want it to do this every time, but it's a good temporary thing.
		// If/when we start writing things to a log, this would be the place to do it.
		System.out.println(gs.toString());

		// Final part: setup for the next round.
		gs.nextTurn();
	}

	/** Adjusts the player population for players being eliminated and whatnot. */
	protected void changePlayerPopulation(int count){
		// I thought we didn't need this, but we do. It just makes two new barriers with appropriate size.
		// The CyclicBarrier constructor defines what method is run when all (count) players have submitted
		// their requests - in this case, executeRequests() and finalResultsAvailable(), respectively.
		roundBegin = new CyclicBarrier(count, new Runnable() { public void run() { executeRequests(); }});
		roundEnd = new CyclicBarrier(count, new Runnable() { public void run() { finalResultsAvailable(); }});
	}

	public void endGame(int winner) {
		//TODO decide on the protocol for ending the game.
		//This is most likely integrated with server.
	}
}
