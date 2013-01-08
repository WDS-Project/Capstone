
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
	
        /**
         * Constructor for HandleDefineGame. Sets the GameEngine.
         * @param eng   The GameEngine for the handler to work with.
         */
	public HandleDefineGame(GameEngine eng) {
		engine = eng;	
	}

        /**
         * Handles all requests for game definitions, including
         * calling methods in the GameEngine for setup.
         * @param exchange      The HttpExchange object that handles
         *              communication with the client.
         */
        @Override
	public void handle(HttpExchange exchange) {
		String req = exchange.getRequestMethod();
		if(req.equalsIgnoreCase("POST")) {
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
                
                //requst format: <number of AI players>/<difficulty of AI1>/<difficulty of AI 2>/etc"
                InputStream stream = exchange.getRequestBody();
                byte[] inbuf = new byte[1000];
                stream.read(inbuf);
                String definition = new String(inbuf).trim();			
                String[] definitions = definition.split("/");
                
                //setup the engine with the appropriate number of players
                int numPlayers = Integer.parseInt(definitions[0]);
                engine.setup(numPlayers);
                
                //start up the AI processes with the given difficulties
                /* Use this when we get to the AI part
                for(int i = 1; i < numPlayers; i++) {
                        PythonStarter AIstarter = new PythonStarter(i, Integer.parseInt(definitions[i]));
                }*/
                
                //200 indicates successful processing of the request
                exchange.sendResponseHeaders(200,0);
                OutputStream response = exchange.getResponseBody();	
                //TODO get the XML gamestate and send it
                //String res = "0_move";
                //response.write(res.getBytes());
                //response.close();
            } catch (IOException ex) {
                //TODO have the client display bad request
            }
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
	Process pythonProc;

	public PythonStarter(int id, int diff) {
		playerID = id;
		difficulty = diff;
		thread = new Thread(this);
		thread.start();
	}
	
	public void run() {
		try{
		pythonProc = Runtime.getRuntime().exec("cmd /c pythonTalker.py " + playerID + " " + difficulty);
		}
		catch(IOException e) {
			System.out.print("Welp. It didn't work.");	
		}
	}
	
}
