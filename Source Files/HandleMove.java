
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
			String reqType = exchange.getRequestMethod();
			if(reqType.equalsIgnoreCase("OPTIONS")) {
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
			else if(reqType.equalsIgnoreCase("POST")) {
				String playerIP = exchange.getRemoteAddress().getAddress().getHostAddress();
				System.out.println("Move request from " + playerIP);
				
				//all this header nonsense that I really don't know why we have to do
				Headers header = exchange.getResponseHeaders();
				header.add("Access-Control-Allow-Origin", "*");
				header.add("Access-Control-Allow-Methods", "POST");
				header.add("Access-Control-Allow-Methods", "GET");
				header.add("Access-Control-Allow-Methods", "OPTIONS");
				header.add("Access-Control-Allow-Headers", "Content-Type");

				//now deal with the actual request
				InputStream stream = exchange.getRequestBody();
				byte[] inbuf = new byte[1000];
				stream.read(inbuf);
				String move = new String(inbuf).trim();

				//get the Move
				Move m = new Move(move, playerIP);

				//get the session
				GameEngine engine = server.findSession(playerIP+":" + m.getPlayerID());

				//if the engine is not found, discard the request
				if(engine == null) {
					System.out.println("Engine not found; possible attempt to move by bad player ID.");
					return;
				}               

				//get the Player
				ServerPlayer player = engine.findPlayer(playerIP+":"+m.getPlayerID());                        

				engine.processMove(m); // This should handle all input validation
				player.synchronizedRequest("gamechange", engine);
				
				// Check if the player has won.
				if (engine.checkWin() == player.getID()) {
					System.out.println("Player "+player.getID()+" has won!");
					player.setResponse("winner:"+player.getID());
				}
				
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
