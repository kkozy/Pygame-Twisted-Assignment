Pygame-Twisted-Assignment
Programming Paradigms
Spring 2015

Kyle Kozak
Thomas Wack

==============================================================================

	Our project can be run using game.py <host|client> in the directory 
housing the game.py file as well as the p1.png and p2.png. It does not 
require any building or use of the "make" command. In order to run the game,
both players must be logged into the same student machine, as it uses the 
'localhost' designation to find the other player.  The first player to run the 
program must issue the command "game.py host" in order to let the program know
that it is effectively the server side.  The second player will issue the 
command "game.py client", at which time the connection should go through and
both of the players should see their "ships" appear onscreen.
	The game is a two player competitive game, where each player controls a 
ship that is capable of firing lasers.  As the each player hits the other,
that player's health shall decrease, eventually resulting in the ship's 
destruction.  The player will then respawn and may continue combat.  For each
succesful "kill", the player will earn a point.  The game is played until 
exhaustion or one of you begs for mercy. 
	Control of the ship's movement is done by pressing the arrow keys on the 
keyboard. Firing the laser is done by clicking the mouse at the location on 
screen you wish to aim at.  The ship will rotate to face the cursor.

==============================================================================

Notes: 
	- Run with command: game.py host|client
		-first run with host option, then with client option
	- Needs to be run on the same student machine such that localhost will work
	- Necessary files: game.py, p1.png, p2.png