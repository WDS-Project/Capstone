/**
 *  This class houses the main server for the Risk game.
 * It handles all HTTP requests and responses among the client, 
 * the GameEngine, and the AI players.
 * 
 * @author Alana Weber
 */
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.*;
import java.util.concurrent.Executors;

public class Server {

	private int port;
	private Scanner keyboard;
	private HttpServer server;

	private TreeMap<String, GameEngine> playersInSessions; 
	//this map is a String containing <PlayerIP:PlayerID> mapped to a GameEngine

	private ArrayList<GameEngine> gameSessions; //And this is a list of current sessions
	private int nextAvailableID = 1;
	private String xmlPath; //so for right now the server is always going to
	//look at the same file to get the Gamestate

	/**
	 * Constructor for Server. Sets the port.
	 * @param newPort   Port for the server to listen on.
	 */
	private Server(int newPort, String xml) {
		port = newPort;
		keyboard = new Scanner(System.in);
		playersInSessions = new TreeMap<String, GameEngine>();
		gameSessions = new ArrayList<GameEngine>();
		xmlPath = xml;
	}

	/**
	 * Creates HTTPServer and contexts, and starts the Server.
	 */
	public void run() {

		try{
			//create new HttpServer with the specified port number
			//and a maximum backlog of 20
			server = HttpServer.create(new InetSocketAddress(port), 20);

			//context for defining a game
			server.createContext("/definegame/", new HandleDefineGame(this, xmlPath));
			//context for passing out game changes
			server.createContext("/gamechange/", new HandleGameChange(this));
			//context for moves
			server.createContext("/move/", new HandleMove(this));
			//context for joining a Game
			server.createContext("/join/", new HandleJoin(this));

			//assign Executor to take care of the tasks using a 
			//cached thread pool
			server.setExecutor(Executors.newCachedThreadPool());

			server.start();
			System.out.println("Server is listening on port " + port + "\n" +
			"Type \"quit\" to close.");
			String closer = keyboard.nextLine();
			if(closer.equalsIgnoreCase("quit"))
				close();

		} catch (IOException e) {
			System.out.println("There was a problem starting the server.");
			System.exit(1);
		} catch (NoSuchElementException e) {
			System.out.println("There was a problem starting the server.");
			System.exit(1);
		}
	}

	/**
	 * Stops all server processes and exits the program.
	 */
	public void close() {
		System.out.println("Goodbye.");
		server.stop(5);	
		System.exit(0);
	}
	
	public String getServerIP() {
		return server.getAddress().getAddress().toString();
	}
	
	public int getServerPort() {
		return port;	
	}

	/**
	 * This gives out IDs in a very simplistic manner. It will only
	 * become a problem if we have so many games that the next available
	 * ID exceeds the digit limit of an int.
	 * @return An ID for a GameEngine
	 */
	public int getNextAvailableID() { return nextAvailableID++;   }

	/**
	 * Finds the session (GameEngine) according to ID.
	 * @param sessionID
	 * @return  The GameEngine (session) corresponding to the given ID
	 *          Null if not found
	 */
	public GameEngine findSession(int sessionID) {
		for(GameEngine ge : gameSessions) {
			if(ge.getID() == sessionID)
				return ge;
		}
		return null;
	}

	/**
	 * Finds the session associated with that players IP.
	 * @param IP
	 * @return  The session (GameEngine) that the player is associated with
	 */
	public GameEngine findSession(String IP) {
		return playersInSessions.get(IP);
	}

	/**
	 * Add a Player to a session
	 * @param IP    IP address of Player
	 * @param ge    GameEngine (session)
	 */
	public void addPlayerToSession(String IP, GameEngine ge) {
		playersInSessions.put(IP, ge);
		System.out.println("Adding player " + IP + " to session " + ge.getID());
	}
        
        /**
         * Remove a player from a session upon elimination so they
         * can send in no more requests.
         * @param IP 
         */
        public void removePlayerFromSession(String IP) {
            playersInSessions.remove(IP);
        }

	/**
	 * Add a session (GameEngine) to the list.
	 * @param ge d
	 */
	public void addSession(GameEngine ge) {
		gameSessions.add(ge);
		System.out.println("New Session: " + ge.getID());
	}

	/**
	 * Main method for Server.
	 * @param args      The port number may be passed as an optional argument.
	 * @throws IOException 
	 */
	public static void main(String[] args) {

		Server server;
		int portNumber = 12345;

		if(args.length > 1) {
			System.out.println("Usage: java Server [port number]\n"+
			"Default port is 12345.");
			System.exit(1);
		}
		if(args.length == 1) {
			try { 
				portNumber = Integer.parseInt(args[0]);
			} catch (NumberFormatException ex) {
				System.out.println("Port number must be an integer.\n" + 
						"Usage: java Server [port number]\n"+
				"Default port is 12345.");
				System.exit(1);
			}
		}

		//server = new Server(portNumber, ""); //ADD XML PATH
		server = new Server(portNumber, "TestGS6.xml"); // Temporary thing for until we get this going
		server.run();
	}

}