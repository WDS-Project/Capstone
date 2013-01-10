
import java.util.concurrent.Semaphore;

/**
 * This class is a representation of a Player to the Engine,
 * either human or AI.
 * @author Alana Weber
 */

public class Player {
  
  private int ID;
  private Semaphore requestSemaphore = new Semaphore(1);
  
  private String request = "";  // Current request
  private String response;      // Current response
  
  /**
   * Constructor for Player
   * @param id  ID for Player
   */
  public Player(int id) {
    ID = id;
  }
  
  /**
   * Getters and setters 
   */
  public int getID() { return ID; }
  public String getRequest() {  return request;  }
  public void setRequest(String req) {  request = req;  }
  public String getResponse() {  return response;  }
  public void setResponse(String resp) {  response = resp;  }
  
  /**
   * Give requests to Engine one at a time.
   * @param request     The request for the player at the time
   * @param round       The engine associated with the game
   * @throws Exception  If something goes wonky
   */
  public void synchronizedRequest(String request, GameEngine round) throws Exception {
        requestSemaphore.acquire(); //This Player gets the floor
        setRequest(request); //The request that came in over the network is stored here
        round.synchronizedRequest(); //Tell the engine this Player is waiting in line
        requestSemaphore.release(); //Release control of the floor
  }
}

