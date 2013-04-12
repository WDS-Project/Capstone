/* 
 * This Javascript file contains methods and fields needed to display a
 * Gamestate on an HTML canvas.
 *
 * For coding purposes, the canvas display code will be separated out. In the
 * final version, all the Javascript will be rolled into one file.
 *
 * Author: WDS Project
 */

// ====================================
// ***    Cavas & viewport setup    ***
// ====================================
 
// Initial variable declarations
var 	canvas = document.getElementById('c'), // Canvas variable
	ctx = canvas.getContext('2d'), // drawing context of the canvas
	selection, // ID of currently selected planet
	connectionSelect, //connection object selected by user currently
	moves = []; // planned moves

// ****** Note: eventually, the size of view & world will need to be determinet from XML
	
// Defines the viewport and sets the canvas to be that size
var view = {
	height: 600,
	width: 800,
	offsetX: 0,
	offsetY: 0
};

// The canvas and the viewport are basically two names for the same thing.
canvas.width = view.width;
canvas.height = view.height;

// The world, on the other hand, is a different matter. It's bigger than the view,
// which is why this setup is needed in the first place. The view's offset is
// its offset from the origin of the world.
var world = {
	height: 1,
	width: 1 // These need to be set when the Gamestate is loaded.
};

var setWorldSize = function(height, width) {
	world.height = height;
	world.width = width;
}

// ===================================================================
// ***    Functions for allowing you to drag the camera around.    ***
// ===================================================================

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
canvas.onmousedown = function(e) {
	mouse = getMousePosition(e);
	canvas.mX = mouse.x;
	canvas.mY = mouse.y;
	canvas.hasMoved = false; // preserves selection if camera is dragged
	
	// Start tracking
	canvas.onmousemove = function(e) { goMouse(e); };
};

// This allows selection of planets & connections.
canvas.onclick = function(e) {
	mouse = getMousePosition(e);
	mouse.xCanv = (mouse.x + view.offsetX - canvas.offsetLeft);
	mouse.yCanv = (mouse.y + view.offsetY - canvas.offsetTop);

	for (var i = 1; i < gs.pList.length; i++) {
		if (gs.pList[i].isInside(mouse.xCanv, mouse.yCanv)) {
			if (gs.pList[i].owner == client.playerID) {
				if(client.state == Client.states.DEPLOYMENT) {
					client.deploy(i); //we're in deployment, so all we need is a planet
								//otherwise wait for a connection to be clicked
				} else if (client.state == Client.states.MOVING) {
					selection = i;
					gs.setActivePlanet(i);
				}
			} else if (gs.pList[i].owner == 0 && 
				client.state == Client.states.CHOOSING) {
				client.choose(i);
			}
			return;
		}
	}
	
	if(selection != null) {
		for (var i = 1; i < gs.cList.length; i++) {
			if (gs.cList[i].isInside(mouse.xCanv, mouse.yCanv)) {
				client.addMove(gs.cList[i]);
				return;
			}
		}
	}
	
	// If nothing was found and the camera hasn't recently been dragged,
	// cancel the current selection.
	if (!canvas.hasMoved) {
		selection = null;
		gs.setActivePlanet(0);
	}
};

// This function runs while the mouse is held down and moving.
function goMouse(e) {
	mouse = getMousePosition(e);
	view.offsetX += c.mX - mouse.x;
	view.offsetY += c.mY - mouse.y;
	canvas.mX = mouse.x;
	canvas.mY = mouse.y;
	canvas.hasMoved = true;
	
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
canvas.onmouseup = function(e) {
	canvas.onmousemove = function() {}; // i.e. do nothing
};

// ==================================================
// ***    Functions for drawing on the canvas.    ***
// ==================================================

var bgmove = 0;
// Clears the canvas by redrawing the background.
var clear = function() {
	ctx.save();
//	ctx.fillStyle = '#eee';
//	ctx.fillRect(0, 0, view.width, view.height);
	
	bgmove = (bgmove + 1) % 100;

	try {  
		var img = new Image();   // Create new img element
		img.src = 'starfield.jpg'; // Set source path
		ctx.drawImage(img, -bgmove, 0);
        } catch (err) { // If the image isn't found, color everything red.
        	// *** DOES NOT WORK IN CHROME ***
        	ctx.fillStyle = '#f00';
        	ctx.fillRect(0, 0, c.width, c.height);
        }

	ctx.restore();
}

// Draws the given Gamestate on the canvas.
var draw = function(gs) {
	ctx.save();
	
	// 1. Draw regions.
	for (var i = 1; i < gs.rList.length; i++)
		gs.rList[i].draw(ctx, view);
	
	// 2. Draw connections.
	for (var i = 1; i < gs.cList.length; i++)
		gs.cList[i].draw(ctx, view);
	
	// 3. Draw Planets.
	for (var i = 1; i < gs.pList.length; i++)
		gs.pList[i].draw(ctx, view, false);

	// 4. Draw the selected planet's connections (i.e. active connections).
	for (var i = 1; i < gs.cList.length; i++) {
		var con = gs.cList[i];
		if (con.p1 == selection)
			gs.cList[i].drawActive(ctx, view, 1);
		else if (con.p2 == selection)
			gs.cList[i].drawActive(ctx, view, 2);
	}
	
	// 5. Redraw the selected planet itself.
	if (selection != null)
		gs.pList[selection].draw(ctx, view, true);
};


