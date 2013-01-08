
import java.io.StringWriter;
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
    
    private String nextTurnID;
    private int[][] changes;
    private int stopPosition;
    
    /**
     * Constructor for GameChange. It receives the information
     * from the GameEngine.
     * @param numPlanets    This is used for allocation of space in the matrix.
     *              The maximum number of planets that can change is the number
     *              of planets.
     * @param turnID        The player ID of the player whose turn is next
     */
    public GameChange(int numPlanets, String turnID) {
        changes = new int[numPlanets][3];
        nextTurnID = turnID;
        stopPosition = 0; //the place in the matrix for the next change to be added
    }
    
    /**
     * Add a change to the matrix.
     * @param p     Planet object that changed     
     */
    public void addChange(Planet p) {
        changes[stopPosition][0] = p.getIDNum();
        changes[stopPosition][1] = p.getOwner();
        changes[stopPosition][2] = p.getFleets();
        stopPosition++;
    }
    
    /**
     * Creates a String representation of the GameChange
     * for testing purposes.
     * @return  The String
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        
        for(int i = 0; i < stopPosition; i++) {
            for(int j = 0; j < 3; j++)
                sb.append(changes[i][j] + " ");
            sb.append("\n");
        }
        
        return sb.toString();
    }
    
    /**
     * Puts the changes into XML form beginning at the parent given.
     * Helper method for getXML()
     * @param parent    The root of the XML document to which to write the changes
     */
    public void makeXML(Node parent) {
       Document doc = parent.getOwnerDocument(); //grab the Document we're working on
       
       //create the GameChange element (which is root)
       //it looks like this: <GameChange> ... </GameChange>
       Element gameChange = doc.createElement("GameChange");
       
       //put the next turn ID in the doc
       Element turn = doc.createElement("NextTurnID");
       turn.setAttribute("nextTurnID", nextTurnID);
       gameChange.appendChild(turn);   
       
       Element planetList = doc.createElement("Planets");
       
       //put each planet changed in the doc
       for(int i = 0; i < stopPosition; i++) {
           Element planet = doc.createElement("Planet");
           planet.setAttribute("idNum", ""+changes[i][0]);
           planet.setAttribute("owner", ""+changes[i][1]);
           planet.setAttribute("numFleets", ""+changes[i][2]);
           planetList.appendChild(planet);
       }
        
       gameChange.appendChild(planetList);
       parent.appendChild(gameChange);
    }
    
    /**
     * Get the XML document created in a String format.
     * @return  XML doc as String
     */
    public String getXML() {
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
            
            //add all the planets with changes using the helper method
            makeXML(root);
                
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
