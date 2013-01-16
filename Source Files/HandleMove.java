
/**
 *
 * @author Alana
 */
import java.io.*;
import java.util.*;
import java.util.concurrent.*;

import com.sun.net.httpserver.*;

public class HandleMove implements HttpHandler {

	Server server;
	
	public HandleMove(Server svr) {
		server = svr;	
	}

        //See Move for the request format
        // /move/<Move>
        
	public void handle(HttpExchange exchange)throws IOException {
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
                
                        if(engine == null) {
                             System.out.println("There is no session associated with this player.");
                             throw new RuntimeException("Bad player IP");
                        }               

                         //get the Player
                        Player player = engine.findPlayer(playerIP);                        
                        
                        engine.processMove(m);
                        
                        try {
                            player.synchronizedRequest("gamechange", engine);
                        } catch (Exception ex) {
                            System.out.println("Trouble sending request to engine.");
                        }
				
			exchange.sendResponseHeaders(200,0);
			OutputStream responseBody = exchange.getResponseBody();
			responseBody.write(player.getResponse().getBytes());
			responseBody.close();
			}
		}
	}
