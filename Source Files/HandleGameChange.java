/**
 *
 * @author Alana
 */
import java.io.*;

import com.sun.net.httpserver.*;

public class HandleGameChange implements HttpHandler {

	Server server;

	public HandleGameChange(Server svr) {
		server = svr;	
	}

	//request format: /gameChange/<playerID>

	public void handle(HttpExchange exchange) {
		try {
			String reqType = exchange.getRequestMethod();
			//it should actually be a GET
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
				System.out.println("GameChange request from " + playerIP);
				
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
				String request = new String(inbuf).trim();

				if(request.charAt(request.length() -1) == '/') //chop off slash to avoid NumberFormatException
					request = request.substring(0, request.length()-1);

				//get the session
				GameEngine engine = server.findSession(playerIP + ":" + request);
                                
                                //if the engine is not found, discard the request
				if(engine == null) {
					System.out.println("Attempt to get a GameChange by bad player ID: " + playerIP + ":" + request);
                                        return;
                                }
                                
                                // Synchronize with the other players
				Player player = engine.findPlayer(playerIP+":"+request);
				player.synchronizedRequest("gamechange", engine);
				
				// Check if the player was eliminated.
				if(player.getStatus() == 0) {
					server.removePlayerFromSession(playerIP+":"+player.getID()); //remove them from the game session
					player.setResponse("eliminated"); //tell the player
					System.out.println("Player "+player.getID()+" has been eliminated.");
				}
				
				// Send the response
				exchange.sendResponseHeaders(200,0);
				OutputStream responseBody = exchange.getResponseBody();
				responseBody.write(player.getResponse().getBytes());
				responseBody.close();
			}
		} catch (Exception e) {
			// Any exception thrown by this handler will be displayed to the server console.
                        System.out.println(e.getMessage());
			e.printStackTrace();
		}
	}
}
