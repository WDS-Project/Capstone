/**
 *  This class houses the main server for the Risk game.
 * It handles all HTTP requests and responses among the client, 
 * the GameEngine, and the AI players.
 * 
 * @author Alana Weber
 */
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.NoSuchElementException;
import java.util.Scanner;
import java.util.concurrent.Executors;

public class Server {

    	private int port;
	private Scanner keyboard;
	private HttpServer server;
	GameEngine engine = new GameEngine();

        /**
         * Constructor for Server. Sets the port.
         * @param newPort   Port for the server to listen on.
         */
        private Server(int newPort) {
            port = newPort;
            keyboard = new Scanner(System.in);
        }
	
        /**
         * Creates HTTPServer and contexts, and starts the Server.
         */
	public void run() {
		
		try{
                        //create new HttpServer with the specified port number
                        //and a maximum backlog of 20
			server = HttpServer.create(new InetSocketAddress(port), 20);
                        
                        //context for defining a game
			server.createContext("/definegame/", new HandleDefineGame(engine));
                        //context for passing out game changes
			server.createContext("/gamechange/", new HandleGameChange(engine));
                        //context for moves
                        server.createContext("/move/", new HandleMove(engine));
			
                        //assign Executor to take care of the tasks using a 
                        //cached thread pool
			server.setExecutor(Executors.newCachedThreadPool());
			
                        server.start();
			System.out.println("Server is listening on port " + port + "\n" +
                                "Type \"quit\" to close.");
			String closer = keyboard.nextLine();
			if(closer.equalsIgnoreCase("quit"))
				close();
                        
		} catch (IOException e) {
			System.out.println("There was a problem starting the server.");
			System.exit(1);
		} catch (NoSuchElementException e) {
			System.out.println("There was a problem starting the server.");
			System.exit(1);
		}
	}
	
        /**
         * Stops all server processes and exits the program.
         */
	public void close() {
                System.out.println("Goodbye.");
		server.stop(5);	
                System.exit(0);
	}
	
	/**
         * Main method for Server.
         * @param args      The port number may be passed as an optional argument.
         * @throws IOException 
         */
        public static void main(String[] args) {
            
                Server server;
                int portNumber = 12345;
            
                if(args.length > 1) {
                    System.out.println("Usage: java Server [port number]\n"+
                               "Default port is 12345.");
                    System.exit(1);
                }
                if(args.length == 1) {
                    try { 
                        portNumber = Integer.parseInt(args[0]);
                    } catch (NumberFormatException ex) {
                        System.out.println("Port number must be an integer.\n" + 
                                "Usage: java Server [port number]\n"+
                               "Default port is 12345.");
                        System.exit(1);
                    }
                }
                    
                server = new Server(portNumber);
		server.run();
	}

}