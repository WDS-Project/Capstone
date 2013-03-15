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
	
	private int numPlayers = 0;

	//these are to figure out where we are in the game
	//in order to know what to send players in the executeRequests() method
	private final int NOT_STARTED = 1;
	private final int IN_PROGRESS = 2;
	private final int GAME_OVER = 3;

	private int stateOfGame = 1;
	private int winner = -1;

	/*** Methods ***/
	// Constructor, I guess? Also related init methods.
	public GameEngine(int id) {
		init();
		ID = id;
		numPlayers = 1;
		System.out.println("This engine's ID number is " + id);
	}

	/** Initialize (or reinitialize) the engine. */
	private void init() {
		players = new TreeMap<String, Player>();
		setRandomize(false); // *** NOTE: For testing purposes only
		// Note that the engine is unusable until players are defined.
	}

	/** Loads a Gamestate into memory for this game. */
	public void loadGamestate(String xmlPath, int numPlayers) throws Exception {
		gs = new Gamestate(xmlPath, numPlayers);
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
		int id = Integer.parseInt(IPandID.substring(IPandID.lastIndexOf(":")+1));
		Player newP = new Player(id);
		newP.setStatus(status);
		players.put(IPandID, newP);
		//Note that the player population is changed by HandleDefineGame
		//Based on the number of players the user asked to play
		return newP;		
	}

	/**
	 * Returns the next Player ID in line. Players start at ID 1.
	 * This is in a separate method to facilitate making the IP:ID
	 * String situation.
	 * @return 
	 */
	public int getNextPlayerID() {
		return ++numPlayers;
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
	public Player findPlayer(int idNum) {
		//if (players.size() > idNum) return null;

		Set<String> keys = players.keySet();
		for(Iterator<String> i = keys.iterator(); i.hasNext(); ) {
			String s = i.next();
			if (players.get(s).getID() == idNum)
				return players.get(s);
		}

		// If we get here, there's a problem with our player ID numbers.
		throw new RuntimeException("Error: Player ID not found... but should have been.");
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
	 */
	public void processMove(Move move) {
		System.out.println("Processing move.");
		GameChange gc = new GameChange();

		// Check that the player who submitted the move is the active player.
		// Then, as long as activePlayer is right, the playerID must be valid.
		if (move.getPlayerID() != gs.getActivePlayer()) {
			throw new RuntimeException("Player "+move.getPlayerID()+" tried to move, but the active"
					+" player is "+gs.getActivePlayer()+".");
		}

		// Check that the request came from the right IP address
		if(findPlayer(move.getIP()+":" + move.getPlayerID()) == null) {
			throw new RuntimeException("Move came from "+move.getIP()+", which isn't the right address.");
		}

		int quota = gs.getPlayerQuota(move.getPlayerID());

		// loop through the mini Moves
		while(move.hasNext()) {
			int[] miniMove = move.next();

			// Grab these two, but before we can get source, we have to check case #1
			Planet dest = gs.getPlanetByID(miniMove[1]);
			int numFleets = miniMove[2];

			// 1. If Source == 0 --> Deployment 
			if(miniMove[0] == 0) {
				quota -= numFleets;
				if (quota < 0)
					throw new RuntimeException("Error: quota exceeded. Quota: " + quota);
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
			
			// Check to see that there are enough fleets to complete the action.
			if (numFleets >= source.getFleets()) {
				throw new RuntimeException("Invalid move: planet " + source.getIDNum() +
					" has " + source.getFleets() + " fleets; request was for " +
					numFleets + ".");
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

		// Store the new GameChange
		change = gc;
		// update the Gamestate
		gs.update(change);

		int winningPlayer = checkWin();
		if(winningPlayer > 0) {
			stateOfGame = GAME_OVER;
			winner = winningPlayer;
		}

		System.out.println("Done processing move.");
	} // end processMove()

	/**
	 * Checks to see if a certain player should be eliminated.
	 * This should be called on the defeated planet owner at
	 * the end of attacks
	 * @param player    The candidate for elimination
	 * @return          True if the candidate should be eliminated, false if not
	 */
	public boolean eliminate(int player) {
		Planet[] planets = gs.getPlanets();
		for(int i = 1; i < planets.length; i++) {
			Planet pl = planets[i];
			if(pl.getOwner() == player)
				return false;
		}
		return true;
	}

	public void eliminatePlayer(int player) {
		findPlayer(player).setStatus(0); //eliminate him/her
		gs.setPlayerInactive(player);
	}

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

	private void executeRequests() {}

	/** Executes the requests of all the players. This method is highly preliminary. */
	private void setResponses() {
		// TODO implement error handling and request checking or whatever

		Set<String> keys = players.keySet();
		//If the game hasn't started yet, send everyone a Gamestate
		if(stateOfGame == NOT_STARTED) {
			//distribute planets here
			//System.out.println("Now distributing planets...");
			gs.distributePlanets();
			
			for(Iterator<String> itKey=keys.iterator(); itKey.hasNext(); ) {
				String key = itKey.next();
				Player player = players.get(key);
				if(player.getStatus() != 0) {
					if(player.getID() != 1)
						player.setResponse(player.getID() + "\n" + gs.writeToXML());
					else
						player.setResponse(gs.writeToXML());
				}
			}
			//System.out.println("Done distributing planets.");
			//System.out.println(gs);
		}

		else if(stateOfGame == IN_PROGRESS) {
			// If it has, send a GameChange
			for(Iterator<String> itKey=keys.iterator(); itKey.hasNext(); ) {
				String key = itKey.next();
				Player player = players.get(key);

				// Process the request for this player.
				// This would be where we process the players' requests...
				try {
					if(player.getStatus() != 0)
						player.setResponse(change.writeToXML());
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		}
		else { //the game must be over
			for(Iterator<String> itKey=keys.iterator(); itKey.hasNext(); ) {
				String key = itKey.next();
				Player player = players.get(key);
				if(player.getStatus() != 0)
					player.setResponse("winner:" + winner); }
		}
		// Now everyone's threads are released and they all move on to roundEnd.
		// The next thing to happen should be finalResultsAvailable().
	}

	/** Do whatever needs to be done to get ready for the next round (turn). */
	private void finalResultsAvailable() {
		changePlayerPopulation(gs.getActivePlayers().length); //make sure we aren't waiting on inactive players

		// Final part: setup for the next round.
		if(stateOfGame == IN_PROGRESS) {
			gs.nextTurn();
			change.setTurnStatus(gs.getActivePlayer(), gs.getTurnNumber(), gs.getCycleNumber());
		}

		setResponses();

		if(stateOfGame == NOT_STARTED)
			stateOfGame = IN_PROGRESS; 

		for(int p : gs.getPlayerList())
			System.out.print(p + " ");

		System.out.println("active player: " + gs.getActivePlayer() + "\n");
	}

	/** Adjusts the player population for players being eliminated and whatnot. */
	protected void changePlayerPopulation(int count){
		// I thought we didn't need this, but we do. It just makes two new barriers with appropriate size.
		// The CyclicBarrier constructor defines what method is run when all (count) players have submitted
		// their requests - in this case, executeRequests() and finalResultsAvailable(), respectively.
		roundBegin = new CyclicBarrier(count, new Runnable() { public void run() { executeRequests(); }});
		roundEnd = new CyclicBarrier(count, new Runnable() { public void run() { finalResultsAvailable(); }});
	}
}
