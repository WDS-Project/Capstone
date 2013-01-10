
public class MoveTest {

/**
     * A main method for testing purposes only.
     * @param args 
     */
    public static void main(String[] args) {
        String mve = "2/1:2:3/4:5:6/7:8:9/";
        Move move = new Move(mve);
        System.out.println(move.getPlayerID());
        while(move.hasNext()) {
            int[] ints = move.next();
            for(int i = 0; i < 3; i++)
                System.out.print(ints[i] + " ");
            System.out.println();
        }
    }
    
 }
