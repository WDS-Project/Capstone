

import java.util.ArrayList;
import java.util.NoSuchElementException;

/**
 * This class houses a representation of a move
 * made by the user. It is created by the engine
 * upon receipt of a move for processing purposes.
 * @author Alana Weber
 */
public class Move {
    
    /*
     * Note: This is what a Move looks like when it is received
     * from the user's HTTP POST request:
     * <playerID>/<source>:<dest>:<numFleets>/<source>:<dest>:<numFleets>/etc
     */
    
    private int playerID;
    private String ipAddr;
    private ArrayList<ArrayList<Integer>> moves = new ArrayList<ArrayList<Integer>>();;
    /*
     * This 2D array looks like this:
     *        sourcePlanetID   destPlanetID   numberOfFleets
     *       -----------------------------------------------
     * move 0|
     * move 1|
     * move 2|
     * etc
     * So it's essentially an n x 3 matrix
     */
    private int currentMoveIndex = -1; //which part of the move we're on
    private final int MOVE_LENGTH = 3;
    
    /**
     * Constructor for Move. Creates a move from a 2D int array
     * @param player    ID of the player
     * @param mves      Mini moves
     */
    public Move(int player, String ipAdd, int[][] mves) {
        playerID = player;
        ipAddr = ipAdd;
        for(int i = 0; i < mves.length; i++) {
            moves.add(new ArrayList<Integer>());
            for(int j = 0; j < MOVE_LENGTH; j++)
                moves.get(i).add(mves[i][j]);
        }
        currentMoveIndex = 0;
    }
    
    /**
     * Constructor for Move
     * @param move      String that represents the move request
     * @throws NumberFormatException    If the move is not
     *                              formatted correctly
     */
    public Move(String move, String IP) throws Exception {
        /*Some checks to account for network anomalies.*/
        //I'm not sure if the first character in the request will be /
        // or the ID number
        if(move.length() < 1)
            throw new Exception("Empty move.");
        if(move.charAt(0) == '/')
            move = move.substring(1);
        
        ipAddr = IP;
        
        //load the moves from the String into the 2D ArrayList
        String[] miniMoves = move.split("/");
        playerID = Integer.parseInt(miniMoves[0]);
        for(int i = 1; i < miniMoves.length; i++) {
            String[] sourceDestFleets = miniMoves[i].split(":");
            
            //if the move is not formatted correctly
            if (sourceDestFleets.length != MOVE_LENGTH)
                throw new Exception("Incorrectly formatted move. Must contain " +
                        "source, destination, and fleets.");
            
            moves.add(new ArrayList<Integer>());
            moves.get(i-1).add(Integer.parseInt(sourceDestFleets[0]));
            moves.get(i-1).add(Integer.parseInt(sourceDestFleets[1]));
            
            if(Integer.parseInt(sourceDestFleets[2]) <= 0)
                throw new Exception("You can't move 0 or fewer fleets.");
            
            moves.get(i-1).add(Integer.parseInt(sourceDestFleets[2]));
        }
        currentMoveIndex = 0;
    }
    
    /**
     * Returns the next mini-move, consisting of a source planet ID,
     * destination planet ID, and number of Fleets, in that order.
     * @return  int array with the above information
     */
    public int[] next() {
        if(!hasNext())        
            throw new NoSuchElementException();
        
        //This is happening because ArrayList.toArray returns Object[]
        //So this is how we avoid casting
        int[] currentMove = new int[moves.get(currentMoveIndex).size()];
        //this size will always be 3 incidentally
        for(int i = 0; i < currentMove.length; i++)
            currentMove[i] = (int)moves.get(currentMoveIndex).get(i);
        currentMoveIndex++;
        
        return currentMove;
    }
    
    /**
     * Checks to see if there are any more mini moves in the list.
     * @return  True if there is, false if not.
     */
    public boolean hasNext() {
        if(currentMoveIndex < 0 || currentMoveIndex >= moves.size())
            return false;
        
        return true;
    }
    
    /**
     * Getter for PlayerID
     * @return  ID of the player
     */
    public int getPlayerID(){ return playerID; }
    
    /**
     * Return IP address of player making the move
     * @return 
     */
    public String getIP() { return ipAddr; }
    
    /**
     * Getter for the next index.  Not sure why this is useful.
     * @return      Index of the next move in the 2D ArrayList (that is,
     * the next row in the matrix.)
     */
    public int getNextMoveIndex() { return currentMoveIndex + 1; }
    
    /**
     * Getter for the total number of moves.
     * @return  The total number of moves.
     */
    public int getNumberOfMoves() { return moves.size(); }  
    
    /**
     * Returns a String representation of this move.
     * @return 
     */
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("Player ID: " + playerID + "\n");
        for(int i = 0; i < moves.size(); i++) {
            for(int j = 0; j < MOVE_LENGTH; j++) {
                sb.append(""+moves.get(i).get(j) + " ");
            }
            sb.append("\n");
        }
        
        return sb.toString();
    }   
    
}
