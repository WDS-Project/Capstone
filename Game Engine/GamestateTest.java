import org.junit.*;
// Josh Polkinghorn

/* This is a test class for the Gamestate class. */
public class GamestateTest {
	@Test
	public void testRead01() {
		Gamestate gs = new Gamestate("src/TestGS.xml");
		System.out.println(gs.toString());
	}
	
	@Test
	public void testWrite01() {
		Gamestate gs = new Gamestate("src/TestGS.xml");
		System.out.println(gs.writeToXML());
	}
	// Here's an interesting test: run gs.writeToXML() and save the resulting
	// string as an XML file. Then run another test to see if that XML file
	// can be successfully read into an equivalent Gamestate.
}
