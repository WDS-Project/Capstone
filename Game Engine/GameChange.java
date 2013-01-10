
import java.io.StringWriter;
import java.util.ArrayList;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;

/**
 *  This class is a description of a GameChange.
 * It is built dynamically by the GameEngine while
 * processing moves, and will be loaded to an XML
 * representation to be sent to all players.
 * 
 * @author Alana Weber
 */
public class GameChange {
    
    private int activePlayer, turnNumber, cycleNumber; //these should come from
    //the GameEngine after it determines whose turn it is
    private ArrayList<ArrayList<Integer>> changes;
    private int numChanges; //place in the matrix for the next change to be added
    private final int CHANGE_LENGTH = 3;
    
    /**
     * Constructor for GameChange. It receives the information
     * from the GameEngine.
     * @param turnID        The player ID of the player whose turn is next
     */
    public GameChange(int active, int turn, int cycle) {
        changes = new ArrayList<ArrayList<Integer>>();
        activePlayer = active;
        turnNumber = turn;
        cycleNumber = cycle;
        numChanges = 0;
    }
    
    /**
     * Add a change to the matrix.
     * @param p     Planet object that changed     
     */
    public void addChange(Planet p) {
        changes.add(new ArrayList<Integer>());
        changes.get(numChanges).add(p.getIDNum());
        changes.get(numChanges).add(p.getOwner());
        changes.get(numChanges).add(p.getFleets());
        numChanges++;
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
    */
    public String writeToXML() {
        
       StringWriter sw = new StringWriter();
        try {
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
        } catch (TransformerException ex) {
            System.out.println("Bad stuff happened.");
        } catch (ParserConfigurationException ex) {
            System.out.println("REALLY bad stuff happened.");
        }
        return sw.toString();
        }
}
