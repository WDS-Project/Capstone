
import java.io.StringWriter;
import java.util.ArrayList;
import javax.xml.parsers.*;
import javax.xml.transform.*;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import org.w3c.dom.*;

/**
 *  This class is a description of a GameChange.
 * It is built dynamically by the GameEngine while
 * processing moves, and will be loaded to an XML
 * representation to be sent to all players.
 * 
 * @author Alana Weber
 */
public class GameChange {

	private int activePlayer = -1, turnNumber = - 1, cycleNumber = -1; //these should come from
	//the GameEngine after it determines whose turn it is
	private ArrayList<ArrayList<Integer>> changes; //change matrix
	private int numChanges; //place in the matrix for the next change to be added
	private final int CHANGE_LENGTH = 3;    //the number of integers part of any one change

	/**
	 * Constructor for GameChange. It receives the information
	 * from the GameEngine.
	 * @param turnID        The player ID of the player whose turn is next
	 */
	public GameChange() {
		changes = new ArrayList<ArrayList<Integer>>();
		numChanges = 0;
	}

	/**
	 * Add a change to the matrix.
	 * @param p     Planet object that changed     
	 */
	public void addChange(Planet p) {

		//check to see if there is already a change pertaining to that Planet
		boolean found = false;
		for(ArrayList<Integer> a : changes) {
			if(a.get(0) == p.getIDNum()) {
				a.set(1, p.getOwner());
				a.set(2, p.getFleets());
				found = true;
			}
		}

		//otherwise, add the Planet
		if (!found) {
			changes.add(new ArrayList<Integer>());
			changes.get(numChanges).add(p.getIDNum());
			changes.get(numChanges).add(p.getOwner());
			changes.get(numChanges).add(p.getFleets());
			numChanges++;
		}
	}

	/**
	 * Sets information about whose turn is next.
	 * This information should come from the engine after it determines
	 * whose turn is next.
	 * @param active
	 * @param turn
	 * @param cycle
	 */
	public void setTurnStatus(int active, int turn, int cycle) { 
		activePlayer = active;
		turnNumber = turn;
		cycleNumber = cycle;
	}

	/**
	 * Creates a String representation of the GameChange
	 * for testing purposes.
	 * @return  The String
	 */
	@Override
	public String toString() {
		StringBuilder sb = new StringBuilder();
		sb.append("ActivePlayer: " + activePlayer + "\n" +
				"TurnNumber: " + turnNumber + "\n" +
				"CycleNumber: " + cycleNumber + "\n" + "Changes:\n");

		for(int i = 0; i < numChanges; i++) {
			for(int j = 0; j < CHANGE_LENGTH; j++)
				sb.append(changes.get(i).get(j) + " ");
			sb.append("\n");
		}

		return sb.toString();
	}

	/**
	 * Getter for changes[][] matrix
	 * @return  The current state of the changes[][] matrix
	 */
	public int[][] getChanges() { 
		//ArrayList.toArray returns Object[], so we have to do this nonsense
		//to avoid casting from Object
		int[][] currentChanges = new int[changes.size()][CHANGE_LENGTH];
		for(int i = 0; i < currentChanges.length; i++) {
			for(int j = 0; j < CHANGE_LENGTH; j++)
				currentChanges[i][j] = (int)changes.get(i).get(j);
		}
		return currentChanges;
	}

	/**
	 * Writes this GameChange to a String XML format.
	 * @return   The XML as a String
	 * @throws TransformerException, ParserConfigurationException
	 *       If bad stuff happened while performing the magic that makes
	 *       the XML into a String, the Exceptions are thrown upward
	 */
	public String writeToXML() throws TransformerException, ParserConfigurationException {

		StringWriter sw = new StringWriter();
		//start building the document
		DocumentBuilderFactory domFactory = DocumentBuilderFactory.newInstance();
		domFactory.setNamespaceAware(true);
		DocumentBuilder builder = domFactory.newDocumentBuilder();
		Document doc = builder.newDocument();

		//create the root of the Document as a starting place
		Element root = doc.createElement("root");
		doc.appendChild(root);

		//create the GameChange element (which is root)
		//it looks like this: <GameChange> ... </GameChange>
		Element gameChange = doc.createElement("GameChange");

		//put the next turn ID in the doc
		Element turn = doc.createElement("Players");
		turn.setAttribute("activePlayer", ""+activePlayer);
		turn.setAttribute("turnNumber", ""+turnNumber);
		turn.setAttribute("cycleNumber", ""+cycleNumber);
		gameChange.appendChild(turn);   

		Element planetList = doc.createElement("Planets");

		//put each planet changed in the doc
		for(int i = 0; i < numChanges; i++) {
			Element planet = doc.createElement("Planet");
			planet.setAttribute("idNum", ""+changes.get(i).get(0));
			planet.setAttribute("owner", ""+changes.get(i).get(1));
			planet.setAttribute("numFleets", ""+changes.get(i).get(2));
			planetList.appendChild(planet);
		}

		gameChange.appendChild(planetList);
		root.appendChild(gameChange);

		//magically transforms the XML document into a readable String format
		DOMSource domSource = new DOMSource(root.getFirstChild());
		TransformerFactory tf = TransformerFactory.newInstance();
		Transformer magic = tf.newTransformer();
		magic.transform(domSource, new StreamResult(sw));

		return sw.toString();
	}
}
