
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
            gc = new GameChange(5, 2, 5, 5);
            Planet x = new Planet(2, "blue", "name", 2,3,4);
            x.setOwner(1);
            x.setFleets(4);
            gc.addChange(x);
            Planet pluto = new Planet(5, "red", "name", 3,4,5);
            pluto.setOwner(3);
            pluto.setFleets(356);
            gc.addChange(pluto);
    }
    
   @Test
   public void testXML() {
       String gcXML = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" +
                "<GameChange>" + 
                    "<Players activePlayer=\"2\" cycleNumber=\"5\" turnNumber=\"5\"/>" + 
                        "<Planets>" +
                        "<Planet" + 
                            " idNum=\"2\"" + 
                            " numFleets=\"4\"" +
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
}
