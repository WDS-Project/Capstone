
/**
 *  This class handles the user's request to begin a new game.
 * 
 * @author Alana Weber
 */
import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

public class HandleDefineGame implements HttpHandler {

	GameEngine engine;
	Server server;
	String xmlGsPath;

	/**
	 * Constructor for HandleDefineGame. Sets the GameEngine and XML path.
	 * @param eng   The GameEngine for the handler to work with.
	 * @param xmlPath   Path of the XML Gamestate
	 */
	public HandleDefineGame(Server svr, String xmlPath) {
		server = svr;
		xmlGsPath = xmlPath;
	}

	/**
	 * Handles all requests for game definitions, including
	 * calling methods in the GameEngine for setup.
	 * @param exchange      The HttpExchange object that handles
	 *              communication with the client.
	 */
	@Override
	public void handle(HttpExchange exchange) {
		try {
			String req = exchange.getRequestMethod();

			/*
			 * I'm pretty sure this gets the IP in a String format.
			 * getRemoteAddress() returns an InetSocketAddress, and getAddress()
			 * returns an InetAddress from that.  From that you can get
			 * the IP in a String format using getHostAddress().
			 */
			String player1IP = exchange.getRemoteAddress().getAddress().getHostAddress();
			System.out.println("Define game request from " + player1IP);

			if(req.equalsIgnoreCase("OPTIONS")) {
				Headers header = exchange.getResponseHeaders();
				header.add("Access-Control-Allow-Origin", "*");
				header.add("Access-Control-Allow-Methods", "POST");
				header.add("Access-Control-Allow-Methods", "GET");
				header.add("Access-Control-Allow-Methods", "OPTIONS");
				header.add("Access-Control-Allow-Headers", "Content-Type");
			}
			else if(req.equalsIgnoreCase("POST")) {
				try {
					//for browser portability, if the request method is POST,
					//the headers must be adjusted to allow all types of requests
					//before continuing
					Headers header = exchange.getResponseHeaders();
					header.add("Access-Control-Allow-Origin", "*");
					header.add("Access-Control-Allow-Methods", "POST");
					header.add("Access-Control-Allow-Methods", "GET");
					header.add("Access-Control-Allow-Methods", "OPTIONS");
					header.add("Access-Control-Allow-Headers", "Content-Type");

					//request format: <number of human players>/<number of AI players>/
					//<difficulty of AI1>/<difficulty of AI 2>/etc"
					InputStream stream = exchange.getRequestBody();
					byte[] inbuf = new byte[1000]; //so the max is 1000 characters
					stream.read(inbuf);
					String definition = new String(inbuf).trim();			
					String[] definitions = definition.split("/");

					int humans = Integer.parseInt(definitions[0]);
					int AIs = Integer.parseInt(definitions[1]);
					int[] diffs = new int[definitions.length -2];
					for(int i = 2; i < definitions.length; i++) 
						diffs[i-2] = Integer.parseInt(definitions[i]);

					//setup the Engine starting with this Player (1)
					engine = new GameEngine(server.getNextAvailableID());
					server.addSession(engine);
					engine.loadGamestate(xmlGsPath);
					engine.changePlayerPopulation(humans+AIs); //this should make Engine wait for all players

					Player playerOne = engine.definePlayer(player1IP+":"+engine.getNextPlayerID(), 1); //active status
					server.addPlayerToSession(player1IP + ":" + playerOne.getID(), engine);

					try {
						playerOne.synchronizedRequest("gamestate", engine);
					} catch (Exception ex) {
						System.out.println("Could not start the game.");
					}

					//Then the engine waits for the others to join before sending out Gamestate

					//start up the AI processes with the given difficulties
					for(int i = 0; i <  AIs; i++) {
						PythonStarter AIstarter = new PythonStarter(i, diffs[0], engine.getID());
					}

					//200 indicates successful processing of the request
					//GameState sent to Player 1
					exchange.sendResponseHeaders(200,0);
					OutputStream response = exchange.getResponseBody();	
					response.write(playerOne.getResponse().getBytes());
					response.close();

				} catch (IOException ex) {
					//TODO have the client display bad request
				}
			}
		} catch (Exception e) {
			// Any exception thrown by this handler will be displayed to the server console.
			e.printStackTrace();
		}
	}

}

/**
 * This class will be further implemented when we get to the AI part.
 * Right now it has leftovers from the prototype in it.
 * @author Alana Weber
 */
class PythonStarter implements Runnable {

	Thread thread;
	int playerID = -1;
	int difficulty = -1;
	int sessionID = -1;
	Process pythonProc;

	public PythonStarter(int id, int diff, int gameID) {
		playerID = id;
		difficulty = diff;
		sessionID = gameID;
		thread = new Thread(this);
		thread.start();
	}

	public void run() {
		try{
			pythonProc = Runtime.getRuntime().exec("cmd /c AIClient.py " + playerID + " " + difficulty + " " + sessionID);
		}
		catch(IOException e) {
			e.printStaceTrace();	
		}
	}

}
