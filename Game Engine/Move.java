

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
    
    /**
     * Constructor for Move. Creates a move from a 2D int array
     * @param player    ID of the player
     * @param mves      Mini moves
     */
    public Move(int player, int[][] mves) {
        playerID = player;
        for(int i = 0; i < mves.length; i++) {
            moves.add(new ArrayList<Integer>());
            for(int j = 0; j < 3; j++)
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
    public Move(String move) throws NumberFormatException {
        //load the moves from the String into the 2D ArrayList
        String[] miniMoves = move.split("/");
        playerID = Integer.parseInt(miniMoves[0]);
        for(int i = 1; i < miniMoves.length; i++) {
            String[] sourceDestFleets = miniMoves[i].split(":");
            moves.add(new ArrayList<Integer>());
            moves.get(i-1).add(Integer.parseInt(sourceDestFleets[0]));
            moves.get(i-1).add(Integer.parseInt(sourceDestFleets[1]));
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
            for(int j = 0; j < 3; j++) {
                sb.append(""+moves.get(i).get(j) + " ");
            }
            sb.append("\n");
        }
        
        return sb.toString();
    }   
    
}
