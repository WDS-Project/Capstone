
import org.junit.*;
import static org.junit.Assert.*;

/**
 *
 * @author Alana
 */
public class MoveTest {
    
    Move move;
    StringBuilder sb;
    String mve = "2/000.000.000/1:2:3/4:5:6/7:8:9/";
    
    @Before
    public void setUp() {
        move = new Move(mve);
        
        sb = new StringBuilder();
        sb.append(move.getPlayerID() + "\n");
        while(move.hasNext()) {
            int[] ints = move.next();
            for(int i = 0; i < 3; i++)
                sb.append(ints[i] + " ");
            sb.append("\n");
        }
    }
  
    @Test
    public void moveTest1() {
        assertEquals(sb.toString(), "2\n1 2 3 \n4 5 6 \n7 8 9 \n");
    }
    
    @Test
    public void testEmptyMove() {
        Move move = new Move(0, "000.000.000",new int[0][0]);
        assertFalse(move.hasNext());
    }
    
    @Test
    public void testEmptyMove2() {
        String mov = "2/000.000.000/";
        Move m = new Move(mov);
        assertFalse(m.hasNext());
    }
}
