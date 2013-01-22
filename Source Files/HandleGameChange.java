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

			//get the IP
			String playerIP = exchange.getRemoteAddress().getAddress().getHostAddress();  
			System.out.println("GameChange request from " + playerIP);

			String req = exchange.getRequestMethod();
			//it should actually be a GET
			if(req.equalsIgnoreCase("OPTIONS")) {
				Headers header = exchange.getResponseHeaders();
				header.add("Access-Control-Allow-Origin", "*");
				header.add("Access-Control-Allow-Methods", "POST");
				header.add("Access-Control-Allow-Methods", "GET");
				header.add("Access-Control-Allow-Methods", "OPTIONS");
				header.add("Access-Control-Allow-Headers", "Content-Type");
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
				String request = new String(inbuf).trim();

				if(request.charAt(request.length() -1) == '/') //chop off slash to avoid NumberFormatException
					request = request.substring(0, request.length()-1);

				//get the session
				GameEngine engine = server.findSession(playerIP + ":" + request);
                                
                                //if the engine is not found, discard the request
				if(engine == null) {
					System.out.println("Attempt to get a GameChange by bad player ID.");
                                        return;
                                }

				Player player = engine.findPlayer(playerIP+":"+request);
				if(engine.eliminate(player.getID())) { //if this player should be eliminated
                                    engine.eliminatePlayer(player.getID()); //get rid of them in the engine
                                    server.removePlayerFromSession(playerIP+":"+player.getID()); //remove them from the game session
                                    player.setResponse("eliminated"); //tell the player
                                }
                                else {
                                    player.synchronizedRequest("gamechange", engine);
                                }
                                 exchange.sendResponseHeaders(200,0);
                                 OutputStream responseBody = exchange.getResponseBody();
                                 System.out.println("Sending response to player " + player.getID());
                                 System.out.println(player.getResponse());
                                 responseBody.write(player.getResponse().getBytes());
                                 responseBody.close();
			}
		} catch (Exception e) {
			// Any exception thrown by this handler will be displayed to the server console.
			e.printStackTrace();
		}
	}
}
