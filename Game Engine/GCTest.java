
import java.util.ArrayList;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.TransformerException;
import org.junit.*;
import static org.junit.Assert.*;

/**
 *
 * @author Alana Weber
 */
public class GCTest {
    
    GameChange gc;
    
    @Before
    public void setUp() {
            gc = new GameChange(2, 5, 5);
            Planet x = new Planet(2, "blue", "name", 2,3,4);
            x.setOwner(1);
            x.setFleets(4);
            gc.addChange(x);
            
            Planet pluto = new Planet(5, "red", "name", 3,4,5);
            pluto.setOwner(3);
            pluto.setFleets(356);
            gc.addChange(pluto);
            
            x.setFleets(6);
            gc.addChange(x);
    }
    
   @Test
   public void testXML() throws TransformerException, ParserConfigurationException {
       String gcXML = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
                "<GameChange>" + 
                    "<Players activePlayer=\"2\" cycleNumber=\"5\" turnNumber=\"5\"/>" + 
                        "<Planets>" +
                        "<Planet" + 
                            " idNum=\"2\"" + 
                            " numFleets=\"6\"" +
                            " owner=\"1\"" +  
                        "/>" +
                        "<Planet" +
                            " idNum=\"5\""+
                            " numFleets=\"356\"" +
                            " owner=\"3\"" +
                        "/>"+
                        "</Planets>"+
                "</GameChange>";
       assertEquals(gcXML, gc.writeToXML());
   }
   
   @Test
   public void testGetChanges() {
       String gamec = "";
       int[][] changes = gc.getChanges();
       for(int i = 0; i < changes.length; i++) {
           for(int j = 0; j < 3; j++) {
               gamec += changes[i][j] + " ";
           }
           gamec += "\n";
       }
       String compare = "2 1 6 \n5 3 356 \n";
       assertEquals(gamec, compare);
   }
   
   @Test
   public void testNoChanges() {
       GameChange gChange = new GameChange(0,0,0);
       assertEquals(gChange.getChanges(), new int[0][0]);
   }
}
