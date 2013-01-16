
/**
 * This class handles a user's request to join a game started by another user.
 * @author Alana Weber
 */
import java.io.*;
import java.util.*;
import com.sun.net.httpserver.*;

public class HandleJoin implements HttpHandler {

	Server server;
	
        /**
         * Constructor for HandleJoin. Sets the Server associated with this handler.
         * @param svr 
         */
	public HandleJoin(Server svr) {
		server = svr;	
	}

        //request format: /join/<sessionID>
        
        
	public void handle(HttpExchange exchange)throws IOException {
                String nextPlayerIP = exchange.getRemoteAddress().getAddress().getHostAddress();
                System.out.println("Join game request from " + nextPlayerIP);
		String req = exchange.getRequestMethod();
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
			int len = stream.read(inbuf);
			byte[] inbufShort = Arrays.copyOfRange(inbuf, 0, len);
			String request = new String(inbufShort);
                        
                        if(request.charAt(request.length() -1) == '/') //chop off slash to avoid NumberFormatException
                            request = request.substring(0, request.length()-1);
                        
                        int sessionID = Integer.parseInt(request); //this better be an int
                        
                        GameEngine engine = server.findSession(sessionID);
                        
                        if(engine == null) {
                            System.out.println("There is no session " + sessionID);
                            throw new RuntimeException("Bad session ID.");
                        }
                        
                        Player nextPlayer = engine.definePlayer(nextPlayerIP+":"+engine.getNextPlayerID(), 1); //active status
                        server.addPlayerToSession(nextPlayerIP + ":" + nextPlayer.getID(), engine);
                        
                        try {
                            nextPlayer.synchronizedRequest("gameState", engine);
                        } catch (Exception ex) {
                            System.out.println("We couldn't add you to the game.");
                        }
			
                        //send Gamestate to the player when this turn rolls around
			exchange.sendResponseHeaders(200,0);
			OutputStream responseBody = exchange.getResponseBody();
			responseBody.write(nextPlayer.getResponse().getBytes());
			responseBody.close();
			}
		}
	}
