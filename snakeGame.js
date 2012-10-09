/* Welcome to Snake as realized through Javascript and the HTML5 Canvas. I'll be
   your host, The Guy Coding This Page. Join us for more fun and frivolity
   throughout the year as we continue on this magical journey through our CS
   Capstone. */

// First, define all global variables. This may not be ideal, but it works for now.
var height = 300, width = 500, // size of the canvas
    gLoop, snake,
    diff = 500, // difficulty modifier for time (unimplemented)
    grid = [], // Game grid. Each square is 5x5px; 0->Empty, -1->Food, Number->Snake link (1=head, last=tail) 
    scale = 20,
    c = document.getElementById('c'),
    ctx = c.getContext('2d');
    
c.width = width; // should be obvious
c.height = height;

// Initializes the grid to be all blank.
var gridSize = [];
gridSize.width = width / scale; // meh
gridSize.height = height / scale;
for (var i = 0; i < gridSize.width; i++)
	grid[i] = [];
for (var i = 0; i < gridSize.width; i++)
	for (var j = 0; j < gridSize.height; j++)
		grid[i][j] = 0;

// Defines a method for filling squares on the grid
grid.fill = function(i, j, color) {
	var x = i * scale,
	    y = j * scale;
	ctx.fillStyle = color;
	ctx.fillRect(x, y, scale-1, scale-1);
};

// Draws the background.
var clear = function() {
	ctx.fillStyle = '#F55';
	ctx.fillRect(0, 0, width, height);
}

// Defines the player's snake class.
var Player = function() {
	var that = this;
	that.color = '#0FF';
	that.length = 3;
	that.direction = 'S'; // cuz why not
	that.head = [0, 0];
	
	that.draw = function() {
		for (var i = 0; i < gridSize.width; i++) {
			for (var j = 0; j < gridSize.height; j++) {
				if (grid[i][j] > 0)
					grid.fill(i, j, that.color);
				if (grid[i][j] == -1) // while I'm here...
					grid.fill(i, j, '#06F'); // draw the food too
			}
		}
		ctx.fillStyle = '#000';
		ctx.fillRect(that.head[0]*scale, that.head[1]*scale, scale-1, scale-1);
	};
	
	that.move = function() { 
		var newHead = [];
		if (that.direction == 'W')
			newHead = [that.head[0]-1, that.head[1]];
		else if (that.direction == 'E')
			newHead = [that.head[0]+1, that.head[1]];
		else if (that.direction == 'N')
			newHead = [that.head[0], that.head[1]-1];
		else
			newHead = [that.head[0], that.head[1]+1];
		
		// Wraparound of the head
		if (newHead[0] < 0)
			newHead[0] = gridSize.width-1;
		if (newHead[0] >= gridSize.width)
			newHead[0] = 0;
		if (newHead[1] < 0)
			newHead[1] = gridSize.height-1;
		if (newHead[1] >= gridSize.height)
			newHead[1] = 0;
		
		// Decide what to do in the new space
		if (grid[newHead[0]][newHead[1]] == -1) {
			// Food; grow, then move
			that.grow(newHead);
			return;
		} else if (grid[newHead[0]][newHead[1]] > 0) {
			// Hit the snake; done.
			GameOver();
			return;
		} else {
		
			// Move forward, nothing special
			var temp = [];
			for (var i = 0; i < gridSize.width; i++) {
				for (var j = 0; j < gridSize.height; j++) {
					if (grid[i][j] > 0) {
						if (grid[i][j] >= snake.length)
							temp = [i, j]; // to find the last segment
						grid[i][j]++; // increment current segment by one
					}
				}
			}
			
			grid[newHead[0]][newHead[1]] = 1; // mark new head
			grid[temp[0]][temp[1]] = 0; // blank last segment
			that.head = newHead;
		}
	}
	
	that.grow = function (newHead) {
		// Move forward
		var temp = [];
		for (var i = 0; i < gridSize.width; i++) {
			for (var j = 0; j < gridSize.height; j++) {
				if (grid[i][j] > 0) {
					if (grid[i][j] >= snake.length)
						temp = [i, j]; // to find the last segment
					grid[i][j]++; // increment current segment by one
				}
			}
		}
		
		grid[newHead[0]][newHead[1]] = 1; // mark new head, deleting food square
		that.length++;// DON'T blank last segment (i.e. grow)
		that.head = newHead;
		spawnFood();
	}
	
	return that;
};

var snake = new Player();
// This bit just makes a default snake
for (var i = 0; i < snake.length; i++) {
	grid[i][0] = i+1;
}

window.onkeydown = keydownControl;

function keydownControl(e) {
    if(e.keyCode==37 && snake.direction != 'E') { // left
    	    snake.direction = 'W';
    } else if (e.keyCode==38 && snake.direction != 'S') { // up
    	    snake.direction = 'N';
    } else if (e.keyCode==39 && snake.direction != 'W') { // right
    	    snake.direction = 'E';
    } else if (e.keyCode==40 && snake.direction != 'N') { // down
    	    snake.direction = 'S';
    }
}

function spawnFood() {
	var randomX = Math.floor(Math.random()*(gridSize.width)),
	    randomY = Math.floor(Math.random()*(gridSize.height));
	
	if (grid[randomX][randomY] != 0)
		spawnFood(); // if there's already something there, recurse
	else
		grid[randomX][randomY] = -1;
}
spawnFood(); // initial spawn

// The general game loop. Each run is a frame.
var running = true;
var GameLoop = function() {
	if (running) {
		clear(); // redraw background
		snake.move();
		snake.draw();
		gLoop = setTimeout(GameLoop, (1000/5)); // when 200ms have passed, recurse & redraw (5fps max)
	}
};
var GameOver = function () {
	running = false;
	alert("Game over! Your score is "+ (snake.length - 3) + ". How sad.");
}
GameLoop(); // DERP LET'S GO
