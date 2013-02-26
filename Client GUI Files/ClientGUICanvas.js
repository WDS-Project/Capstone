/* 
 * For coding purposes, the canvas display code will be separated out. In the
 * final version, all the Javascript will be rolled into one file.
 *
 * Author: WDS Project
 */

// Initial variable declarations
var 	c = document.getElementById('c'), // Canvas variable
	ctx = c.getContext('2d'), // drawing context of the canvas
	select, // ID of currently selected planet
	moves = []; // planned moves

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
// which is why this setup is needed in the first place. The view's offset is
// its offset from the origin of the world.
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

};

// *** Functions for allowing you to drag the camera around. ***
// Gets the mouse position. Cross-browser for your convenience!
var getMousePosition = function(e) {
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
	//alert("Mousedown: view offsetX = " + view.offsetX + ", offsetY = " + view.offsetY);
	mouse = getMousePosition(e);
	c.mX = mouse.x;
	c.mY = mouse.y;
	// Start tracking
	c.onmousemove = function(e) { goMouse(e); };
};

// This function runs while the mouse is held down and moving.
function goMouse(e) {
	mouse = getMousePosition(e);
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

var bgmove = 0;

// Clears the canvas by drawing a big white rectangle over everything.
var clear = function() {
	ctx.save();
//	ctx.fillStyle = '#eee';
//	ctx.fillRect(0, 0, view.width, view.height);
	
	bgmove = (bgmove + 1) % 100;

	try {  
		var img = new Image();   // Create new img element
		img.src = 'X:/Capstone/Repository/Capstone/starfield.jpg'; // Set source path
		ctx.drawImage(img, -bgmove, 0);
        } catch (err) { // If the image isn't found, color everything red.
        	// *** DOES NOT WORK IN CHROME ***
        	ctx.fillStyle = '#f00';
        	ctx.fillRect(0, 0, c.width, c.height);
        }

	ctx.restore();
}

// Draws the given Gamestate.
var draw = function(gs) {
	// 1. Draw connections.
	ctx.save();
	ctx.strokeStyle = '#f0f';
	ctx.lineWidth = 3;
	for (var i = 1; i < gs.cList.length; i++) {
		//if (gs.cList[i] == null) continue;
		var con = gs.cList[i].split(',');
		var p1 = gs.pList[con[0]];
		var p2 = gs.pList[con[1]];
		
		ctx.beginPath(); // You NEED THIS for it to draw successfully
		ctx.moveTo(p1.xPos - view.offsetX, p1.yPos - view.offsetY);
		ctx.lineTo(p2.xPos - view.offsetX, p2.yPos - view.offsetY);
		ctx.stroke();
		ctx.closePath();
		
	}
	ctx.restore();
	
	// 2. Draw Planets.
	ctx.save();
	ctx.strokeStyle = '#fff';
	ctx.lineWidth = 2;
	for (var i = 1; i < gs.pList.length; i++) {
		var planet = gs.pList[i];
		ctx.fillStyle = planet.color;
		ctx.beginPath();
		ctx.arc(planet.xPos - view.offsetX, planet.yPos - view.offsetY,
			planet.radius, 0, 2*Math.PI, true);
		ctx.fill();
		// 2.5. Draw number of fleets.
		ctx.stroke();
		ctx.closePath();
	}
	ctx.restore();
		
	// 3. Draw arrows (both planned and selection)
	
	// 4. Draw the selected planet
};

// DrawLoop(); // Start drawing the canvas --> Gets called in ClientGUI.js


