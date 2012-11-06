/* In this magical journey of wonderment and excitement, I will be attempting
   to use several techniques to prototype the GUI we'll be using for our
   Capstone project (hopefully). Here's hoping this works. 11/4/12
*/

// Initial variable declarations
var 	gLoop, // the game loop - see GameLoop() below
	selection,
	c = document.getElementById('c'),
	ctx = c.getContext('2d');

// Defines the viewport and sets the canvas to be that size
var view = { // view = new object.
	height: 600, // new attribute
	width: 800,
	offsetX: 0,
	offsetY: 0
};

// The canvas and the viewport are basically two names for the same thing.
c.width = view.width;
c.height = view.height;

// The world, on the other hand, is a different matter. It's bigger than the view,
// which is why this crazy setup is needed in the first place.
var world = {
	height: 1500,
	width: 1600
};

/* *****Notes about Canvas states*****
   Canvas states are stored on a stack. Every time the save method is called, 
   the current drawing state is pushed onto the stack. A drawing state consists of:
   - Transformations (translations, rotations, scaling, etc.)
   - strokeStyle, fillStyle, etc.
   - Clipping path (whatever that is)
   
   ctx.save(); --> Saves the current state of the context.
   ctx.restore(); --> Reverts to last saved context state.
   
   Here's the one we really want:
   ctx.transform(x, y);
   
   Note that x & y are DELTAS - i.e. transform(0,0) moves nowhere and does NOT
   reset to the origin.
*/

// A generic circle.
var Circle = function(xPos, yPos, rad) {
	var that = this;
	that.color = '#af3';
	that.radius = rad;
	that.x = xPos;
	that.y = yPos;
	
	// This draws a given circle. The circle already knows its own color,
	// radius, and (x, y) coordinates.
	that.draw = function() { // I think that ideally you pass it ctx, but since ctx is global here...
		ctx.save();
		ctx.fillStyle = that.color;
		ctx.strokeStyle = '#fff';
		ctx.lineWidth = 3;
		ctx.beginPath(); // You NEED THIS for it to draw successfully
		
		// The position of each circle is modified to account for the
		// offset of the view. Circles that fall outside of the view
		// (i.e. canvas) aren't drawn at all.
		ctx.arc(that.x - view.offsetX, that.y - view.offsetY, that.radius,
			0, 2*Math.PI, true);
		// Other things being drawn will need to incorporate these
		// offsets in the same manner.
		
		ctx.fill();
		ctx.stroke();
		ctx.closePath();
		ctx.restore();
	};

	// Tests if a point is inside this circle.
	that.isInside = function(x, y) {
		var h = Math.sqrt(Math.pow( (x - c.offsetX - that.x + view.offsetX), 2) + Math.pow(y - that.y + view.offsetY - c.offsetY, 2));
		if (h <= that.radius)
			return true;
		else
			return false;
	};
};

// This just generates a bunch of random circles. ~~ --> Math.Floor().
var circles = [];
circles.size = 200;
for (var i = 0; i < circles.size; i++) {
	x = ~~(Math.random() * world.width);
	y = ~~(Math.random() * world.height);
	rad = ~~(Math.random() * 20 + 10);
	circles[i] = new Circle(x, y, rad);
}

// *** Functions for allowing you to drag the camera around. ***
// Gets the mouse position. Cross-browser for your convenience!
var getMouse = function(e) {
	var posx = 0, posy = 0;
	if (!e) var e = window.event;
	if (e.pageX || e.pageY) {
		posx = e.pageX;
		posy = e.pageY;
	}
	else if (e.clientX || e.clientY) {
		posx = e.clientX + document.body.scrollLeft
			+ document.documentElement.scrollLeft;
		posy = e.clientY + document.body.scrollTop
			+ document.documentElement.scrollTop;
	}
	return { x:posx, y:posy };
};

// When the mouse is clicked, the camera starts following it.
c.onmousedown = function(e) {
	mouse = getMouse(e);
	c.mX = mouse.x;
	c.mY = mouse.y;
	// Start tracking
	c.onmousemove = function(e){ goMouse(e); };
};

// This function runs while the mouse is held down and moving.
function goMouse(e) {
	mouse = getMouse(e);
	view.offsetX += c.mX - mouse.x;
	view.offsetY += c.mY - mouse.y;
	c.mX = mouse.x;
	c.mY = mouse.y;
	
	// Keeps the camera within the world.
	if (view.offsetX > world.width - view.width)
		view.offsetX = world.width - view.width;
	if (view.offsetY > world.height - view.height)
		view.offsetY = world.height - view.height;
	if (view.offsetX < 0)
		view.offsetX = 0;
	if (view.offsetY < 0)
		view.offsetY = 0;
}

// When the mouse is let up, the camera stops following it.
c.onmouseup = function(e) {
	c.onmousemove = function() {}; // i.e. do nothing
};

// This allows selection of planets and all that jazz.
c.onclick = function(e) {
	mouse = getMouse(e);
	for (var i = 0; i < circles.size; i++)
		if (circles[i].isInside(mouse.x, mouse.y))
			selection = i;
}

// Gets the position of the canvas relative to the page.
var curleft = curtop = 0; // current cumulative offset from left/top
var obj = c;
if (obj.offsetParent) {
	do {
		curleft += obj.offsetLeft;
		curtop += obj.offsetTop;
	} while (obj = obj.offsetParent);
}
c.offsetX = curleft;
c.offsetY = curtop;

// These variables allow the background to scroll.
var bgOffset = 0,
	bgDirect = 1;
	
// Clears the canvas by drawing a big white rectangle over everything.
var clear = function() {
	ctx.save();
	try {  
		var img = new Image();   // Create new img element
		img.src = 'starfield.jpg'; // Set source path
		ctx.drawImage(img, -bgOffset, 0);
		bgOffset += bgDirect;
		if (bgOffset > 100)
			bgDirect = -1;
		else if (bgOffset < 0)
			bgDirect = 1;
        } catch (e) { // If the image isn't found, color everything red.
        	ctx.fillStyle = '#f00';
        	ctx.fillRect(0, 0, c.width, c.height);
        };

	ctx.restore();
}

// Highlights the selected circle. Same as Circle.draw(), but a little bigger.
var drawSelection = function() {
	var that = circles[selection];
	if (that) { // if there is actually a selection...
		ctx.save();
		ctx.fillStyle = "#f00";
		ctx.beginPath();
		ctx.arc(that.x - view.offsetX, that.y - view.offsetY, that.radius+5,
			0, 2*Math.PI, true);		
		ctx.fill();
		ctx.closePath();
		ctx.restore();
	}
};

// *******************************************************
// The following code creates connections between planets.
//var connection = 
// *******************************************************

// Main loop. Every 20ms, it redraws everything.
var GameLoop = function() {
	clear();
	drawSelection();
	for (var i = 0; i < 200; i++) {
		circles[i].draw();
	}
	gLoop = setTimeout(GameLoop, 1000/50); // when 20ms have passed, recurse & redraw (50fps max)
};
GameLoop(); // DERP LET'S GO


