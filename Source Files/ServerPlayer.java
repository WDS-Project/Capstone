
import java.util.concurrent.Semaphore;

/** 
 * This class extends Player to have features related to networking.
 * @author WDS Project
 */
public class ServerPlayer extends Player {
	private Semaphore requestSemaphore = new Semaphore(1);
	private String request = "";  // Current request
	private String response;      // Current response
	
	// Getters & Setters
	public String getRequest() {  return request;  }
	public void setRequest(String req) {  request = req;  }
	public String getResponse() {  return response;  }
	public void setResponse(String resp) {  response = resp;  }
	
	public ServerPlayer(int id) {
		super(id);
	}
	
	/**
	 * Give requests to Engine one at a time.
	 * @param request     The request for the player at the time
	 * @param round       The engine associated with the game
	 * @throws Exception If something goes wrong with the synchronization
	 */
	public void synchronizedRequest(String request, GameEngine round) throws Exception {
		System.out.println("Player " + getID() + " synchronized request");
		requestSemaphore.acquire(); //This Player gets the floor
		setRequest(request); //The request that came in over the network is stored here
		round.synchronizedRequest(); //Tell the engine this Player is waiting in line
		requestSemaphore.release(); //Release control of the floor
	}
}
