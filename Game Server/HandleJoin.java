
/**
 *
 * @author Alana
 */
import java.io.*;
import java.util.*;
import java.util.concurrent.*;

import com.sun.net.httpserver.*;
import java.util.logging.Level;
import java.util.logging.Logger;

public class HandleJoin implements HttpHandler {

	Server server;
	
	public HandleJoin(Server svr) {
		server = svr;	
	}

        //request format: /join/<sessionID>
        
        
	public void handle(HttpExchange exchange)throws IOException {
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
			stream.read(inbuf);
			String request = new String(inbuf);
                        
                        int sessionID = Integer.parseInt(request); //this better be an int
                        
                        GameEngine engine = server.findSession(sessionID);
                        
                        if(engine == null)
                            throw new RuntimeException("Bad session ID.");
                        
                        String nextPlayerIP = exchange.getRemoteAddress().getAddress().getHostAddress();
                        Player nextPlayer = engine.definePlayer(nextPlayerIP, 1); //active status
                        server.addPlayerToSession(nextPlayerIP, engine);
                        try {
                            nextPlayer.synchronizedRequest("gameState", engine);
                        } catch (Exception ex) {
                            System.out.println("We couldn't add you to the game.");
                        }
				
			exchange.sendResponseHeaders(200,0);
			OutputStream responseBody = exchange.getResponseBody();
			responseBody.write(nextPlayer.getResponse().getBytes());
			responseBody.close();
			}
		}
	}

