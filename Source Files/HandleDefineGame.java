
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
	
	/**
	* Constructor for HandleDefineGame. Sets the GameEngine and XML path.
	* @param eng   The GameEngine for the handler to work with.
	* @param xmlPath   Path of the XML Gamestate
	*/
	public HandleDefineGame(Server svr) {
		server = svr;
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
			String reqType = exchange.getRequestMethod();
			
			if (reqType.equalsIgnoreCase("OPTIONS")) { 
				Headers header = exchange.getResponseHeaders();
				header.add("Access-Control-Allow-Origin", "*");
				header.add("Access-Control-Allow-Methods", "POST");
				header.add("Access-Control-Allow-Methods", "GET");
				header.add("Access-Control-Allow-Methods", "OPTIONS");
				header.add("Access-Control-Allow-Headers", "Content-Type");
				
				//send an ok
				exchange.sendResponseHeaders(300,0);
				OutputStream response = exchange.getResponseBody();	
				response.write("ok".getBytes());
				response.close();
			}
			else if (reqType.equalsIgnoreCase("POST")) {
				String player1IP = exchange.getRemoteAddress().getAddress().getHostAddress();
				System.out.println("Define game request from " + player1IP);
				
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
					
					//request format: <name of Gamestate file>/<number of human players>/<number of AI players>/
					//<difficulty of AI1>/<difficulty of AI 2>/<etc>/"
					InputStream stream = exchange.getRequestBody();
					byte[] inbuf = new byte[1000]; //so the max is 1000 characters
					stream.read(inbuf);
					String definition = new String(inbuf).trim();
					String[] params = definition.split("/");
					
					//number of players
					int humans = Integer.parseInt(params[1]);
					int AIs = Integer.parseInt(params[2]);
					int totalPlayers = humans + AIs;
					
					//difficulties of AIs
					int[] diffs = new int[params.length -3];
					for(int i = 3; i < params.length; i++) 
						diffs[i-3] = Integer.parseInt(params[i]);
					
					//gamestate file name
					String gsFile = params[0] + ".xml";
					
					//setup the Engine starting with this Player (1)
					engine = new GameEngine(server.getNextAvailableID());
					server.addSession(engine);
					
					try {
						engine.loadGamestate(gsFile, totalPlayers);
					} catch (Exception ex) {
						System.out.println("Error loading gamestate.");
						exchange.sendResponseHeaders(400,0);
						OutputStream response = exchange.getResponseBody();	
						response.write("Error".getBytes());
						response.close();
						return;
					}
					
					engine.changePlayerPopulation(humans+AIs); //this should make Engine wait for all players
					
					ServerPlayer playerOne = engine.definePlayer(player1IP+":1", 1); //active status
					server.addPlayerToSession(player1IP + ":" + playerOne.getID(), engine);
					
					//start up the AI processes with the given difficulties
					for(int i = 0; i < AIs; i++) {
						new PythonStarter(diffs[i], engine.getID(),
							server.getServerIP(), server.getServerPort());
					}
					System.out.println("Done defining game. Now we're about to do a synchronized request...");

					playerOne.synchronizedRequest("gamestate", engine);
					//Then the engine waits for the others to join before sending out Gamestate
					
					//200 indicates successful processing of the request
					// Answer player 1's request with a Gamestate
					exchange.sendResponseHeaders(200, 0);
					OutputStream response = exchange.getResponseBody();	
					response.write(playerOne.getResponse().getBytes());
					response.close();
					System.out.println("Define game success!");
				} catch (IOException ex) {
					ex.printStackTrace();
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
	int difficulty, sessionID, serverPort;
	String serverIP = "";
	Thread thread;
	Process pythonProc;
	
	public PythonStarter(int diff, int gameID, String IP, int port) {
		difficulty = diff;
		sessionID = gameID;
		serverIP = IP;
		serverPort = port;
		thread = new Thread(this);
		thread.start();
	}
	
	public void run() {
		try{
			System.out.println("Starting an AI! Difficulty: "+difficulty);
			pythonProc = Runtime.getRuntime().exec("cmd /c python AIClient.py "
				+ difficulty + " " + sessionID + " " +
				serverIP + ":" + serverPort);
			//System.out.println("Now we are waiting to hear from it.");
		}
		catch(IOException e) {
			e.printStackTrace();	
		}
	}
	
}
