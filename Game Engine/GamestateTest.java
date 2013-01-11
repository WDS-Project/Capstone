import static org.junit.Assert.*;

import java.util.Arrays;

import org.junit.*;
// Josh Polkinghorn

/* This is a test class for the Gamestate class. */
public class GamestateTest {
	Gamestate gs;
	
	@Before
	public void setup() {
		gs = new Gamestate("src/TestGS.xml");
	}
	
	@Test
	public void testRead01() {
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
	
	@Test
	public void testGetConnections01() {
		// As it turns out, you can't compare int arrays directly. Who'da thunk it.
		assertTrue(Arrays.equals(new int[] {2, 4, 5}, gs.getConnections(1)));
		assertTrue(Arrays.equals(new int[] {1, 4}, gs.getConnections(2)));
		assertTrue(Arrays.equals(new int[] {4, 5}, gs.getConnections(3)));
		assertTrue(Arrays.equals(new int[] {1, 2, 3}, gs.getConnections(4)));
		assertTrue(Arrays.equals(new int[] {1, 3}, gs.getConnections(5)));
	}
	@Test (expected = RuntimeException.class) 
	public void testGetConnections02() {
		gs.getConnections(10);
	}
	
	@Test
	public void testIsConnected01() {
		assertTrue(gs.isConnected(1, 2));
		assertTrue(gs.isConnected(1, 4));
		assertTrue(gs.isConnected(1, 5));
		assertTrue(gs.isConnected(2, 4));
		assertTrue(gs.isConnected(3, 4));
		assertTrue(gs.isConnected(3, 5));
		
		assertFalse(gs.isConnected(1, 3));
		assertFalse(gs.isConnected(2, 3));
		assertFalse(gs.isConnected(4, 5));
	}
}
