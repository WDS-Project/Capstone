import org.junit.*;
// Josh Polkinghorn

/* This is a test class for the Gamestate class. */
public class GamestateTest {
	@Test
	public void testRead01() {
		Gamestate gs = new Gamestate("src/TestGS.xml");
		System.out.println(gs.toString());
	}
}
