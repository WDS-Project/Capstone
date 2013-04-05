
/**
 *
 * @author Alana
 */
import java.io.*;

import com.sun.net.httpserver.*;

public class HandleMove implements HttpHandler {

	Server server;

	public HandleMove(Server svr) {
		server = svr;	
	}

	//See Move for the request format
	// /move/<Move>

	public void handle(HttpExchange exchange) {
		try {
			//get the IP
			String playerIP = exchange.getRemoteAddress().getAddress().getHostAddress();

			System.out.println("Move request from " + playerIP);

			String req = exchange.getRequestMethod();
			if(req.equalsIgnoreCase("OPTIONS")) {
				Headers header = exchange.getResponseHeaders();
				header.add("Access-Control-Allow-Origin", "*");
				header.add("Access-Control-Allow-Methods", "POST");
				header.add("Access-Control-Allow-Methods", "GET");
				header.add("Access-Control-Allow-Methods", "OPTIONS");
				header.add("Access-Control-Allow-Headers", "Content-Type");
				
				//send an ok
				exchange.sendResponseHeaders(200,0);
				OutputStream response = exchange.getResponseBody();	
				response.write("ok".getBytes());
				response.close();
			}
			else if(req.equalsIgnoreCase("POST")) {
				//all this header nonsense that I really don't know why we have to do
				Headers header = exchange.getResponseHeaders();
				header.add("Access-Control-Allow-Origin", "*");
				header.add("Access-Control-Allow-Methods", "POST");
				header.add("Access-Control-Allow-Methods", "GET");
				header.add("Access-Control-Allow-Methods", "OPTIONS");
				header.add("Access-Control-Allow-Headers", "Content-Type");

				//now deal with the actual request
				InputStream stream = exchange.getRequestBody();
				byte[] inbuf = new byte[100];
				stream.read(inbuf);
				String move = new String(inbuf).trim();

				//get the Move
				Move m = new Move(move, playerIP);

				//get the session
				GameEngine engine = server.findSession(playerIP+":" + m.getPlayerID());

				//if the engine is not found, discard the request
				if(engine == null) {
					System.out.println("Attempt to move by bad player ID.");
					return;
				}               

				//get the Player
				Player player = engine.findPlayer(playerIP+":"+m.getPlayerID());                        

				engine.processMove(m);
				if(engine.eliminate(player.getID())) { //if this player should be eliminated
					engine.eliminatePlayer(player.getID()); //get rid of them in the engine
					server.removePlayerFromSession(playerIP+":"+player.getID()); //remove them from the game session
					player.setResponse("eliminated"); //tell the player
				}
				player.synchronizedRequest("gamechange", engine);
				exchange.sendResponseHeaders(200,0);
				OutputStream responseBody = exchange.getResponseBody();
				responseBody.write(player.getResponse().getBytes());
				responseBody.close();
			}
		} catch (Exception e) {
			// Any exception thrown by this handler will be displayed to the server console.
			e.printStackTrace();
		}
	}
}
