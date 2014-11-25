### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###
### BGHelper V1.9
###		   
### Author: SolarLune
###
### Contributors: Siegel (TrackTo)
###
### Date Updated: 8/3/12
###
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
###
### This script and the functions below
### are under the 'do what you wish' license
### agreement under a single condition. 
### You may use any part of the scripts in your own works, commercial,
### educational, or personal, for free, -WITH- ATTRIBUTION that comprises
### of stating the name of the module that you used (BGHelper), as well as the 
### name of the author of the module (SolarLune), as well as contributors for
### each function that you used (e.g. if you use the TrackTo function, attribute
### Siegel, as well as SolarLune (for the module)).
###
###
###
### This script and all functions within (with exceptions to contributed works)
### are the property of the author, SolarLune -
### even if you, as the end user, should edit the script, it is still the property of the author, 
### and as such, he has rights to the usage of the script and related functions.
### He may revoke rights for usage of this script and associated functions at any time, for any reason.
###
###
###
### By using this script, you agree to this license agreement.
###
### You may NOT edit this license agreement.
###
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

### CHANGELOG ###

### 5/23/11 - Release.

### 5/24/11 - V1.2 Update. Updated TrackTo, as well as added GetAngle and LOD (renaming the original LOD function to LODSimple).
### Updated Clamp to only work with one value (max will be negative minimum).

### At some point, V1.3 Update. Added callbacks, which allow for getting the frame a value changes, and acting on it.

### 7/28/11 - V1.4 Update. Added some mathematic functions such as GetDimensions, LockToGrid, and LockToGridList.

### 9/6/11 - V1.5 Update. Added a Node Pathfinding class. Also added Reverse... Apparently. Also added the CGRange class for gradual
### looping processes.

### 9/14/11 - V1.6 Update. Added a soft-body pinning function, SoftBodyPin. Also changed MouseOrbit to work with no button press - 
### mb = 0 == no button press, 1 = left mb, 2 = middle, and 3 = right. Also added reversal of direction capability to the MouseOrbit functions.

### 9/17/11 - Finished NodeMaps and NodeMap-based pathfinding. PosClose no longer returns -1; just either 1 or 0.

### 10/19/11 - Idea for expanding NodeMaps, but added the ImageBindID function, which gives the OpenGL bind ID for a given image.

### 10/22/11 - Still haven't implemented the NodeMap idea. :P Anyway, worked a little on the CGRange class to add a function to wipe it.

### 11/7/11 - I don't think I will implement that NodeMap idea (multiple paths; take the shortest), as pathfinding is faster and easier built-in to the BGE.
### Anyway, I'm adding a Noise function! :D

### 1/12/12 - Implemented Keyboard key press functions and a joystick class for checking joystick values 
### (requires a sensor for each joystick you want to poll).

### 8/3/12 - V1.9 - Been working on this steadily. Not sure of how many things I've fixed / done, but it should be better than before.
### Added a smoother mouse-look function (the old version's still there for compatability, but the new one does the same
### stuff). I'm calling this release 1.9.

from bge import logic
from bge import types
from bge import render
from bge import events
from bge import constraints
from bge import texture

from copy import *

import math
import mathutils
import random

import os
import sys
import time

#### MODULE CONSTANTS ####

# COLOR CONSTANTS #

# Constants can be accessed as normal variables; assuming you imported the module as 'import BGHelper',
# you can access the color red by using 'BGHelper.red', for example. Alternatively, if you imported the module
# as 'from BGHelper import *', you could just use 'obj.color = red'.

red = [1.0, 0.0, 0.0, 1.0]
green = [0.0, 1.0, 0.0, 1.0]
greenpine = [0.5, 1.0, 0.0, 1.0]
blue = [0.0, 0.0, 1.0, 1.0]
bluesky = [0.0, 0.5, 1.0, 1.0]
yellow = [1.0, 1.0, 0.0, 1.0]
orange = [1.0, 0.5, 0.0, 1.0]
mustard = [0.5, 0.25, 0.0, 1.0]
brown = [0.1, 0.05, 0.0, 1.0]

white = [1.0, 1.0, 1.0, 1.0]
black = [0.0, 0.0, 0.0, 1.0]

charcoal = [0.1, 0.1, 0.1, 1.0]
graydark = [0.25, 0.25, 0.25, 1.0]
gray = [0.5, 0.5, 0.5, 1.0]
graylight = [0.8, 0.8, 0.8, 1.0]
silver = [0.9, 0.9, 0.9, 1.0]

redpastel = [1.0, 0.25, 0.25, 1.0]
greenpastel = [0.25, 1.0, 0.25, 1.0]
bluepastel = [0.25, 0.25, 1.0, 1.0]
yellowpastel = [1.0, 1.0, 0.25, 1.0]
orangepastel = [1.0, 0.75, 0.25, 1.0]
mustardpastel = [0.8, 0.6, 0.4, 1.0]
brownpastel = [0.5, 0.3, 0.1, 1.0]

halfpi = math.pi / 2.0			# Half of pi - a 90 degree rotation
twopi = math.pi * 2.0			# Two pi - a full 360 degree rotation
fourthpi = math.pi / 4.0		# A fourth of pi - a 45 degree rotation

vectup = mathutils.Vector([0, 0, 1])		# Quick vectors; faster than the functions to type out
vectdown = mathutils.Vector([0, 0, -1])
vectright = mathutils.Vector([1, 0, 0])
vectleft = mathutils.Vector([-1, 0, 0])
vectforward = mathutils.Vector([0, 1, 0])
vectback = mathutils.Vector([0, -1, 0])

#############
## CLASSES ##
#############

class CCallback(object):

	"""
	A callback class for making callback objects. These objects are useful for telling when a value changes - for example, you
	could use a callback to tell when the Player collides with an object other than the one he is currently colliding with (None, if
	he isn't colliding with anything). You can use a callback object to execute a function when the callback returns - in the above
	example, you could create an object or particle when this callback returns positive.
	"""

	def __init__(self):
	
		self.calls = dict({})
		self.idindex = 0
	
	def Add(self, check, onchange, id = None, defaultvalue = 1, mode = 0):
	
		"""
		Add a callback to the list for this Callback object to take care of.
		
		check = Checking function for the callback (e.g. a function that returns obj.position.x < 10), like:
		
		lambda : obj.getDistanceTo(sce.objects['Dest']) < 5
		
		onchange = Returning function for the callback (e.g. a function that does: obj.endObject(); 
		this would run when obj.position.x < 10, but only the one frame that this is true (default))
		
		id = Name / ID for the callback; Not necessary, but is used to refer to the callback later. Can be a number, string, etc.
		
		defaultvalue = What the default value is; when the callback is first added, if defaultvalue = 0, 
		then the previous value recorded for the callback will be None. Unless the checking function returns None, then the returning function will run.
		
		mode = (0 by default); what mode the callback is; 0 == changed, 1 == equals, 
		2 == greater than, 3 == less than; try to keep this set to 0.
		
		This function also returns the original callback ID, so you can get it later if you need to.
		"""
	
		if defaultvalue == 0:
			callback = [check, onchange, mode, None]
		else:
			callback = [check, onchange, mode, check()]
			
		if id == None:				# If you don't specify an ID, then it will return an internal ID counter
			id = self.idindex
			self.idindex += 1
			
		self.calls[id] = callback	# A list of all calls for this callback object - the checking function, the function to return if the callback is true, the mode, as well as the previous value (used by the Change mode, which is default)
		
		return id					# Returns the ID number if you want to keep track of it and access the Callback object's callbacks through object.calls[id]

	def Remove(self, id = None):
	
		"""
		Removes the callback with the specified ID from the list of callback functions for this object.
		"""

		if id == None:
			self.calls.popitem()
		else:
			del self.calls[id]
			
	def RemoveAll(self):
	
		self.calls.clear()

	def Get(self, id):
	
		return self.calls[id]
		
	def Update(self):
		"""
		Update the callbacks, and run their associated functions if they change, or for whatever mode each callback is in.
		"""
	
		for c in self.calls:
			
			call = self.calls[c]
		
			value = call[0]()
			
			mode = call[2]

			if call[3] != value and mode == 0:		# Changed (not equal)
				call[1](call[3])
				call[3] = value
			elif call[3] == value and mode == 1:	# Equals (experimental; stick with mode 0)
				call[1](call[3])
				call[3] = value
			elif call[3] > value and mode == 2:		# Greater than (experimental; stick with mode 0)
				call[1](call[3])
				call[3] = value
			elif call[3] < value and mode == 3:		# Less than (experimental; stick with mode 0)
				call[1](call[3])
				call[3] = value
	
class CBoxBounds(object):

	"""
	A BoxBounds object for collision testing. The Box Bounds object can check a point for collision in that object (via the PointBoxInt
	function), or check another BoxBounds object for collision (via the BoxBoxInt function).
	
	You update the bounds each frame with the Update() function, and for op, use the point to move the bounds object around by.
	The DebugDraw function is used to draw the BoxBounds object onscreen - if the bounds object is active but not colliding with anything,
	it's white. If it is colliding, it's red, and if the bounds object is inactive, then it is yellow.
	
	The SetBounds function is used to set the bounds of the object - this should be used before the Update function.
	"""

	def __init__(self, topleft, bottomright, originpoint = [0, 0, 0], obj = None):
	
		self._box = []
		self.bounds = []
		self.collision = []		# If this bounds object is involved in a collision, and if so, then with which object
		self.active = 1			# If this bounds object should be considered for collisions
		self.originpoint = originpoint
		
		self.SetBounds(topleft, bottomright)
		
		#self.owner = pass
		#op = self.originpoint
		#self._box = [ [topleft[0], topleft[1], topleft[2]], [bottomright[0], bottomright[1], bottomright[2]] ]	# Un-transformed box
		if obj == None:
			self.owner = logic.getCurrentController().owner
		else:
			self.owner = obj
	
	def SetBounds(self, topleft, bottomright):
		#op = self.originpoint
		self._box = [ [topleft[0], topleft[1], topleft[2]], [bottomright[0], bottomright[1], bottomright[2]] ]
		
	def Update(self, op = [0, 0, 0]):
		self.originpoint = op
		b = self._box
		self.bounds = [ [op[0] + b[0][0], op[1] + b[0][1], op[2] + b[0][2]], [op[0] + b[1][0], op[1] + b[1][1], op[2] + b[1][2]] ]
		
		self.points = [
		[op[0] + b[0][0], op[1] + b[0][1], op[2] + b[0][2]],
		[op[0] + b[1][0], op[1] + b[0][1], op[2] + b[0][2]],
		[op[0] + b[0][0], op[1] + b[1][1], op[2] + b[0][2]],
		[op[0] + b[0][0], op[1] + b[0][1], op[2] + b[1][2]],
		[op[0] + b[1][0], op[1] + b[1][1], op[2] + b[0][2]],
		[op[0] + b[0][0], op[1] + b[1][1], op[2] + b[1][2]],
		[op[0] + b[1][0], op[1] + b[0][1], op[2] + b[1][2]],
		[op[0] + b[1][0], op[1] + b[1][1], op[2] + b[1][2]],
		]
		
		self.bounds.sort()
		
		self.collision = []	# Reset the collision
			
	def BoxBoxInt(self, boxone, boxtwo):
			
		if boxone.active and boxtwo.active:
			
			for p in boxone.points:
			
				col = self.PointBoxInt(boxtwo, p)
			
				if col != None:
				
					boxone.collision.append([boxtwo, col])
					boxtwo.collision.append([boxone, col])
					return col
				
		return None
		
	def PointBoxInt(self, box, point):
	
		if box.active:
	
			if point[0] > box.bounds[0][0] and point[1] > box.bounds[0][1] and point[2] > box.bounds[0][2] \
			and point[0] < box.bounds[1][0] and point[1] < box.bounds[1][1] and point[2] < box.bounds[1][2]:
				
				box.collision.append(['point', point])
				return point

		return None
	
	def DebugDraw(self):
			
		for p in range(len(self.points)):
		
			if p < len(self.points) - 1:
			
				pn = p + 1

				if self.active:
					if self.collision != []:
						color = [1, 0, 0]
					else:
						color = [1, 1, 1]
				else:
					color = [1, 1, 0]
					
				render.drawLine(self.points[p], self.points[pn], color)
				
class CPersistence(object):

	"""
	Persistence of scene saver for BGE games.
	You can use this to save and load select information from objects to allow for persistence across scenes.
	"""

	def __init__(self):
	
		self.perlist = {}
		
	def Save(self, savelist, newlist = 1):
	
		"""
		Saves the object / value pairings in savelist. Savelist should look like this:
		
		[
			[sce.objects['Player'], 'worldPosition'],
			[sce.objects['Switch'], 'on'],
			...
		]
		
		Notice that it's all in a single list. Even if there is just one object / value pairing, it 
		should still be contained in another list.
		
		Saving will modify the internal persistency list (which is sorted by scene name). The function will also return
		the list for you to look at, if you wish - this should be the result:
		
		[
			['Player', 'worldPosition', <Actual worldPosition value, e.g. Vector...>, 1] - The last value, 1, indicates this is a built-in variable, not a custom one.
			['Switch', 'on', 1, 0] - This last value is 0, indicating it's a custom variable.
		]
		"""
	
		sce = logic.getCurrentScene()
		
		if not sce.name in self.perlist or newlist:	# Initializes the scene list if either the list doesn't exist for the current
			self.perlist[sce.name] = []	# scene, or if you want to wipe the persistence list. It's possible that you won't want to override the
										# previous list, like if you used SaveAll, and then want to add in specific properties.
		for o in savelist:
		
			if o[1] in o[0]:
				self.perlist[sce.name].append([o[0].name, o[1], o[0][o[1]], 1])
			else:
				self.perlist[sce.name].append([o[0].name, o[1], getattr(o[0], o[1], None), 0])
				
		return (self.perlist[sce.name])	# Returns the list for good measure
			
	def SaveAll(self, objlist = None, newlist = 1):
	
		"""
		Saves in the persistence list all -custom- variables for each object.
		Generally not necessary, nor is it stable if you have references to objects that may not exist anymore.
		Is not tested, and so is not optimized for release.
		
		objlist = an optional list that lists which objects to save data from the current scene; 
		if not specified, the whole scene object list is used.
		"""
	
		sce = logic.getCurrentScene()
	
		if not sce.name in self.perlist or newlist:	# Initialize the list of object properties
			self.perlist[sce.name] = []
		
		if objlist == None:
			objlist = sce.objects
		
		for ob in objlist:
			
			if ob.invalid:
				self.perlist[sce.name].append({ob.name, None, None})					# Tells that an object is dead, as the reference is invalid
			else:
				self.perlist[sce.name].append({ob.name, 'attrDict', ob.attrDict})	# Tells that there's an attribute dictionary up ahead
	
		return self.perlist[sce.name]
		
	def Load(loadlist = None):
	
		sce = logic.getCurrentScene()
		
		if loadlist == None:
			loadlist = self.perlist[sce.name]
		
		for l in loadlist:
		
			print (l)
			
			obname = l[0]	# Object name
			var = l[1]		# Variable name
			value = l[2]	# Variable value
			built = l[3]	# Built-in variable?
			
			obj = sce.objects[obname]
			
			if built == 1:
				setattr(obj, var, value)
			else:
				obj[var] = value
				
		print ('list loaded!')
				
		return loadlist
	
class CNodePath(object):

	"""
	Node path class for moving along paths. Makes nice simple AI. A simple set-up can be seen in the 
	NodePath scene in the example file that should be bound with the BGHelper module.
	
	The idea is simple. You create a NodePath object:
	
	obj['np'] = CNodePath()
	
	You calculate a path using a list:
	
	obj['np'].Calculate([x for x in sce.objects if 'Node' in x.name()], 'nodeindex') # Creates a path consisting of all objects with 'Node' in their names, and sorts them by their 'nodeindex' variables
	
	And finally move on that list:
	
	obj['np'].MovePath(obj, 0.1)
	
	It's not too difficult to utilize.
	
	self.path = The path from beginning to end. You can only have one path per NodePath object, but you can have several, or make many
	and swap them out when necessary (at leat, you should be able to).
	self.currentnode = The current node on the path for this object.
	self.direction = Direction the movement is in - 1 = forward (from the first path point to the last), and -1 = backward.
	self.movespeed = The movement speed this object moves when moving from Node point to Node point.
	self.oncomplete = What to do on path completion - 0 = continue the path, and 1 = reverse movement.
	self.pathcompleted = A simple flag variable that alerts you for one game frame when a path has been completed.
	"""
	
	def __init__(self):
	
		self.currentnode = -1
		self.path = []
		self.direction = 1
		self.movespeed = 1.0
		self.oncomplete = 0			# What to do on path completion - 0 = continue, 1 = reverse
		self.pathcompleted = 0		# If the path's been completed
		
	def GetNextNode(self, n = 1):
		"""
		Return the next node in path.
		n = the number to check (i.e. you can check 1 node ahead, or 10 nodes ahead)
		
		Note that looping doesn't work well; 
		i.e. if you have a path of 3 nodes but you check 12 nodes ahead, it will give an error. Clamp n to as few values as possible.
		"""

		if self.currentnode + n < len(self.path):
			return (self.path[self.currentnode + n])
		elif len(self.path) > 0:
			return (self.path[(self.currentnode + n) - len(self.path)])
			
	def GetPrevNode(self, n = 1):
	
		"""
		Return the previous node in path.
		n = the number to check
		"""
		
		if self.currentnode - n >= 0:
			return (self.path[self.currentnode - n])
		else:
			return (self.path[len(self.path) - (self.currentnode + n)])
		
	def SetNextNode(self):
	
		self.SetNode(self.currentnode + 1)
			
	def SetPrevNode(self):
	
		self.SetNode(self.currentnode - 1)
	
	def SetNode(self, n):
	
		self.currentnode = n
		
		if self.currentnode >= len(self.path):
			self.currentnode = 0
		elif self.currentnode < 0:
			self.currentnode = len(self.path) - 1
			
	def MovePath(self, obj, speed, turntime = 5.0, linear = 0):
	
		"""
		Moves the specified object on its path.
		
		obj = Object to move on this path (self.path).
		speed = Speed to move the object; differs depending on whether the movement is in linear mode or not.
		turntime = How fast to turn toward the next node in the path.
		linear = Whether to move in Linear Velocity mode or not (Static mode). Linear velocity is only done for Dynamic objects.
		
		I believe the movement speed is in Blender Units per second, while in Static mode, the movement speed is in BU per game frame.
		
		"""
	
		self.pathcompleted = 0
	
		if self.oncomplete == 1:
			if (self.currentnode >= len(self.path) - 1 and self.direction == 1) or (self.currentnode <= 0 and self.direction == -1):
				self.direction = Reverse(self.direction, -1, 1)
				self.pathcompleted = 1
	
		if self.direction > 0:
			next = self.GetNextNode()
		else:
			next = self.GetPrevNode()
		
		
		
		if PosClose(obj.worldPosition, next[0]):
			self.SetNode(next[1])
	
		TrackTo(next[0], obj, time = turntime, dimensions = 'xy')
		
		if linear:
			obj.setLinearVelocity([0.0, speed, obj.getLinearVelocity()[2]], 1)
		else:
			obj.applyMovement([0.0, speed, 0.0], 1)
		
	def Calculate(self, pathpoints, sortvar = 0):
		"""
			Calculates the path from the current node on. Generally, you want to pass a list of objects to the pathpoints; you get more information back.
			If you pass a list of points in space, the path will consist of the index of the entry as well as the point. 
			For example, the path will look like
			
			[
			[Vector([x, y, z]), 0],
			[Vector([x, y, z]), 1],
			etc.
			]
			
			If you pass objects, you'll have a path that looks like
			
			[
			[Node0, Vector([x, y, z]), 0],
			[Node1, Vector([x, y, z]), 1],
			etc.
			]
			
			sortvar = whether or not to sort the list of points, and how to do so.
			If sortvar == 0, the path is not sorted; it is supplied in the same order that it is given (I think).
			If sortvar == 1, the path is sorted alphanumerically, via the node objects' names. For example, Node0, Node1, etc. If it's a list, it's sorted numerically.
			If sortvar == a string, the path is sorted using the key of the node objects' variable, whose name is equal to the string. For example, if you use a sortvar
			of 'nodeindex', then the nodes will be sorted in the list according to their 'nodeindex' value.
			
			The string sorting doesn't work with list values as path points."""
		
		if isinstance(sortvar, str):

			p = sorted(pathpoints, key = lambda object : object[sortvar])
		
		elif sortvar == 1:
		
			if isinstance(pathpoints[0], types.KX_GameObject):
				p = sorted(pathpoints, key = lambda object : object.name)
			else:
				p = sorted(pathpoints)
		
		else:
			
			p = pathpoints
		
		path = []
		
		for x in range(len(p)):
			
			if isinstance(p[x], types.KX_GameObject):
				path.insert(x, [p[x].worldPosition, x, p[x]])
			else:							# It's a list, so just go with that
				path.insert(x, [p[x], x])
		
		self.path = path
		
		return (path)	# Just in case you want to see the path yourself
	
class CNodeMap(object):

	"""
	A Node Map for path following. Unlike a simple Node Path, a Node Map is just that, a map of nodes.
	In a Node Map, each node can connect to any other node assuming there is an unobstructed shot to it.
	
	This allows for path-finding that should be very efficient as well as easy to use. In addition, NodeMaps are NOT
	bound to objects - i.e. a node map represents a whole node map area in-game, so multiple objects may use the same
	map.
	
	One might think that it would be nice to be able to attach nodes to positions. However, there's no way to know
	if altering the path would 'work out', so it's not advised.
	"""
	
	# ~~ Helper classes ~~

	class CNode(object):
	
		"""
		Internal helper node object. Use to find nodal neighbors.
		"""
	
		def __init__(self, nodemap, pos, ownerobj = None):
		
			self.links = []
			self.pos = pos									# World map position
			self.map = nodemap								# The NodeMap object you belong to
			self.parent = None								# Parent node for paths. Should work, I guess.
			self.ownerobj = ownerobj						# "parent" object; can be used for reference work.
			# Note that there's no correlation between the object and the node, it's just used to get an object
			# from a position, basically
				
		def Update(self, solidvar = '', raytest = 1, distrange = None):
		
			"""
			Updates all nodes in the nodemap.
			
			solidvar = variable to check for when checking if the path from node A to node B is collision free.
			raytest = if the test should be done.			
			"""
				
			self.links = []
				
			m = self.map
			obj = logic.getCurrentController().owner
				
			for node in m.nodes:
			
				if not node == self:
					
					if not raytest:
						diff = ListCom(ListAbs(ListSub(self.pos, node.pos)))
						if distrange == None or (diff >= distrange[0] and diff <= distrange[1]):
							if self not in node.links:
								node.links.append(self)
							if node not in self.links:
								self.links.append(node)
					else:
					
						test = obj.rayCast(node.pos, self.pos, 0, solidvar, 1, 1)
						
						#if g != [0, 0, 0]:		# Add a girth value for testing around the object
						
						#	if test[0] == None:
						#		test = obj.rayCast(ListSub(node.pos, g), ListSub(self.pos, g), 0, solidvar, 1, 1)
						#	if test[0] == None:
						#		test = obj.rayCast(ListAdd(node.pos, g), ListAdd(self.pos, g), 0, solidvar, 1, 1)
						
						#angok = 1
						
						# if anglimit != [0, 0, 0]:
						
							# md = math.degrees(mathutils.Vector(node.pos).angle(mathutils.Vector(self.pos)))
							
							# inc = anglimit[2]
							
							# diff = math.floor(md / inc) * inc
							# diff = md - diff
							
							# if diff < anglimit[0] or md > anglimit[1]:
								# angok = 0

						if test[0] == None:# and angok:
						
							diff = ListCom(ListAbs(ListSub(self.pos, node.pos)))
							
							if distrange == None or (diff >= distrange[0] and diff <= distrange[1]):
								if self not in node.links:
									node.links.append(self)
								if node not in self.links:
									self.links.append(node)

		def GetLinks(self):
			return self.links
					
	def __init__(self):
	
		self.nodes = []		# Nodes in your map
		self.nodenum = 0								# Number of nodes in the map; useless, kinda, but useful for some things.
		self.debugcolor = RandomList([0.2, 0.2, 0.2, 1.0], [0.5, 0.5, 0.5, 1.0])[:3]				# Unique debug color for each node map
		
	# ~~ Path Handling ~~
	
	def Update(self, solidvar = '', raytest = 1, distrange = None):
	
		"""
		Manually update all nodes' to find their neighbors; unnecessary since nodes 
		get their neighbors when added into the NodeMap.
		"""
	
		[node.Update(solidvar, raytest, distrange) for node in self.nodes]		
						
	def Calculate(self, start, end, solidvar = '', startray = 1, endray = 1, instant = 1):
	
		"""
		Construct a path from one point (start) to another (end).
		
		start and end should both be positions.
		solidvar can be any string; used to check for the closest nodes from point to point.
		
		Returns the path to get from the start point to the end point. Use with a Navigate function
		to move toward the end position.
		
		The returned list will be [path, 0], where path is a list of points on the path, and the last number
		indicating whether the path was successfully found or not. For whatever reason, it won't always
		find the path, though this might be more to do with my in-game setup than anything. :S
		"""
	
		map = self.nodes	# You can specify another map of nodes, if you want.
	
		#endnode = self.GetClosestNode(end, rayvar = solidvar)
		
		startnode = self.GetClosestNode(start, raytest = startray, rayvar = solidvar)
		endnode = self.GetClosestNode(end, raytest = endray, rayvar = solidvar)
			
		if endnode == None or startnode == None:
			
			return ([[], 0])
			
		else:
			
			startnode = startnode[0]
			endnode = endnode[0]
		
		pathfound = 0
		
		checkpossibles = [startnode]
		checked = []
		
		path = []	

		pathpass = 0

		while (pathfound == 0):
		
			#pathpass += 1
			#if pathpass > 100:	# Failsafe
			#	pathfound = None
				
			chklist = checkpossibles[:]
				
			if len(chklist) <= 0:		# Check list is empty
				break
				
			for node in chklist:
			
				checkpossibles.remove(node)
				
				if not node in checked:
				
					checked.append(node)

					if node == endnode and instant == 1:		# A path has been found! If instant is on, then take that path to the bank.
						
						pathfound = 1
						
						pathparent = endnode
						
						while pathparent != None:

							path.append(pathparent)
							pathparent = pathparent.parent
						
						#pathparent = finalnode		
						
						#while pathparent != None:
						
						#	print (pathparent.node.pos)
							
						#	path.append(pathparent)
						#	pathparent = pathparent.parent

						path = [p.pos for p in path]
						
						path.reverse()

						break
					
					for link in node.links:
						
						if not link in checked:

							if link.parent == None:
								link.parent = node
							checkpossibles.append(link)	# Register it as being checked in the next loop
	
		for node in self.nodes:
			node.parent = None	# Clear parent relationship after the path has been figured out

		if pathfound == 1:
			#self.path = path
			return [path, 1]
		else:
			return [path, 0]			# The path was invalid
		
	def Navigate(self, path, ind, movespd = 0.1, linear = 1, zaxis = 1, obj = None, freq = None):
	
		"""
		Moves the object obj on the path indictated from node to node. When a node has been reached, it moves
		on to the next node in the path, if there is one.	
		path = path list obtained from path calculation using the Calculate function.
		ind = path index; a user (object) variable that starts at 0 and increases or decreases as the object moves along the nodes in the path.
		linear = linear movement
		zaxis = whether or not to move on the Z-axis
		obj = what object to move; if left at None, it will use the script controller's object
		
		Returns a list consisting of the path index and if the path has been completed.
		"""
	
		cont = logic.getCurrentController()
	
		if obj == None:
			obj = cont.owner
		
		freq = cont.sensors[0].frequency + 1
		
		ret = [ind, 0]
		
		if ind >= 0 and ind <= len(path) - 1:
		
			if PosClose(obj.worldPosition, path[ind], 1, movespd * freq) == 1:
			
				if ind + 1 >= len(path):	# Path end
				
					ret[1] = 1
				
				else:
				
					ret[0] = ind + 1
			else:
			
				p = path[ind]
				op = obj.worldPosition
			
				if not zaxis:
					moveto = mathutils.Vector([p[0] - op[0], p[1] - op[1], 0.0])
				else:
					moveto = mathutils.Vector([p[0] - op[0], p[1] - op[1], p[2] - op[2]])
				
				if linear:
					moveto.magnitude = movespd * logic.getLogicTicRate()
					moveto.z += obj.getLinearVelocity()[2]
					obj.setLinearVelocity(moveto)
				else:
					moveto.magnitude = movespd * freq
					obj.applyMovement(list(moveto))
		
		return ret
		
	def NavigateMS(self, path, ind, movespd = 0.1, zaxis = 1, obj = None, freq = None):
	
		"""
		Returns the movement speed that the object obj should move on the path indictated from node to node. 
		When a node has been reached, it moves
		on to the next node in the path, if there is one.	
		path = path list obtained from path calculation using the Calculate function.
		ind = path index; a user (object) variable that starts at 0 and increases or decreases as the object moves along the nodes in the path.
		linear = linear movement
		zaxis = whether or not to move on the Z-axis
		obj = what object to move; if left at None, it will use the script controller's object
		
		Returns a list consisting of the path index and if the path has been completed.
		"""
	
		cont = logic.getCurrentController()
	
		if obj == None:
			obj = cont.owner
		
		freq = cont.sensors[0].frequency + 1
		
		ret = [ind, 0, None]
		
		moveto = mathutils.Vector()
		
		if ind >= 0 and ind <= len(path) - 1:

			if PosClose(obj.worldPosition, path[ind], 1, movespd * freq) == 1:
			
				if ind + 1 >= len(path):	# Path end
				
					ret[1] = 1
				
				else:
				
					ret[0] = ind + 1
			else:
			
				p = path[ind]
				op = obj.worldPosition
			
				if not zaxis:
					moveto = mathutils.Vector([p[0] - op[0], p[1] - op[1], 0.0])
				else:
					moveto = mathutils.Vector([p[0] - op[0], p[1] - op[1], p[2] - op[2]])
				
				moveto.magnitude = movespd * logic.getLogicTicRate()
				moveto.z += obj.getLinearVelocity()[2]
					
		ret[2] = moveto
					
		return ret
				
	# ~~ Node handling ~~
		
	def AddNode(self, pos, update = 0, raytest = 1, rayvar = 'nodesolid', ownerobj = None):
	
		"""
		Create a node at a position and add it to the node map. Also, find neighbors
		for the indicated node.
		
		pos = position of the node
		update = if it should find the neighbors of the node immediately or not; default = 0
		(Generally it would be faster to add all of the nodes and then update them, to save on re-raycasting objects...
		I think)
		raytest = if it should use rays to find its neighbors; default = 1
		rayvar = variable name to use when checking for neighbors; default = 'nodesolid'
		ownerobj = owner of the node; used just to tie the position of the node back to a object (so, for example,
		you can check if this is a 'patrol' node or a 'food' node, etc).
		"""
	
		n = self.CNode( self, list(pos), ownerobj)
		
		obj = logic.getCurrentController().owner
		
		self.nodes.append(n)
		
		self.nodenum += 1
		
		if update == 1:		# Find the neighbors of this node
			
			for fromnode in self.nodes:
			
				if fromnode != n:
				
					hit = obj.rayCast(fromnode.pos, n.pos, 0, rayvar, 1, 1)[0]
					
					if not raytest or (raytest and hit == None):
					
						if n not in fromnode.links:
							fromnode.links.append(n)
						if fromnode not in n.links:
							n.links.append(fromnode)

	def DeleteNode(self, node):
	
		"""
		Delete the node from the NodeMap, taking care of links to neighbors as well. Nodes can be gotten through the
		'GetNode' function
		"""
		
		self.nodenum -= 1
		
		for neighbor in node.links:			# Remove links to this node from other objects
			
			if node in neighbor.links:
			
				neighbor.links.remove(node)
			
		self.nodes.remove(node)				# Remove the node
	
 
		"""
		Returns the node at the position designated by pos. If there is no pos variable, it will return a random node.
		If there is no node at a specified position, the function will return None.
		"""
	
		if pos != None:
			ret = [n for n in self.nodes if n.pos == pos]
			if len(ret) > 0:
				return ret[0]
		else:
			if len(self.nodes) > 0:
				return (self.nodes[math.floor(logic.getRandomFloat() * len(self.nodes))])
		
		return None	# Node not found
		
	def GetClosestNode(self, pos = None, raytest = 1, rayvar = ''):
	
		"""
		Get the closest node to the specified position. 
		
		Returns None if there is no closest node
		that has a clear shot to the specified position.
		"""
		
		obj = logic.getCurrentController().owner
		
		if pos == None:
			pos = obj.worldPosition
		
		nodes = []

		[nodes.append([n, ListCom(ListAbs(ListSub(n.pos, pos)))]) for n in self.nodes]
					
		nodes.sort(key = lambda n:n[1])
		
		if len(nodes) > 0:
		
			if raytest:
				
				for n in nodes:
				
					if obj.rayCast(pos, n[0].pos, 0, rayvar, 1, 1)[0] == None:
						return n
						
					#print (obj.rayCast(pos, n[0].pos, 0, rayvar, 1, 1))
					
				return nodes[0]		# Found nodes, but no node has a clear shot to specified position, so just go for the closest one
				
			else:
			
				return nodes[0]	# Return the closest node to the specified position, regardless of whether it's a clear pathway or not
		
		else:
			
			return None			# Didn't find a node
	
	# ~~ Map Handling ~~	
	
	def MapCopy(self, othermap):
	
		"""
		Copies the other map's nodes to this one.
		
		Makes it so that:
		
		This NodeMap's node list = Other NodeMap's node list
		"""
	
		self.nodenum = othermap.nodenum
		self.nodes = copy(othermap.nodes)
	
	def MapDelete(self):
		"""
		Deletes all nodes in the NodeMap.
		"""
		self.nodenum = 0
		self.nodes = []
	
	# ~~ Debug Tools ~~
	
	def DebugDraw(self, uniquecolor = 1):
	
		"""
		Draws the node points and the connections between them. For debugging purposes.
		"""
	
		if len(self.nodes) > 0:
			
			for n in self.nodes:
					
				px = n.pos[0]
				py = n.pos[1]
				pz = n.pos[2]
				
				if uniquecolor:
					nc = self.debugcolor #[1, 1, 0]
					amt = 0.5
					lc = [self.debugcolor[0] + amt, self.debugcolor[1] + amt, self.debugcolor[2] + amt] #[0, 1, 0]
				else:
					nc = [1, 1, 0]
					lc = [0, 1, 0]	
			
				render.drawLine([px - 1, py, pz], [px, py - 1, pz], nc)		# Draw a diamond for each node
				render.drawLine([px, py - 1, pz], [px + 1, py, pz], nc)
				render.drawLine([px + 1, py, pz], [px, py + 1, pz], nc)
				render.drawLine([px, py + 1, pz], [px - 1, py, pz], nc)
				
				for l in n.links:											
					tp = l.pos
					render.drawLine(n.pos, tp, lc)							# Also draw a line to each node link
		
	def DebugDrawPath(self, path):
	
		"""
		Draws the paths between points for a specific path. For debugging purposes.
		"""
		
		if len(path) > 0:
		
			for n in range(len(path)):
			
				if n < len(path) - 1:
			
					render.drawLine(path[n], path[n + 1], [1, 1, 0 ])
	
class CAStarPath(object):

	"""
	A* pathfinding class. Useful for pathfinding around complex shapes.
	
	Calculate creates a path from the start point specified (if you choose one) to the goal.
	"""
	
	class CNode(object):
	
		"""
		Path node for path creation.
		"""
	
		def __init__(self, point, parentnode):
		
			self.pos = point
			self.parent = parentnode
	
	def __init__(self):
	
		self.path = []
		self.area = []		# List of all points checked
		self.pathindex = 0

	def Calculate(self, goalpos, startpos = None, prop = '', gs = 1.0, ray = 0):
	
		if startpos == None:
			startpos = logic.getCurrentController().owner.worldPosition
	
		obj = logic.getCurrentController().owner
		objlist = logic.getCurrentScene().objects
		
		solids = {}
		checked = {}
		
		self.path = [] # Blank the path.
		self.area = []
		
		def AddNode(np, node):
		
			if ray == 1:
			
				p = (np[0], np[1], np[2] + 1)
				tp = (np[0], np[1], np[2] - 1)
				
				sol = obj.rayCast(tp, p, 4, 'solid', 1, 1)
				
				#print (sol)
				
				if sol[0] != None:
				
					#pos = RoundVec(sol[0].worldPosition)[:]
					pos = np
					solids[str(pos)] = sol[0]
					#print ('solid found')
			
			nsp = str(np)							# Simply checks to see if the specified position is in the dict of solids or of those checked already
			
			if not nsp in solids and not nsp in checked:
				n = self.CNode(np, node)
				check[str(np)] = n
				checked[str(np)] = n
				self.area.append(np)
		
		if ray == 0:
		
			for o in objlist:									# Get the solid objects
			
				if prop == '' or prop in o:
				
					pos = RoundVec(o.worldPosition.copy())[:]

					solids[str(pos)] = o
			
		pathdone = 0
		pathpass = 0

		check = {str(startpos[:]):self.CNode(startpos[:], None)}	# Set the checking list to start from the starting point
		
		#goalpos = goal
		
		#goalpos = tuple(LockToGridList(goal.worldPosition.copy(), gs))				# Get the intended goal position
		
		while not pathdone:												# Loop through this process until a path has been found or until time has sufficiently passed
			
			pathpass += 1
			if pathpass > 100:											# Failsafe in case a path is never found
				pathdone = 1							
				
			nodes = check.copy()										# Done to prevent list changing while looping
				
			for x in nodes:
					
				node = nodes[x]
				pos = node.pos

				spos = str(pos)
				
				if pos == goalpos:
				
					#print ('FOUND THE GOAL!')							# You found the goal!
					
					self.path.append(pos)								# Set up the path by putting the goal at the end
					
					n = node
					
					while n.parent != None:								# Loop through the parents until you get to the beginning
						self.path.insert(0, n.pos)
						n = n.parent
					
					pathdone = 2
					
					break
				
				AddNode((pos[0], pos[1] + gs, pos[2]), node)					# Add a node in each direction
				AddNode((pos[0], pos[1] - gs, pos[2]), node)
				AddNode((pos[0] + gs, pos[1], pos[2]), node)
				AddNode((pos[0] - gs, pos[1], pos[2]), node)
										
				del check[spos]											# Delete this node from the list (not from existence; I think I'm relying on Python's
																		# garbage collection here) because it's already been checked		
		if pathdone == 1:
			return -1 			# Path's not found. :(
	
	def Navigate(self, movespd = 0.1, linear = 1, zaxis = 1, obj = None, oncomplete = 0):
		
		"""
		Moves the object obj on the path indictated from node to node. When a node has been reached, it moves
		on to the next node in the path, if there is one.	
		
		movespd = how fast to move
		linear = linear movement
		zaxis = whether or not to move on the Z-axis
		obj = what object to move; if left at None, it will use the script controller's object
		oncomplete = what to do on finishing the path; 0 = nothing, 1 = reverse, 2 = go to start, 3 = snap to start
		
		Returns 1 if the path is complete, and 0 otherwise.
		"""
	
		if obj == None:
			obj = logic.getCurrentController().owner
		
		path = self.path
				
		if PosClose(obj.worldPosition, path[self.pathindex], 1, 0.1) == 1:
		
			if self.pathindex + 1 >= len(path):	# Path end
			
				#if oncomplete == 0:		# Stop
			
				#	return 1
				
				if oncomplete == 1:			# Reverse
				
					self.path.reverse()
					self.pathindex = 0
				
				elif oncomplete == 2:
				
					self.pathindex = 0
				
				elif oncomplete == 3:		# Snap to start
				
					obj.worldPosition = self.path[0]
					self.pathindex = 0
				
				return 1
			
			else:
			
				self.pathindex += 1
		else:
		
			p = path[self.pathindex]
			op = obj.worldPosition
		
			if not zaxis:
				moveto = mathutils.Vector([p[0] - op[0], p[1] - op[1], 0.0])
			else:
				moveto = mathutils.Vector([p[0] - op[0], p[1] - op[1], p[2] - op[2]])
			
			if linear:
				moveto.magnitude = movespd * logic.getLogicTicRate()
				moveto.z = obj.getLinearVelocity()[2]
				obj.setLinearVelocity(moveto)
			else:
				moveto.magnitude = movespd
				obj.applyMovement(list(moveto))
		
		return 0
	
	def DebugDrawNode(self, pos, color):
	
		render.drawLine([pos[0], pos[1], pos[2]], [pos[0], pos[1], pos[2] + 1], color)
		
	def DebugDraw(self):
	
		for p in self.area:
		
			if p in self.path:
			
				self.DebugDrawNode(p, [green[0], green[1], green[2]])
				
			else:
				
				self.DebugDrawNode(p, [orange[0], orange[1], orange[2]])
	
class CGRange(object):

	"""
	
	Gradual Range - Returns a range of numbers, like the range() function, but does so in such a way that you can step throug hit gradually.
	For example, say you wanted to loop through 1000 game objects. Doing this in a for loop normally would cause the BGE to lock
	up while it looks at each object. However, by using a GRange (Gradual Range), you can step through the range of numbers a little bit at a time,
	like 0 - 49, 50-99, 100-149, 150-199, etc.
	
	The stopped index stays with the object, so if you store it in a game object, you can use it again and again and spread out the work across
	several game frames to keep the game running.
	
	__init__() = called when the object is created (e.g. obj['gr'] = BGHelper.CGRange(stop, maximum)
	
	stop = value to stop at
	maximum = maximum number to iterate through each time you call for the next set of numbers
	start = number to start counting at; usually 0
	step = amount to use to step through the list; usually 1
	done = what to do on getting to the end of the list. 0 (default) = return None, 1 = reset the list from the beginning, and 2 = raise a StopIteration error.
	
	__next__() = used to step through the range. Returns the next set of numbers. Assuming cr is a CGRange object, you can use several methods to get the next set.
	
	Next(cr)
	cr.Next()
	cr.__next__()
	
	Any of those methods will work, but cr.__next__() is frowned upon, and Next(cr) is pretty accepted usage; however, cr.Next() does match with the next function:
	
	Reset() = used to reset the index value to the original starting position, thereby making the object repeat the iteration process. For example,
	
	cr.Next() # [0, 1, 2]
	
	Next(cr) # [3, 4, 5]
	
	Next(cr) # [6, 7] 	< Last list
	
	Next(cr) # Returns None so that you know :)
	
	cr.Reset() # Resets the range returned
	
	cr.Next() # [0, 1, 2] < Starts over
	
	"""

	def __init__(self, stop, maximum, start = 0, step = 1, done = 0):
	
		self.max = maximum	# Maximum number to loop through, e.g. from 0 - 99 on a 0 - 10000 loop; after that, it's from 100 - 199 loop
		self.stop = stop
		self.start = start
		self.index = start
		self.step = step
		self.whendone = done	# If the object should raise StopIteration error when finished (2), reset (1), or just return None (0)
		pass
		
	def __iter__(self):
	
		return self
	
	def __next__(self):

		end = self.index + self.max
		
		if end > self.stop:
			end = self.stop
		
		l = []
		
		if self.index < end:
			
			for i in range(self.index, end, self.step):
			
				l.append(i)
				
			self.index = i + 1
			
			return l
		
		else:
		
			if self.whendone == 0:
				return None
			elif self.whendone == 1:
				self.Reset()
				return(self.Next())
			else:
				raise StopIteration
		
	def Next(self):		# Just exposing the Next function to the object
		return self.__next__()
			
	def Reset(self):
		self.index = self.start
		
	def Wipe(self, stop, max, start = 0, step = 1, done = 0):
		"""
		Wipes the current Gradual Range List. For example,
		
		cg = CGRange(10, 2)
		cg.Next() # [0, 1]
		cg.Next() # [2, 3]
		
		cg.Wipe(50, 3) # Wipes the current range out of the function, effectively resetting it; similar to cg = CGRange(50, 3)
		
		cg.Next() # [0, 1, 2]
		cg.Next() # [3, 4, 5]
		"""
		self.__init__(stop, max, start, step, done)

### INPUT CLASSES ###
		
class CJoyState(object):

	"""
		Object for handling joystick input; gives you an object that you can pull button, axis, and hat states from.
		Also holds the previous states of these input devices, allowing you to see if a device has been just pressed,
		released, or held.
		
		The button and hat input check functions below should be called after polling, at least once. So,
		the way you use it is this way:
		
		#----- EXAMPLE -----
		
		joysensor = cont.sensors['Joystick']	# Get the joystick sensor (there's no global variable for this yet)
		obj['joystate'] = CJoyState(joysensor) 	# Create a CJoyState object (only needs to be done once per joystick)
		obj['joystate'].Poll()					# Poll the joystick sensor for joystick values (only needs to be done once per frame to get all input)
		
		buttonpressed = obj['joystate'].ButtonDown(1) # Check to see if a button, in this case the second one, has been pressed
		
		#----- EXAMPLE END -----
		
		There are different parts to the CJoyState object. You have three different portions:
		
		'axis' - Example: [0, 1000, -1000, 1320]
		Axis states; some joysticks have an 'Analog' mode in which the analog sticks drive these variables. Others don't.	
		
		'hat' - [0] # A list; seems to be just a single number for a USB PS2 controller (and most joysticks, I'd assume) when in Analog mode,
		as the D-Pad then changes this hat variable rather than the 'axis' variable.
		
		'button': [0, 9, 6] # A list consisting of each pressed button. There's no built-in functionality for checking to see if a button
		was just pressed or released, but there is one in the class (either the function, or you can check directly with the
		joystateobject.prevbutton (or prevaxis and prevhat) variables.
		
		From my tests using a Dual Shock PS2 controller (with analog sticks) connected to a PS2 - USB converter, 
		it would look like this is the case:
		
		
		1. With -Analog mode- on, the Analog sticks drive the axis variable, in an analog manner (further you hold, the higher the numbers go). Max
		is 32768. D-Pad is assigned to the hat variable, with a different number for each direction (for whatever reason). Thumbstick button
		presses register.
		
		
		2. With -Analog mode- off, the D-pad can be used to drive the axis variable in a digital manner. However, the left analog stick
		still drives the variable as well, but in a digital manner (either full on in any direction, or not). The right analog stick no longer
		responds. Thumbstick button presses do not register.
		
		
		It looks like the easiest way to design a game to use joysticks would be to use the 'axis' variable for movement and the button list for
		buttons. With analog mode on, people can use the sticks if they want, and with it off, they can use the D-Pad. If you're using this, you
		probably want to connect it to a joystick sensor set to All Events, with the index of the joystick you want to check for.
	"""

	def __init__(self, joysensor):
	
		self.sensor = joysensor

		self.connected = joysensor.connected

		self.index = joysensor.index					# Joystick index value; can be used to differentiate between joysticks
		self.numAxis = joysensor.numAxis
		self.numHat = joysensor.numHats
		self.numButton = joysensor.numButtons
		
		self.axismax = 32768							# Maximum value the axis can move; usually, 32768 is the max
		self.deadzone = 2000							# A basic deadzone that you can use for testing axis movements
	
		self.axis = self.sensor.axisValues				# The axis (analog values in analog mode, digital values in digital mode)
		self.hat = self.sensor.hatValues				# The hat values for the joystick
		self.button = self.sensor.getButtonActiveList()	# The curently active buttons for the joystick.
		
		self.prevaxis = None							# Previous axis, button, and hat values for the joystick (from one Poll() call ago).
		self.prevhat = None
		self.prevbutton = None	
	
	def Poll(self):
	
		self.connected = self.sensor.connected
	
		self.index = self.sensor.index					# Joystick index value; can be used to differentiate between joysticks
		self.numAxis = self.sensor.numAxis
		self.numHat = self.sensor.numHats
		self.numButton = self.sensor.numButtons
	
		self.prevaxis = self.axis[:]
		self.prevhat = self.hat[:]
		self.prevbutton = self.button[:]
	
		self.axis = self.sensor.axisValues
		self.hat = self.sensor.hatValues
		self.button = self.sensor.getButtonActiveList()	
	
	def AssignSensor(self, sensor):
		self.sensor = sensor
		
	def ButtonDown(self, button):
		return button in self.button
	def ButtonHeld(self, button):
		return (button in self.button and button in self.prevbutton)
	def ButtonReleased(self, button):
		return (button not in self.button and button in self.prevbutton)
	def ButtonPressed(self, button):
		return (button in self.button and not button in self.prevbutton)
	
	def HatDown(self, hat):
		"""
		Tests the joystick's hat sensors to see if they're pressed down. 'hat' defines which value
		to check for. Different joysticks have different hat setups, but for a USB PS2 controller,
		each individual D-pad press in analog mode yields a different hat value.
		"""
		return hat in self.hat
	def HatHeld(self, hat):
		return (hat in self.hat and hat in self.prevhat)
	def HatReleased(self, hat):
		return (not hat in self.hat and hat in self.prevhat)
	def HatPressed(self, hat):
		return (hat in self.hat and not hat in self.prevhat)
		
	def AxisDown(self, axis, dir, threshold = 32768/2.0):
	
		"""
		Checks the axes (analog sticks or D-Pad) to see if they cross a threshold in a certain direction.
		The threshold's separate because it seemed easier this way to find out if a stick was pressed in
		a certain direction.
		Valid directions are 1 and -1; usually, each analog stick has two axes (one for up and down, and one for left and right).
		"""
	
		a = self.axis[axis]
		if dir > 0:
			return a > dir * threshold
		elif dir < 0:
			return a < dir * threshold
		else:
			return 0
			print ("No such direction as 0")
	def AxisReleased(self, axis, dir, threshold = 32768/2.0):
		a = self.axis[axis]
		pa = self.prevaxis[axis]
		if dir > 0:
			return a <= dir * threshold and pa > dir * threshold
		elif dir < 0:
			return a >= dir * threshold and pa < dir * threshold
		else:
			return 0
			print ("No such direction as 0")
	def AxisPressed(self, axis, dir, threshold = 32768/2.0):
		a = self.axis[axis]
		pa = self.prevaxis[axis]
		if dir > 0:
			return a > dir * threshold and pa <= dir * threshold
		elif dir < 0:
			return a < dir * threshold and pa >= dir * threshold
		else:
			return 0
			print ("No such direction as 0")
	def AxisHeld(self, axis, dir, threshold = 32768/2.0):
		a = self.axis[axis]
		pa = self.prevaxis[axis]
		if dir > 0:
			return a > dir * threshold and pa > dir * threshold
		elif dir < 0:
			return a < dir * threshold and pa < dir * threshold
		else:
			return 0
			print ("No such direction as 0")
	
class CJoyProfile(object):

	"""
	Class that stores profile input setups for the different joysticks. I only have a couple, but I'll add them.
	
	You don't have to make a CJoyProfile object to use it - it's just a container. Use it as you would use a static class in C++ -
	refer to the class's attributes, rather than making an object to do so.
	
	For example:
	
	ps2prof = BGHelper.CJoyProfile.PS2USB
	
	test = obj['joystate'].ButtonDown(2) 				# Just a number
	test = obj['joystate'].ButtonDown(ps2prof['Cross']) # The X button for a PS2 controller
	
	It might seem a little messy to have all values next to each other, but it's generally
	easier than having an extra dictionary to separate them.
	
	"""
	
	"""
	The profile for a PS2-USB Controller Converter, which allows you to use standard PS2 controllers on your computer. 
	"""
	
	PS2USB = {		
	
		'Triangle':0,				# BUTTONS
		'Circle':1,
		'Cross':2,
		'Square':3,
		'L2':4,
		'R2':5,
		'L1':6,
		'R1':7,
		'Select':8,
		'Start':9,
		'L3':10,
		'R3':11,

		'Up':1,						# Hat values
		'Up-Right':3,
		'Right':2,
		'Right-Down':6,
		'Down':4,
		'Left-Down':12,
		'Left':8,
		'Left-Up':9,
		'None':0,

		'LHorizontal':0,			# Analog stick axes
		'LVertical':1,
		'RVertical':2,
		'RHorizontal':3,

		'AxisLeft':-1,				# Analog stick directions (for use with AxisDown and other Axis check functions)
		'AxisRight':1,				# Both sticks work the same way, so you can use any of these for either stick.
		'AxisUp':-1,
		'AxisDown':1,	
		}
	LOGITECHCHILLSTREAM = {
		
		'Triangle':3,				# BUTTONS
		'Circle':2,
		'Cross':1,									
		'Square':0,
		
		'L2':6,
		'R2':7,
		'L1':4,
		'R1':5,
		'Select':8,
		'Start':9,
		'L3':10,
		'R3':11,
		
		'Up':1,						# Hat values
		'Up-Right':3,
		'Right':2,
		'Right-Down':6,
		'Down':4,
		'Left-Down':12,
		'Left':8,
		'Left-Up':9,
		'None':0,
		
		'LHorizontal':0,			# Analog stick axes
		'LVertical':1,
		'RHorizontal':2,
		'RVertical':3,
		
		'AxisLeft':-1,				# Analog stick directions (for use with AxisDown and other Axis check functions)
		'AxisRight':1,				# Both sticks work the same way, so you can use any of these for either stick.
		'AxisUp':-1,
		'AxisDown':1,	
		
		}

#class CCombo(object):
	
	#def __init__(self, inputs):
		
		#self.inputs = inputs	# Possible inputs
		#self.combos = {}
		
	#def AddCombo(self, combo, threshold, comboname = 'A Combo'):
		
		#self.combos['comboname'] = {'combo':combo, 'timer':0.0, 'pasttimer':0.0, 'threshold':threshold, 'comboindex':0}
		
	#def Check(self, comboname, input):
		
		#combo = self.combos[comboname]
		
		#in = self.inputs[input]
		
		#combo['pasttimer'] = combo['timer']
		#combo['timer'] = time.clock()
		#diff = combo['timer'] - combo['pasttimer']
		
		#if input == combo['combo']['comboindex'] and diff < combo['threshold']:
			#combo['comboindex'] += 1
		
		#if combo['comboindex'] >= len(combo['combo']):
			#finished = 1
		#else:
			#finished = 0
			
		#return ({'comboover':finished, 'comboindex':combo['comboindex']})
		
class CTimer(object):
	
	"""
	Just a nice container for checking if a variable is set to a value within a time limit; shouldn't need
	to be called every frame, but just running the Check function will return the value that you want.
	
	Add function -
	
	timername = unique identifier for the timer that you want to add. 
	Note that this timer is 'updated' when you run the Check function, so it's just measuring 
	the amount of time between the two points.
	
	variable = variable that you want to check
	targetvalue = value that you want to check against (variable must equal this value)
	thresh = maximum amount of time that can elapse between checks for it to still be considered 'alright';
	
	An example of this would be a CTimer to check to see if you do a certain 'tap', like if you wanted to check
	to see if you pressed Right + X, with a tiny amount of buffer so that you don't have to press them at the EXACT
	same time.
	"""
	
	def __init__(self):
		
		self.target = {} # List of target timers to check
				
	def Check(self, timername, variable, targetvalue, thresh):
		
		if not timername in self.target:
			self.target[timername] = {'prevcheck':time.clock(), 'check':time.clock(), 'lastposcheck':-1}
		
		target = self.target[timername]
		
		target['prevcheck'] = target['check']
		target['check'] = time.clock()

		if (variable == targetvalue):
			target['lastposcheck'] = time.clock()
			
		within = target['check'] - target['lastposcheck'] < thresh
			
		print (within)
			
		return within
		
		#	
		#print (target['variable'], target['targetvalue'])
		#print (within)
		
	def Remove(self, timername):
		self.target.remove(timername)

#############
# FUNCTIONS #
#############

### INPUT FUNCTIONS ###

def KeyDown(keycode):

	"""
	Tests to see if a key is being held down on the keyboard.
	You don't need to define a keydict - it can use the one from the logic module.
	"""
	keydict = logic.keyboard.active_events
	if keycode in keydict:
		return keydict[keycode] == logic.KX_INPUT_JUST_ACTIVATED or keydict[keycode] == logic.KX_INPUT_ACTIVE
	else:
		return False

def KeyPressed(keycode):

	"""
	Tests to see if a key is being held down on the keyboard.
	You don't need to define a keydict - it can use the one from the logic module.
	"""
	keydict = logic.keyboard.active_events
	if keycode in keydict:
		return keydict[keycode] == logic.KX_INPUT_JUST_ACTIVATED
	else:
		return False

def KeyReleased(keycode):

	"""
	Tests to see if a key is being held down on the keyboard.
	You don't need to define a keydict - it can use the one from the logic module.
	"""
	keydict = logic.keyboard.active_events
	if keycode in keydict:
		return keydict[keycode] == logic.KX_INPUT_JUST_RELEASED
	else:
		return False

def KeyHeld(keycode):
	
	"""
	Tests to see if a key is being held down on the keyboard.
	You don't need to define a keydict - it can use the one from the logic module.
	"""
	keydict = logic.keyboard.active_events
	if keycode in keydict:
		return keydict[keycode] == logic.KX_INPUT_ACTIVE
	else:
		return False
	
def MouseDown(mousecode):
	
	mousedict = logic.mouse.active_events
	
	if mousecode in mousedict:
		
		return mousedict[mousecode] == logic.KX_INPUT_JUST_ACTIVATED or mousedict[mousecode] == logic.KX_INPUT_ACTIVE
	
	else:
		
		return False
	
def MouseHeld(mousecode):
	
	mousedict = logic.mouse.active_events
	
	if mousecode in mousedict:
		
		return mousedict[mousecode] == logic.KX_INPUT_ACTIVE
	
	else:
		
		return False
	
def MousePressed(mousecode):
	
	mousedict = logic.mouse.active_events
	
	if mousecode in mousedict:
		
		return mousedict[mousecode] == logic.KX_INPUT_JUST_ACTIVATED
	
	else:
		
		return False
	
def MouseReleased(keycode):
	
	mousedict = logic.mouse.active_events
	
	if mousecode in mousedict:
		
		return mousedict[mousecode] == logic.KX_INPUT_JUST_RELEASED
	
	else:
		
		return False
	
#### BGUI PYTHON FUNCTIONS ####

### Functions for BGUI object placement; code from someone on Moguri's blog

def PixelX(xpos):
	return float(xpos / render.getWindowWidth())
def PixelY(ypos):
	return float(ypos / render.getWindowHeight())
def PixelW(width):
	return float((width - 1) / render.getWindowWidth())
def PixelH(height):
	return float((height - 1) / render.getWindowHeight())

#### MATH / PYTHON FUNCTIONS ####

def Reverse(value, first, second):
	"""
	
	Toggles the value between two possibile values, so that if it's first, it's second and vice versa. Example:
	
	val = 1
	Reverse(val, 1, -1) = -1
	Reverse(val, 1, -1) again would = 1 this time, as val is -1, and so has been reversed.
	
	Really, it could be thought of as a toggle between values. It's a little late to change the name now, though. :p
	
	"""

	if value == first:
		return second
	elif value == second:
		return first
	else:
		return value
def LockToGridList(l, grid):

	"""
	Locks each element of the list to the grid indicated. To see how this works, refer
	to LockToGrid.
	The list can be any size.
	"""
	
	locked = [LockToGrid(l[x], grid) for x in range(len(l))]
	
	return (locked)
def ListSub(lone, ltwo):
	"""
	Subtracts two lists and returns the resulting list. Lists can be any size. Lists also don't need 
	to be the same size, but they should be, or else the returned list won't be complete. 
	
	List 1 (lone) at least needs to be less than or equal to the size of list 2 (ltwo); if not, an error will be thrown (I think).
	
	lone = a list
	ltwo = a list
	"""

	return ([lone[x] - ltwo[x] for x in range(len(lone))])
def ListAdd(lone, ltwo):

	"""
	Adds two lists together. See ListSub.
	"""

	return ([lone[x] + ltwo[x] for x in range(len(lone))])
def ListPlace(lone, index, value):

	"""
	Places a value in a slot in a list.
	
	Here's how it works.
	
	list = [10, 5, 9, 10]
	
	list[1] += 10 # You want 15 from list[1], but it doesn't work
	
	list = ListPlace(list, 1, list[1] + 10) # Works; Now, list = [10, 15, 9, 10]
	
	And returns the list back.
	
	"""

	ret = []

	for x in range(len(lone)):
	
		if x == index:
			ret.insert(x, value)
		else:
			ret.insert(x, lone[x])
			
	return ret
def ListCom(lone):

	"""
	Combines all elements in a 1 DIMENSIONAL list.
	"""

	a = 0
	
	for x in range(len(lone)):
		a += lone[x]
		
	return a
def ListAbs(lone):

	"""
	Absolutes the values in a list. See ListSub.
	"""

	return ([abs(lone[x]) for x in range(len(lone))])
	
# def ListExecute(lone, ltwo, function):

	# return ([lone[x].function(ltwo[x]) for x in range(len(lone))])
		
def FindGOInList(property, value, list):
	
	"""
	
		Return a Game Object and its index from a list given that it has a property, set to a value 
		that you're looking for, IF POSSIBLE. Otherwise, it will return None. Just a faster method than try: catch.
	
	"""
	
	found = [None, None]
	
	try:
		for l in range(len(list)):
			if list[l][property] == value:
				found = [list[l],l]
	except IndexError:
		return ([None, None])
		
	return (found)
	
def LockToGrid(value, grid):
	"""
	Locks value to the grid size indicated by the 'grid' property.
	
	For example,
	
	value = 0.45, grid = 0.5, returned would be 0.5.
	value = 1.74, grid = 0.5, returned would be 1.5.
	value = 1.75, grid = 0.5, returned would be 2.0.
	"""
	return round(value / grid) * grid
	
def KeepRadian(value):
	"""
	Loops the value around to be in the range of radians, ranging from -pi to pi. If the value exceeds pi, then it goes back to -pi.
	"""
	
	while (value > math.pi or value < -math.pi):
	
		if value > math.pi:
			value -= twopi
		elif value < -math.pi:
			value += twopi
	
	return value

def InRange(value, min, max, inclusive = 1):
	"""
	Function that returns whether 'value' is within the range of 'min' to 'max'.
	Inclusive = 1 or 0 - defines whether to evaluate as true when 'value' is equal to 'min' or 'max'. Default = 1.
	value, min, max = number
	"""
	if inclusive:
		if value >= min and value <= max:
			return 1
		else:
			return 0
	else:
		if value > min and value < max:
			return 1
		else:
			return 0	

def OutRange(value, min, max):
	"""
	Returns true when 'value' is out of the range of 'min' to 'max'.
	value, min, max = number
	"""
	if value < min or value > max:
		return 1
	else:
		return 0

def VectorRound(vector, roundval = 1):
	"""
	Returns the input 'vector' with its values rounded off. 
	roundval = how far to round off (higher number = higher precision)
	"""
	v = vector.copy()
	v.x = round(v.x, roundval)
	v.y = round(v.y, roundval)
	v.z = round(v.z, roundval)
	return v

def Lerp(a, b, scalar):
	"""Lerp - Linearly interpolates between 'a'
	when 'scalar' is 0 and 'b' when 'scalar' is 1.
	a = number or Vector
	b = number or Vector
	scaler = number between 0 and 1
	"""
	return (a + scalar * (b - a))

def ListLerp(a, b, scalar):
	
	returnlist = []
	
	for item in range(len(a)):
		returnlist.append(Lerp(a[item], b[item], scalar))
	
	return returnlist

def XLerp(a, b, scalar, multiple = 2):
	"""XLerp - Does what Lerp does, but uses multiples to allow for the ability
	to clamp values (i.e. have the function return 1 when the scalar is between 0.5 and 1)"""
	s = scalar
	s *= multiple
	if s > 1:
		s = 1
	return (a + s * (b - a))

def Clamp(value, min, max = None):
	"""
	Clamp: Clamps the specified 'value' between the maximum and minimum values.
	Returns 'max' when 'value' is greater than 'max', 'min' when 'value' is less than 'min',
	and 'value' itself when neither is true.
	
	V1.2 (?) Update added the feature to only have to specify min if you want max to equal -min. What I mean is that:
	
	Clamp(variable, -10, 10)
	
	can be shortened to 
	
	Clamp(variable, -10)
	
	and have the same effect. In the above example, it is NOT the same as 
	
	Clamp(variable, 10)
	
	"""
	if max != None:
		if value > max:
			return max
		elif value < min:
			return min
		else:
			return value
	else:
		if value > -min:
			return -min
		elif value < min:
			return min
		else:
			return value

def Sign(value):					
	"""
	Returns the sign of the inputted 'value'; i.e. 5 = 1, -9.1 = -1, 0 = 0
	"""
	if value > 0:
		return 1
	elif value < 0:
		return -1
	else:
		return 0

def RandomList(base = [0.0, 0.0, 0.0, 0.0], top = [1.0, 1.0, 1.0, 1.0], lock = [-1, -1, -1, -1]):
	
	"""
	Returns a random 4-component sequence. Good for colors.
	
	All arguments are lists; this is just for ease of use. Note that you can use a number for the base list.

	base = the minimum amount that must be in the returned vector.
	top = the maximum amount that must be in the returned vector.
	lock = whether to lock the first component to a value or not. 
	If any index >= 0, the channel is locked to that value; otherwise, it will be random. For example,
	
	lock = [-1, -1, -1, 1.0]
	
	would lock the returned random list to three random numbers, but a value of 1.0 in the last index.
	
	"""
	
	if isinstance(base, float) or isinstance(base, int): # If you use a single value, it will be turned into a list.
		base = [base, base, base, base]
	
	if isinstance(top, float) or isinstance(top, int): # If you use a single value, it will be turned into a list.
		base = [top, top, top, top]
		
	#d = top - base
	
	d = ListSub(top, base)
	
	#print (d)
		
	r = [base[0] + (random.random() * d[0]) , base[1] + (random.random() * d[1]) , 
		base[2] + (random.random() * d[2]) , base[3] + (random.random() * d[3]) ]

	if lock[0] >= 0:
		r[0] = lock[0]
	if lock[1] >= 0:
		r[1] = lock[1]
	if lock[2] >= 0:
		r[2] = lock[2]
	if lock[3] >= 0:
		r[3] = lock[3]
		
	return r

def RandomNumber(base = 0.0, top = 1.0):
	
	"""
	Returns a random number between base and top.
	
	baseline = the minimum amount that must be in the returned number.
	top = the maximum amount that must be in the returned number.
	"""

	d = float(top) - float(base)
	
	r = float(base) + (random.random() * d)
		
	return r

def GetAngle(obj, destobj, xy = 0):
	"""
	Gets the angle from one object (Game object or list point) to another.
	
	obj = First point or game object.
	destobj = Second point or game object.
	xy = Whether or not to return the angle on the X and Y axes (0), the Y and Z axes (1), or the Z and X (2) axes.
	Defaults to X and Y axes. Return value is in radians.
	"""

	if isinstance(obj, mathutils.Vector):					# If it's a vector, pos = the vector
		pos = obj
	elif isinstance(obj, list) or isinstance(obj, tuple): 	# If it's a tuple or list, make it a vector
		pos = mathutils.Vector(obj)
	else:													# If it's a game object, use its world position
		pos = obj.worldPosition
	
	if isinstance(destobj, mathutils.Vector):
		dpos = destobj
	elif isinstance(destobj, list) or isinstance(destobj, tuple):
		dpos = mathutils.Vector(destobj)
	else:
		dpos = destobj.worldPosition
		
	if xy == 0:
		return (math.atan2(pos.y - dpos.y, pos.x - dpos.x))
	elif xy == 1:
		return (math.atan2(pos.z - dpos.z, pos.y - dpos.y))
	else:
		return (math.atan2(pos.x - dpos.x, pos.z - dpos.z))

### NOISE FUNCTIONS ###

def Noise(size = [1, 1, 1], seed = 0, base = 0.0, top = 100.0):
	
	grid = []
	
	random.seed(seed)
	
	for z in range(size[2]): 			# Create the array
		grid.append([])
		for y in range(size[1]):
			grid[z].append([])
			for x in range(size[0]):
				grid[z][y].append(base)
	
	for z in range(size[2]): 			# Populate the array
		for y in range(size[1]):
			for x in range(size[0]):
				
				grid[z][y][x] = random.Random()
				
	return grid
		
#### GENERAL FUNCTIONS ###
	
def AddDict(dictionary, var, value = 0):
	"""
	Adds the value specified to the dictionary key 'variablename' in the dictionary specified.
	"""
	
	if var in dictionary:
		dictionary[var] += value
	else:
		dictionary[var] = value
	
def InitVar(variablename, value = 0, object = None):
	"""
	Initializes the variable indicated by 'variablename' in 'object' to 'value' 
	IF it doesn't already exist in the 'object'.
	"""
	
	if object == None:
		obj = logic.getCurrentController().owner
	else:
		obj = object
	
	if not variablename in obj:
		obj[variablename] = value

def FindChild(obj, childname, exact = 0):
	"""
	Finds the child in the specified object's children array.
	obj = object whose children you wish to search through
	childname = Name of the child object.
	
	With 'exact' off (default), FindChild will simply look for the child whose name has 'childname' in it. So, if childname == 'spr', 
	with 'exact' off, it could return either ComputerSprite or Lightsprout, as both names have 'spr' in them
	
	exact = Whether or not to look for EXACTLY the child's name or not
	"""
	for child in obj.children:
		if exact:
			if childname == child.name:
				return child
		else:
			if childname in child.name.lower():	
				return child
	return None		# childname wasn't found in the list of obj's children, so return None (no children)

def GetFPS(safe = 1):						
	"""
	Returns the FPS of the game; note that because Blender's function may be off, with 'safe' on, it may return
	logic's tic rate instead of the averageFrameRate (sometimes it returns extremely large values);
	To enable this safeguard, set 'safe' to 1
	"""
	if safe:
		if logic.getAverageFrameRate() > 0.0:	# Sometimes the framerate varies wildly or isn't larger than zero
			return logic.getAverageFrameRate()
		else:									# In this case, use the logic tic rate
			return logic.getLogicTicRate()
	else:
		return logic.getAverageFrameRate()		# Just get the average FPS

def Evaluate(var):           
	"""
	Check to see if an object property is a string can be converted to a normal variable.
	If so, then it evaluates the string and returns it; otherwise, just the value is returned.
	"""
	
	if isinstance(var, str):
		return eval(var)
	else:
		return value	
	
def GetThisFile():

	os.path.join(sys.path[0], sys.argv[0])

### POSITION FUNCTIONS ###

def Close(x, y, tol = 0.1):		
	"""
	Tests to see if the two numbers 'x' and 'y' are within a certain tolerance
	x = number
	y = number
	tol = maximum tolerance between the two
	"""
	if abs(x - y) <= tol:
		return 1
	else:
		return 0

def PosClose(posone, postwo, elevation = 1, tol = 1.0):
	"""
	Tests to see if two positions are close together, within a certain tolerance (on all axes);
	elevation indicates whether the check should work for all three axes, or just X and Y
	"""
	
	if not Close(posone[0], postwo[0], tol):
		return 0
	elif not Close(posone[1], postwo[1], tol):
		return 0
	if elevation > 0 and not Close(posone[2], postwo[2], tol):       # Only evaluate the third dimension if indicated to do so
		return 0                            
	
	return 1	
	
### VECTOR FUNCTIONS ###
		
def RoundVec(vec, amt = 1):

	"""
	Rounds off a Vector.
	"""

	return (mathutils.Vector([round(vec.x, amt), round(vec.y, amt), round(vec.z, amt)]))
	
def VectorDown(position = None, range = 1):
	"""
	Returns a vector straight down (-Z). You use this with a rayCast 
	function to test for directly to the right of an object.
	
	For example, obj.rayCast( VectorDown(position), position, etc...)
	
	position = object's position to create the 'down' vector from.	
	range = optional argument indicating how far the vector should go stretch (by default, it's 100 Blender Units)
	"""
	
	if position == None:
		position = logic.getCurrentController().owner.position
	p = position.copy()
	p.z -= range
	return p

def VectorRight(position = None, range = 1):
	"""
	Returns a vector straight right (+X). You use this with a rayCast 
	function to test for directly to the right of an object.
	
	For example, obj.rayCast( VectorRight(position), position, etc...)
	
	position = object's position to create the 'down' vector from.
	range = optional argument indicating how far the vector should go stretch (by default, it's 100 Blender Units)
	"""
	if position == None:
		position = logic.getCurrentController().owner.position
	p = position.copy()
	p.x += range
	return p

def VectorLeft(position = None, range = 1):
	"""
	Returns a vector straight left (-X). You use this with a rayCast 
	function to test for directly to the right of an object.
	
	For example, obj.rayCast( VectorLeft(position), position, etc...)
	
	position = object's position to create the 'left' vector from.
	range = optional argument indicating how far the vector should go stretch (by default, it's 100 Blender Units)
	"""
	if position == None:
		position = logic.getCurrentController().owner.position
	p = position.copy()
	p.x -= range
	return p

def VectorUp(position = None, range = 1):
	"""
	Returns a vector straight up (+Z). You use this with a rayCast 
	function to test for directly to the right of an object.
	
	For example, obj.rayCast( VectorUp(position), position, etc...)
	
	position = object's position to create the 'up' vector from.	
	range = optional argument indicating how far up the vector should go stretch (by default, it's 100 Blender Units)
	"""
	if position == None:
		position = logic.getCurrentController().owner.position
	p = position.copy()
	p.z += range
	return p

def VectorForward(position = None, range = 1):
	"""
	Returns a vector straight forward (+Y). You use this with a rayCast 
	function to test for directly to the right of an object.
	
	For example, obj.rayCast( VectorForward(position), position, etc...)
	
	position = object's position to create the 'forward' vector from.	
	range = optional argument indicating how far the vector should go stretch (by default, it's 100 Blender Units)
	"""
	if position == None:
		position = logic.getCurrentController().owner.position
	p = position.copy()
	p.y += range
	return p

def VectorBackward(position = None, range = 1):
	"""
	Returns a vector straight forward (-Y). You use this with a rayCast 
	function to test for directly to the right of an object.
	
	For example, obj.rayCast( VectorBackward(position), position, etc...)
	
	position = object's position to create the 'backward' vector from.	
	range = optional argument indicating how far the vector should go stretch (by default, it's 100 Blender Units)
	"""
	if position == None:
		position = logic.getCurrentController().owner.position
	p = position.copy()
	p.y -= range
	return p
	
def Scale(amount, obj = None):

	"""
	Scales an object up by an amount.
	
	If amount is a list, then each component of the object's scaling is scaled by the associated component of the list;
	i.e. if amount is [0.1, 1, 10], then the object will be scaled by 0.1 on the X-axis, 1 on the Y-axis, and 10 on the Z-axis.
	If amount is a single number, then all components of the object will be scaled the same.
	"""

	s = obj.scaling
	
	if isinstance(amount, list):
		obj.scaling = [s[0] + amount[0], s[1] + amount[1], s[2] + amount[2]]
	else:
		obj.scaling = [s[0] + amount, s[1] + amount, s[2] + amount]
	
### GAME FUNCTIONS ###	

def MouseLook(obj = None, lockrot = 0, turnspd = 1.0, upcap = 1.4, downcap = -1.4, min = 0.002, macfix = 1, speedadd = 0, friction = 0.9):
	"""
	A generic mouse look script for Blender 2.5. Useful, as all you need to do is run the function
	every frame to have working mouse-look for the selected object.
	
	Author: SolarLune
	Date Updated: 5/14/11
	
	lockrot = whether or not to lock rotation for a certain axis; 0 = none, 1 = X-axis rotation locked (up and down), 2 = Z-axis rotation locked (turning)
	
	turnspd = how sensitive the mouse is
	friction = how quickly the mouse slows down when using speed
	
	upcap = how far upwards the mouse can aim
	downcap = how far downwards the mouse can aim
	min = minimum amount the mouse can move to look (eliminates drifting)
	macfix = a somewhat hacky fix that should smooth mouse-looking on Macs; sets the mouse position to the center only
	when necessary
	speedadd = if the mouse-look should be speed-based (a smoother mouse-look)
	"""

	cont = logic.getCurrentController()
	
	if obj == None:
		obj = cont.owner

	mouse = logic.mouse
	
	win_w = render.getWindowWidth()
	win_h = render.getWindowHeight()
	
	#render.setMousePosition(int(win_w / 2), int(win_h / 2))	# Center mouse; SHOULD ONLY BE DONE IF THE MOUSE GETS UNWIELDY

	if not 'ml_rotx' in obj:
	
		obj['ml_rotx'] = -(obj.localOrientation.to_euler().x - (math.pi * 0.5))
		
		render.setMousePosition(int(win_w / 2), int(win_h / 2))	# Center mouse; SHOULD ONLY BE DONE IF THE MOUSE GETS UNWIELDY
		
		obj['prevmouse'] = [0.5, 0.5]
		
		obj['mousevel'] = mathutils.Vector([0.0, 0.0])
		
		#print (mouse.position, obj['prevmouse'])

		#obj['ml_rotx'] = 0.0
		
	else:

		#print (tuple(mouse.position) + tuple(obj['mousevel']))

		toedge = mathutils.Vector(mouse.position) + obj['mousevel']
		
		if speedadd:
			
			obj['mousevel'] *= friction
	
			obj['mousevel'].x += (mouse.position[0] - obj['prevmouse'][0]) * (turnspd * 0.1)
			obj['mousevel'].y += (mouse.position[1] - obj['prevmouse'][1]) * (turnspd * 0.1)

		else:
			
			obj['mousevel'].x = (mouse.position[0] - obj['prevmouse'][0]) * turnspd
			obj['mousevel'].y = (mouse.position[1] - obj['prevmouse'][1]) * turnspd

		obj['prevmouse'] = [mouse.position[0], mouse.position[1]]
		
		if macfix:
			
			margin = 0.1
		
			if toedge.x < margin or toedge.x > 1.0 - margin or toedge.y < margin or toedge.y > 1.0 - margin:
				
				#print ('reset')
				
				render.setMousePosition(int(win_w / 2), int(win_h / 2))
				
				#obj['mousevel'].x = 0.0
				#obj['mousevel'].y = 0.0
				
				obj['prevmouse'] = [0.5, 0.5]
				
		else:
			
			render.setMousePosition(int(win_w / 2), int(win_h / 2))
			
			obj['mousevel'].x = mouse.position[0] - 0.5
			obj['mousevel'].y = mouse.position[1] - 0.5
						
		mouse_mx = obj['mousevel'].x
		mouse_my = obj['mousevel'].y
		
		if abs(mouse_mx) > min or abs(mouse_my) > min:
	
			if not lockrot == 2:
	
				obj.applyRotation([0, 0, -mouse_mx], 0)
				
			if not lockrot == 1:
				
				if (obj['ml_rotx'] - mouse_my) < upcap and (obj['ml_rotx'] - mouse_my) > downcap:

					obj['ml_rotx'] -= mouse_my

					obj.applyRotation([-mouse_my, 0, 0], 1)		# Apply local rotation last, after the global rotation to avoid camera's twisting	
					
def OldMouseLook(obj = None, lockrot = 0, movespd = 1.0, upcap = 1.4, downcap = -1.4, min = 0.002):
	"""
	A generic mouse look script for Blender 2.5. Useful, as all you need to do is run the function
	every frame to have working mouse-look for the selected object.
	
	Author: SolarLune
	Date Updated: 5/14/11
	
	lockrot = whether or not to lock rotation for a certain axis; 0 = none, 1 = X-axis rotation locked (up and down), 2 = Z-axis rotation locked (turning)
	movespd = how sensitive the mouse is
	upcap = how far upwards the mouse can aim
	downcap = how far downwards the mouse can aim
	min = minimum amount the mouse can move to look (eliminates drifting)
	"""

	cont = logic.getCurrentController()
	
	if obj == None:
		obj = cont.owner

	mouse = logic.mouse
	
	win_w = render.getWindowWidth()
	win_h = render.getWindowHeight()
	
	render.setMousePosition(int(win_w / 2), int(win_h / 2))	# Center mouse; SHOULD ONLY BE DONE IF THE MOUSE GETS UNWIELDY
	
	if not 'ml_rotx' in obj:
	
		obj['ml_rotx'] = -(obj.localOrientation.to_euler().x - (math.pi * 0.5))
		#obj['ml_rotx'] = 0.0
		
	else:

		mouse_mx = (mouse.position[0] - 0.5) * movespd
		mouse_my = (mouse.position[1] - 0.5) * movespd
	
		if abs(mouse_mx) > min or abs(mouse_my) > min:
	
			if not lockrot == 2:
	
				obj.applyRotation([0, 0, -mouse_mx], 0)
				
			if not lockrot == 1:
				
				if (obj['ml_rotx'] - mouse_my) < upcap and (obj['ml_rotx'] - mouse_my) > downcap:

					obj['ml_rotx'] -= mouse_my

					obj.applyRotation([-mouse_my, 0, 0], 1)		# Apply local rotation last, after the global rotation to avoid camera's twisting	

def MouseOrbit(spd = 2.0, xrev = 1, yrev = 0, capspd = 0.075, minimum = 0.002, mb = 0, fixed = 1):

	"""
	Simple mouse orbiting script.
	
	spd = How fast to rotate the object
	minimum = How little a movement will rotate the object
	mb = Which mouse button to use (0 = left mouse button, 1 = middle, 2 = right)
	xrev = Reverse movement on the X-axis
	yrev = Reverse movement on the Y-axis (pitch)
	capspd = Maximum speed the mouse can move before being capped
	fixed = if the orbit speed is local or not (you usually want it fixed)
	"""

	cont = logic.getCurrentController()
	obj = cont.owner

	mouse = logic.mouse

	if mb == 1:
		mmb = events.LEFTMOUSE
	elif mb == 2:
		mmb = events.MIDDLEMOUSE
	elif mb == 3:
		mmb = events.RIGHTMOUSE
	else:
		mmb = None
		
	winw = render.getWindowWidth()
	winh = render.getWindowHeight()

	render.setMousePosition(int(winw / 2), int(winh / 2))

	if not 'mouseorbitinit' in obj:
		
		obj['mouseorbitinit'] = 1		# Eliminate initial view change.
		
	else:
	
		#minimum = 0.002  # How little you have to move the mouse to rotate the view (eliminates drifting)
		
		if mmb == None or mouse.events[mmb]:
			
			mx = mouse.position[0] - 0.5
			my = mouse.position[1] - 0.5
			
			#print (mx, my)

			mx = Clamp(mx, -capspd)
			my = Clamp(my, -capspd)
			
			if xrev:
				mx = -mx
			if yrev:
				my = -my
			
			if fixed:
			
				if abs(mx) > minimum:
					
					obj.applyRotation([0.0, 0.0, mx * spd], 0)
					
				if abs(my) > minimum:
				
					obj.applyRotation([my * spd, 0.0, 0.0], 1)
			
			else:
			
				if max(abs(mx), abs(my)) > minimum:
		
					obj.applyRotation([my * spd, 0.0, mx * spd], 1) # Apply rotation to the Helper object depending on how fast you move the mouse, combined with the speed variable above

def MouseOrbitSpeed(spd = 2.0, xrev = 1, yrev = 0, capspd = 0.075, minimum = 0.002, mb = 2, center = 1):

	"""
	Simple mouse orbiting script.
	
	spd = How fast to rotate the object
	minimum = How little a movement will rotate the object
	mb = Which mouse button to use (0 = left mouse button, 1 = middle, 2 = right)
	xrev = Reverse movement on the X-axis
	yrev = Reverse movement on the Y-axis (pitch)
	center = If it should set the cursor to be in the center of the screen on mouse button press
	"""

	cont = logic.getCurrentController()
	obj = cont.owner

	mouse = logic.mouse

	if mb == 1:
		mmb = events.LEFTMOUSE
	elif mb == 2:
		mmb = events.MIDDLEMOUSE
	elif mb == 3:
		mmb = events.RIGHTMOUSE
	else:
		mmb = None
		
	winw = render.getWindowWidth()
	winh = render.getWindowHeight()

	#minimum = 0.002  # How little you have to move the mouse to rotate the view (eliminates drifting)

	if not 'mouseorbitinit' in obj:
		
		obj['mouseorbitinit'] = 1
	
	else:
	
		if mmb == None or mouse.events[mmb] == 1 and center:
			
			render.setMousePosition(int(winw / 2), int(winh / 2))

		if mmb == None or mouse.events[mmb] == 2:    

			mx = mouse.position[0] - 0.5
			my = mouse.position[1] - 0.5 
			
			mx = Clamp(mx, -capspd)
			my = Clamp(my, -capspd)
			
			if xrev:
				mx = -mx
			if yrev:
				my = -my
			
			if abs(mx) > minimum:
				
				obj.applyRotation([0.0, 0.0, mx * spd], 0)
				
			if abs(my) > minimum:
			
				obj.applyRotation([my * spd, 0.0, 0.0], 1)

def LODSimple(high, highdist, medium, meddist = None, low = None, object = None):
	"""
	A very simple Level of Detail (LOD) script.
	Support for a high detail, medium detail, and low detail mesh.
	
	object = Which object to switch meshes on as well as calculate distance from
	high = What high-detail mesh to use
	highdist = What is the max distance for the high mesh to be displayed
	(minimum distance for next lowest-detail mesh to be displayed)
	medium = What medium-detail mesh to use
	meddist = What is the max distance for the medium mesh to be displayed (must exist if low is used)
	low = What low-detail mesh to use after meddist has been crossed
	"""
	
	from bge import logic
	
	if object == None:
		obj = logic.getCurrentController().owner
	else:
		obj = object
	
	cam = logic.getCurrentScene().active_camera

	if low == None:
	
		if obj.getDistanceTo(cam) > highdist:
			obj.replaceMesh(medium)
		else:
			obj.replaceMesh(high)		
	
	else:
		
		if obj.getDistanceTo(cam) > highdist:
			try:
				if obj.getDistanceTo(cam) > meddist:
					obj.replaceMesh(low)
				else:
					obj.replaceMesh(medium)
			except:
				print ("You can't use the LOD without a maximum medium distance in 'meddist', but with a low-detail mesh.")
		else:
			obj.replaceMesh(high)

def LOD(detaillist, object = None, camera = None, replaceonce = 1):

	"""
		A more complex and flexible LOD system.
		
		detaillist = list of detail meshes and their distances, with the first part of each entry 
		being the distance value, and the second being the mesh name.
		
		For example, [ [0, 'lowpoly'], [10, 'medpoly'], [20, 'highpoly'] ]
		will replace the mesh like this: 
		
		If the distance to the camera is greater than 20, then it will use the 'highpoly' mesh
		Else, if the distance to the camera is greater than 10, then it will use the 'medpoly' mesh
		Else, if the distance to the camera is greater than 0, then it will use the 'lowpoly' mesh
		
		The distance can't go below 0, so use that for the lowest poly mesh for your game object
		
		object = object to perform LOD calculation from (and mesh replacement on)
		
		camera = the object to calculate distance to; doesn't have to be a camera at all - it can even be a point in space.
		
		replaceonce = Replacing the object mesh takes Rasterizer time - doing this every frame is bad on it. Setting this to 1
		ensures that replacing the mesh only is done when necessary (if the object's first mesh is not equal to the mesh to 
		replace).

		There is a known bug that there can be a noticeable stutter when replacing particularly high-poly meshes. This is caused
		by the high poly mesh not being stored in RAM if it is in a hidden layer. The solution is to place the mesh somewhere in an
		active scene (the solution was only tested with the high-poly mesh in the current scene, though other scenes (background
		or overlay) might work, as well).
	"""

	if object == None:
		obj = logic.getCurrentController().owner
	else:
		obj = object
	
	if camera == None:
		cam = logic.getCurrentScene().active_camera
	else:
		cam = camera
	
	mesh = [-1, None]
	
	for entry in detaillist:	# Loop through the detail list and find the entry that's closest to the camera
	
		dist = obj.getDistanceTo(cam)	
	
		if dist > entry[0]:		# The distance to the camera is greater than the minimum distance for the detail mesh, so consider it
		
			if mesh[0] == -1:	# There is no previous mesh to use, so go with this one
			
				mesh = entry
			
			else:				# There is a previous mesh to use, so compare the two (the current one in entry, and the previous one in mesh)
		
				if dist - entry[0] < dist - mesh[0]:	# Compare the current mesh entry's distance value
				
					mesh = entry 						# with the previous mesh's minimum distance to find the one that's closest.
					
					# e.g. High poly mesh at 0, low poly at 50, camera at 100 
					# 100 - 0 = 100, 100 - 50 = 50, low poly is closest, so go with that mesh
					
	if replaceonce:
	
		if str(obj.meshes[0]) != mesh[1]:	# Only replace the mesh if the object's current mesh isn't equal to the one to use (if it's equal, then the mesh was replaced earlier)
		
			obj.replaceMesh(mesh[1])
	
	else:
		
		obj.replaceMesh(mesh[1])

def Occlude(obj = None, size = [2, 2, 2], offset = [0, 0, 0], prop = '', cam = None):
	"""
	Checks to see if the object is visible and is not 'covered' by any other objects
	between the camera and itself by performing nine raycasts from the center and corners of the object to the camera.
	
	If the function returns 1, then the object is completely occluded on all ray casts.
	If the function returns -1, then the object is partially occluded on some ray casts.
	If the function returns 0, then the object is not occluded on any raycasts.
	
	obj = which object to check from
	size = size of the object (defaults to the size of the normal cube)
	prop = what property that occluding objects must have with this variable to be registered as 'occluding' the object
	
	offset = offset of the object from its center (can be found out by going into edit mode,
	selecting all vertices, and then seeing where the center is) - an offset of [0, 0, 0] (default) is discarded
	
	cam = which camera to occlude from; defaults to the scene's active camera
	
	This is a basic custom occlusion, much like Blender does when you have Occluder meshes.

	"""
	
	def Check(r):
		if r != None:
			return 1
		else:
			return 0

	def Offset(vec):
	
		if offset[0] != 0 or offset[1] != 0 or offset[2] != 0:
			v = vec
			v[0] += offset[0]
			v[1] += offset[1]
			v[2] += offset[2]
			return v
		else:
			return vec

	if cam == None:
		cam = logic.getCurrentScene().active_camera
	if obj == None:
		object = logic.getCurrentController().owner
		
	result = 0

	pos = object.worldPosition.copy()
	pos = Offset(pos)
	r = cam.rayCast(pos, cam.position, 0, prop, 1, 1)
	if Check(r[0]): result += 1
	
	pos = object.worldPosition.copy()
	pos = Offset(pos)
	pos.x += size[0] / 2.0
	pos.z += size[2] / 2.0
	
	r = cam.rayCast(pos, cam.position, 0, prop, 1, 1)
	if Check(r[0]): result += 1

	pos = object.worldPosition.copy()
	pos = Offset(pos)
	pos.x -= size[0] / 2.0
	pos.z += size[2] / 2.0
	
	r = cam.rayCast(pos, cam.position, 0, prop, 1, 1)
	if Check(r[0]): result += 1
	
	pos = object.worldPosition.copy()
	pos = Offset(pos)
	pos.x -= size[0] / 2.0 
	pos.z -= size[2] / 2.0
	
	r = cam.rayCast(pos, cam.position, 0, prop, 1, 1)
	if Check(r[0]): result += 1
	
	pos = object.worldPosition.copy()
	pos = Offset(pos)
	pos.x += size[0] / 2.0 
	pos.z -= size[2] / 2.0
	
	r = cam.rayCast(pos, cam.position, 0, prop, 1, 1)
	if Check(r[0]): result += 1
	
	pos = object.worldPosition.copy()
	pos = Offset(pos)
	pos.y += size[1] / 2.0
	pos.z += size[2] / 2.0
	
	r = cam.rayCast(pos, cam.position, 0, prop, 1, 1)
	if Check(r[0]): result += 1
	
	pos = object.worldPosition.copy()
	pos = Offset(pos)
	pos.y -= size[1] / 2.0
	pos.z += size[2] / 2.0
	
	r = cam.rayCast(pos, cam.position, 0, prop, 1, 1)
	if Check(r[0]): result += 1
	
	pos = object.worldPosition.copy()
	pos = Offset(pos)
	pos.y -= size[1] / 2.0 
	pos.z -= size[2] / 2.0
	
	r = cam.rayCast(pos, cam.position, 0, prop, 1, 1)
	if Check(r[0]): result += 1
	
	pos = object.worldPosition.copy()
	pos = Offset(pos)
	pos.y += size[1] / 2.0 
	pos.z -= size[2] / 2.0
	
	r = cam.rayCast(pos, cam.position, 0, prop, 1, 1)
	if Check(r[0]): result += 1
	
	if result >= 9:
		result = 1	# Stopped by an occluding object on all raycasts
	elif result > 0:
		result = -1	# Stopped by an occluding object on one or more raycasts
		
	# 0 = not stopped by an occluding object by any raycasts
	
	return result

def TrackTo(dest, obj = None, axis = 'y', time = 0, dimensions = "xyz"):

	"""
	Track To function equivalent to the track to actuator.
	Contributed by Siegel.

	dest = destination object (or point) to track to
	obj = source object to rotate; if set to None or omitted, it defaults to the object running the script
	axis = which axis ('x', 'y', or 'z') to align the source object to the destrination point
	time = time value to rotate the source object by (in seconds)
	dimensions = specify which global axes to track on; you can select which ones to align to the object
	"""

	if obj == None:
		obj = logic.getCurrentController().owner
		
	if axis == 'x':
		axis = 0
	elif axis == 'y':
		axis = 1
	elif axis == 'z':
		axis = 2

	vect = obj.getVectTo(dest)
	
	if dimensions.count("x") == 0:
		vect[1].x = 0
	if dimensions.count("y") == 0:
		vect[1].y = 0
	if dimensions.count("z") == 0:
		vect[1].z = 0
		
	if time > 0:
		obj.alignAxisToVect(vect[1], axis, 1.0/time)
	else:
		obj.alignAxisToVect(vect[1], axis)

def GetColor(x, y, array, size, comp = 4):

	""" 
	GetColor V1.1
	Author: SolarLune
	Date Updated: 7/31/11
	
	Returns the color of the pixel at position x, y
	in the given image array; notice that this only
	works with the bge.texture module's imageToArray function
	(or perhaps just the texture's source)
	
	x = X-pixel's color to check
	y = Y-pixel's color to check
	array = image array; can be found with the bge.texture module's imageToArray function, or by passing the source
	size = 2 component list or tuple; size in width/height of the image. Can be found with the texture's source's size
	comp = how many components per color (should be either 3 (RGB) or 4 (RGBA) - 4 is default)
	"""

	# Old method of getting the width (size) of the image; it's just better to pass it in yourself

	# size = len(array) / comp   # Four values per pixel (RGBA)
	# size = math.sqrt(size)     # Square size gets the size of the image (because it's 512x512, for example)

	# New method allows for oddly sized images

	comp = 4 

	width = size[0]
	height = size[1]

	if x < 0:   # You can't look beyond the left without a warning
		x = 0
	elif x > width - 1:
		x = width - 1
	if y < 0:
		y = 0
	elif y > height - 1:
		y = height - 1
		
	value = (math.floor(x) * comp) + ((math.floor(y) * comp) * width)
	value = int(value)

	if comp == 4:
		return [array[value], array[value + 1], array[value + 2], array[value + 3]]
	else:
		return [array[value], array[value + 1], array[value + 2]]
	
### BGE MESH FUNCTIONS ###

def GetSharedVertices(mesh, vert, max_diff = 0, mat = 0):
	
	"""Returns the vertices sharing the position occupied by the vertex 'vert'. 
	'mesh' = which object's vertices to check; 
	'vert' = which vertex to find the duplicates of
	'mat' = which vertices of 'mesh' to check, according to material index, I believe.
	note that this goes through all vertices, so this should only be used with lower-poly objects
	and	should only be done rarely to keep up efficiency."""

	list = []
	
	for a in range(mesh.getVertexArrayLength(mat)):

		v = mesh.getVertex(mat, a)
		
		if max_diff != 0:
			if abs(v.x - vert.x) < max_diff and abs(v.y - vert.y) < max_diff and abs(v.z - vert.z) < max_diff:
				list.append(v)
		else:
			if v.x == vert.x and v.y == vert.y and v.z == vert.z:
				list.append(v)
	
	return list

def GetFaces(mesh):

	"""
	Return the faces of the mesh specified.
	"""

	return([mesh.getPolygon(f) for f in range(mesh.numPolygons)])
	
def GetVertices(mesh = None, shared = 1, mat = 0):
	"""
	Returns a list of all vertices in the mesh of the specified material.
	mesh = what mesh to look through (can be found with obj.meshes)
	shared = whether or not to discard similar vertices (i.e. only to return unique vertices)
	mat = what material's mesh to search through
	"""
	verts = []

	if mesh == None:
		obj = logic.getCurrentController().owner
		mesh = obj.meshes[0]
	
	for v in range(mesh.getVertexArrayLength(mat)):

		vert = mesh.getVertex(mat, v)
		xyz = vert.getXYZ()
		
		if shared:		# If the function should eliminate vertices that are already present, as in certain cases, BGE meshes return more vertices than are actually there
			if not xyz in verts:
				verts.append(xyz)
		else:
			verts.append(xyz)
	
	return verts

def FurthestVertices(mesh = None):

	"""
	Calculates the furthest points from the center of 'mesh' by stepping through each vertex.
	This means that it's a slow process, but it works fairly well.
	Returns a list of the two (mathematically) furthest points on the mesh.
	"""
	
	if mesh == None:
		obj = logic.getCurrentController().owner
		mesh = obj.meshes[0]
	
	verts = []  
	
	for v in range(mesh.getVertexArrayLength(0)):
		vert = mesh.getVertex(0, v)
		verts.append(vert.getXYZ())
        
	verts.sort()
    
	verts = [verts[0], verts[len(verts) - 1]]
    
	return verts	
		
### MISC. BGE FUNCTIONS ###

def GetGLBindID(obj, material = None):
	
	"""
	An attempt at getting an OpenGL Bind ID from a texture, given an object and material name. It's only useful if you're messing about
	with OpenGL, blitting a texture over the screen. I'm not sure if this will work, but it should... Maybe. :P
	"""

	if material == None:
		material = obj.meshes[0].materials[0]
		
	matid = texture.materialID(obj, str(material))
	t = texture.Texture(obj, matid)
	
	bindid = t.bindId
	t.close()
	del t

	return (bindid)

def SoftBodyPin(softbodyobj, controls):

	"""
	Pins the soft body object to an object using its vertices (a control object). It will pin the soft-body
	object to all of the vertices of all of the objects in the controls list. So, for controls pass a list like:
	
	[ControlObject, ControlObject2, etc.]
	
	where ControlObject are Game Objects fetched through the scene list, for example.
	"""
	
	softid = softbodyobj.getPhysicsId()
	ctype = 2 # Constraint type, 1 = edge; 0 = point, 2 = angular?
	
	for c in controls:
	
		cid = c.getPhysicsId()
	
		for vert in range(c.meshes[0].getVertexArrayLength(0)):
		
			vpos = c.meshes[0].getVertex(0, vert).getXYZ()
			
			constraints.createConstraint(softid, cid, ctype, vpos[0], vpos[1], vpos[2], 8, -1, 0.5)

def GetDimensions(object, roundit = 3, mesh = None):

	"""
	Gets the dimensions of the object (what you see under dimensions in the properties window in the 3D menu).
	object = which object to use; note that it will by default use the first mesh; you can specify which mesh by providing the mesh
	via the mesh property.
	roundit = how far down to round the returned dimension values; set it to a negative number to not round the numbers off at all.
	"""

	s = object.worldScale
	
	if mesh == None:	
		mesh = object.meshes[0]

	#print (dir(mesh))
	
	verts = [[], [], []]
	
	for v in range(mesh.getVertexArrayLength(0)):
	
		vert = mesh.getVertex(0, v)
		
		pos = vert.getXYZ()
		
		verts[0].append(pos[0])
		verts[1].append(pos[1])
		verts[2].append(pos[2])
	
	verts[0].sort()
	verts[1].sort()
	verts[2].sort()

	if roundit >= 0:
		size = [
		round( (verts[0][len(verts[0]) - 1] - verts[0][0]) * s[0] , roundit), 
		round( (verts[1][len(verts[0]) - 1] - verts[1][0]) * s[1] , roundit), 
		round( (verts[2][len(verts[0]) - 1] - verts[2][0]) * s[2] , roundit) ]
	else:
		size = [(verts[0][len(verts[0]) - 1] - verts[0][0]) * s[0], 
		(verts[1][len(verts[0]) - 1] - verts[1][0]) * s[1], 
		(verts[2][len(verts[0]) - 1] - verts[2][0]) * s[2]]
		
	#print (size)
	
	return (size)

def AxisCheck(mx, my, mz, dist = 1.0, prop = 'wall', face = 1, xray = 1, poly = 1):
	"""
	Performs a raycast along a single direction with mx, my, and mz indicating the ending position.
	"""
	cont = logic.getCurrentController()
	obj = cont.owner

	pos = obj.position									# Get the Player's current position
	topos = pos.copy()									# Make a copy of the Player's current position
	topos.x += (Sign(mx) * dist) + mx					# Offset the copy by the movement value for the X-axis
	topos.y += (Sign(my) * dist) + my					# And offset the copy by the movement value for the Y-axis
	topos.z += (Sign(mz) * dist) + mz
	
	return obj.rayCast(topos, pos, 0, prop, face, xray, poly)		# We may have just collided with something on the line specified

def UVScroll(uspd = 0.0025, vspd = 0.0, layer = 0, mesh = None, mat = 0, freqstretch = 1):
	"""
	Scrolls the UV Coordinate of each vertex in the specified mesh by
	uspd and vspd.
	uspd = how fast to scroll on the X-axis (X)
	vspd = how fast to scroll on the V-axis (Y)
	layer = which UV-layer to scroll; 0 = first layer, 1 = second, 2 = both
	mesh = which mesh to use for UV-animation
	mat = which material to look for (I think it's organized by material)
	freqstretch = frequency-stretching enabled - if set to 1, then you can run this script with an Always sensor set to a
	limited frequency rate and still scroll the UV-map by the same speed, so you should only connect this script's controller to a single Always sensor
	"""
	
	from bge import logic

	cont = logic.getCurrentController()
	obj = cont.owner
	
	if mesh == None:
		mesh = obj.meshes[mat]

	if freqstretch:
		f = cont.sensors[0].frequency + 1
	else:
		f = 1
		
	for v in range(mesh.getVertexArrayLength(mat)):
		
		vert = mesh.getVertex(0, v)

		if layer == 0 or layer == 2:
			vert.u += uspd * f
			vert.v += vspd * f
		if layer == 1 or layer == 2:
			vert.u2 += uspd * f
			vert.v2 += vspd * f

def FindMaterial(material, obj = None):
	"""
	Looks through obj's materials to find the material indicated by the string in 'material' and returns the index of that material;
	if that material isn't found, then it returns 0.
	
	obj = object to look in
	material = material (string) to look for
	"""

	if obj == None:
		obj = logic.getCurrentController().owner
	
	mesh = obj.meshes[0]
	
	for m in range(len(mesh.materials)):	# Loop through materials in the mesh
	
		mname = str(mesh.materials[m])
		
		if mname[2:] == material:		# If the material minus the first 'MA' is found, then
			return m					# Return the index of that material
			break	
			
	else:
		return 0						# Default to material index 0

def VertCol(color, obj = None, material = None):

	"""
	Set the color of each vertex in the object's first mesh.
	obj = (object pointer) object to change vertex color on
	color = (list) color to change each vertex's color value to
	material = name (string) of what material in particular to change the material's color to
	"""

	if obj == None:
		obj = logic.getCurrentController().owner
	
	mesh = obj.meshes[0]

	if material != None:
		mat = FindMaterial(obj, material)
	else:
		mat = 0

	for v in range(mesh.getVertexArrayLength(mat)):

		vert = mesh.getVertex(0, v)
		vert.color = color	

def Near(objpos = None, prop = '', mindist = 0, maxdist = 9999999, sort = 0, checklist = None, onlyobj = 0):
	"""
	Returns a list of objects (and their corresponding distances) that are within the range of 'maxdist' in Blender Units 
	from the point indicated by 'objpos'.
	
	objpos = either a Vector (position variable), a 3D list position, or a game object. 
	If it is an object, then that object is
	excluded from the check (i.e. it won't return its own object as being near itself in the near list), and
	the checks performed are relative to the cube
	
	maxdist = Maximum distance from the object any objects must be to be returned (defaults to 9,999,999 BU)
	mindist = Minimum distance from the object any objects must be to be returned (optional)
	
	property = What property any near objects must have to be returned; a property value of '' (default) will check for any object
	sort = If the function should sort the list in order of closest object to furthest; scales in speed lost to list's size, I would assume
	checklist = A list that you can specify to check through. If None, then the function will use the scene's object list; otherwise, it will check through
	the list. List can either consist of strings or game objects.
	"""
		
	sce = logic.getCurrentScene()
	
	if objpos == None:
		objpos = logic.getCurrentController().owner
	
	if isinstance(objpos, mathutils.Vector):								# Supplied object position is a position Vector
		pos = objpos														# Position to check from - an object's position
		removeobj = None
	elif isinstance(objpos, list) or isinstance(objpos, tuple):				# Supplied object position is a tuple or list
		pos = mathutils.Vector(objpos)										# Position to check from
		removeobj = None
	else:																	# Supplied object position is an object
		pos = objpos.worldPosition
		removeobj = objpos
		
	if checklist == None:							# Use the scene's objects
		objlist = sce.objects
	else:											# Use the list provided
		objlist = checklist
		
	returnlist = []
		
	for object in objlist:
	
		if isinstance(object, str):				# It's possible that checklist passed is a set of strings and not object pointers
			obj = sce.objects[object]			# If it's a list of strings, then reference the scene's object list for the objects
		else:
			obj = object
		
		if not removeobj == obj and not obj.invalid:				# Don't take into account the object you're testing from to be in the list
		
			dist = obj.getDistanceTo(pos)
				
			if prop != '':					# If the property field is blank, then just get any and all scene objects within range
			
				if prop in obj and dist <= maxdist and dist >= mindist:
				
					if onlyobj:
					
						returnlist.append(obj)
					
					else:
					
						returnlist.append([obj, dist])
			else:
			
				if dist <= maxdist and dist >= mindist:
				
					if onlyobj:
				
						returnlist.append(obj)
					
					else:
					
						returnlist.append([obj, dist])
	
	if sort:
	
		if onlyobj:
		
			returnlist.sort(key = lambda sortkey : str(sortkey.name)) # If there's only objects in the list (no distance values), it sorts the list by object name
		
		else:
	
			returnlist.sort(key = lambda sortkey : sortkey[1])	# If sort is set to 1 (and onlyobj is not set to 1), it sorts the list, using as a key the distance values to the object
	
	if len(returnlist) <= 0:
		returnlist = [None]
	
	return returnlist

def RayCastList(topos, frompos, prop = None, face = 0, xray = 1):
	""" Uses a series of raycasts to find all objects that collide on a specific ray; an example would be 
	to find any enemy (more than one) that is in a straight line from the Player to where he's aiming.
	topos = the end position of the raycast
	frompos = the start position of the raycast (e.g. the Player's position)
	prop = what property to look for; None or "" will search for any object
	face = whether or not to return face values
	xray = whether or not to look through objects that don't have the property specified
	"""	
	
	from bge import logic
	
	obj = logic.getCurrentController().owner

	l = []							# List of hit vectors
	o = []							# List of hit objects (an object can only be counted once)
	
	pos = frompos

	for x in range(100):			# Maximum would be 100 hits
		
		if prop == None:			# None is not an acceptable type; defaults to a blank string
			prop = ""
			
		r = obj.rayCast(topos, pos, 0, prop, face, xray)
			
		if r[0] != None:
			if not r[0] in o:
				l.append(r)			# Add the raycast listing
				o.append(r[0])		# Add the object to the hit object list (you can't hit the same object twice)
			
			pos = r[1]
			
		else:
			print (o)
			#print ("---")
			return l
			break
	
	print (o)
	#print ("---")
	return l

def RayCastCorners(angle, pos = None, dist = 100000.0, size = 1, prop = '', face = 0, xray = 1, axis = 0):
	"""
	Docstring! OK, so...
	pos = position to check from (usually the center of the object)
	angle = angle to check rays on
	dist = distance outwards to check rays on
	size = how far out from the center to check in 4 directions
	axis = which set of axes to check (0 = x and y, 1 = x and z)
	
	This is pretty much deprecated in favor of the RayCastWidth functions.
	
	"""

	obj = logic.getCurrentController().owner
	
	if pos == None:
		pos = obj.worldPosition

	pos = pos.copy()
	
	if prop == None:
		prop = ""
	
	topos = pos.copy()
	topos.x += math.cos(angle) * dist
	topos.z += math.sin(angle) * dist
	
	r = obj.rayCast(topos, pos, 0, prop, face, xray)

	if r[0] == None:
		pos.x += size / 2.0
		if axis == 0:
			pos.y += size / 2.0
		else:
			pos.z += size / 2.0
			
		topos = pos.copy()
		topos.x += math.cos(angle) * dist
		topos.z += math.sin(angle) * dist
	
		r = obj.rayCast(topos, pos, 0, prop, face, xray)
	
	if r[0] == None:
		pos.x -= size
		
		topos = pos.copy()
		topos.x += math.cos(angle) * dist
		topos.z += math.sin(angle) * dist
	
		r = obj.rayCast(topos, pos, 0, prop, face, xray)
	
	if r[0] == None:
	
		if axis == 0:
			pos.y -= size
		else:
			pos.z -= size
			
		topos = pos.copy()
		topos.x += math.cos(angle) * dist
		topos.z += math.sin(angle) * dist
	
		r = obj.rayCast(topos, pos, 0, prop, face, xray)
	
	if r[0] == None:
		pos.x += size
		
		topos = pos.copy()
		topos.x += math.cos(angle) * dist
		topos.z += math.sin(angle) * dist
	
		r = obj.rayCast(topos, pos, 0, prop, face, xray)
	
	#print (r)
	
	return (r)	

def RayCastWidthXY(angle, pos = None, dist = 100000.0, width = 0.5, prop = '', face = 0, xray = 1):
	"""
	Performs three raycasts out from the position specified - the first being from the center out, the second
	being to the left side, specified by angle, and the right doing the same.
	pos = position to check from
	angle = angle (in radians) to ray cast to
	dist = distance in Blender Units to check
	width = width in BU to spread out for the side raycasts
	prop = property to search for
	face = whether or not to return the hit face
	xray = go through objects that don't have the property or not
	"""
	
	cont = logic.getCurrentController()
	obj = cont.owner
	
	if pos == None:
		pos = obj.worldPosition
	
	p = pos.copy()
	
	topos = p.copy()
	topos.x += math.cos(angle)
	topos.y += math.sin(angle)
	
	ray = 'middle'	# Which raycast worked
	
	if prop == None:
		prop = ""
	
	r = obj.rayCast(topos, p, dist, prop, face, xray)
	
	if r[0] == None:	# raycast the right side

		ray = 'right'
		
		rangle = angle + (math.pi / 2.0)
		p.x += math.cos(rangle) * width
		p.y += math.sin(rangle) * width
		topos.x += math.cos(rangle) * width
		topos.y += math.sin(rangle) * width
		r = obj.rayCast(topos, p, dist, prop, face, xray)
		
	if r[0] == None:	# Since both the middle raycast and the right raycast failed, try left

		ray = 'left'
	
		langle = angle - (math.pi / 2.0)
		
		p.x += (math.cos(langle) * width) * 2.0
		p.y += (math.sin(langle) * width) * 2.0
		topos.x += (math.cos(langle) * width) * 2.0
		topos.y += (math.sin(langle) * width) * 2.0
		
		r = obj.rayCast(topos, p, dist, prop, face, xray)
		
	#print ([r, ray])
	
	return (r, ray)

def RayCastWidthXZ(angle, pos = None, dist = 100000.0, width = 0.5, prop = '', face = 0, xray = 1):
	
	cont = logic.getCurrentController()
	obj = cont.owner
	
	if pos == None:
		pos = obj.worldPosition.copy()
	
	p = pos.copy()
	
	topos = p.copy()
	topos.x += math.cos(angle)
	topos.z += math.sin(angle)
	
	ray = 'middle'	# Which raycast worked
	
	if prop == None:
		prop = ""
	
	r = obj.rayCast(topos, p, dist, prop, face, xray)

	if r[0] == None:	# raycast the right side

		ray = 'right'
		
		rangle = angle + (math.pi / 2.0)

		p.x += math.cos(rangle) * width
		p.z += math.sin(rangle) * width
		topos.x += math.cos(rangle) * width
		topos.z += math.sin(rangle) * width
		r = obj.rayCast(topos, p, dist, prop, face, xray)
		
	if r[0] == None:	# Since both the middle raycast and the right raycast failed, try left

		ray = 'left'
	
		langle = angle - (math.pi / 2.0)
		
		p.x += (math.cos(langle) * width) * 2.0
		p.z += (math.sin(langle) * width) * 2.0
		topos.x += (math.cos(langle) * width) * 2.0
		topos.z += (math.sin(langle) * width) * 2.0
		
		r = obj.rayCast(topos, p, dist, prop, face, xray)
		
	#print ([r, ray])
	
	return (r, ray)	

def RayCastAngleXZ(angle, pos = None, dist = 100000.0, prop = '', face = 0, xray = 1):
	"""
	Performs a RayCast function check on a given angle rather than to a specific position. The check is done on the X and Z axes.
	pos = starting position
	angle = angle to check on
	dist = distance to check (max)
	prop = property to search for; "" = check all collisions
	face = return the face normal for the collision
	xray = don't return the first collision, regardless of whether it's an object with the property specified or not
	(with xray = false, it will return first collision, whether or not it meets the property standard)
	
	Note that this is pretty much just RayCastWidth without the side raycasts
	"""
	
	
	cont = logic.getCurrentController()
	obj = cont.owner
	
	if pos == None:
		pos = obj.worldPosition
	
	p = pos.copy()
	
	topos = p.copy()
	topos.x += math.cos(angle)
	topos.z += math.sin(angle)
	
	if prop == None:
		prop = ""
	
	r = obj.rayCast(topos, pos, dist, prop, face, xray)
	
	return r

def RayCastAngleXY(angle, pos = None, dist = 100000.0, prop = '', face = 0, xray = 1):
	"""
	Performs a RayCast function check on a given angle rather than to a specific position. The check is done on the X and Y axes.
	pos = starting position
	angle = angle to check on
	dist = distance to check (max)
	prop = property to search for; "" = check all collisions
	face = return the face normal for the collision
	xray = don't return the first collision, regardless of whether it's an object with the property specified or not
	(with xray = false, it will return first collision, whether or not it meets the property standard)
	"""

	cont = logic.getCurrentController()
	obj = cont.owner
	
	if pos == None:
		pos = obj.worldPosition
		
	p = pos.copy()
	
	topos = p.copy()
	topos.x += math.cos(angle)
	topos.y += math.sin(angle)
	
	if prop == None:
		prop = ""
	
	r = obj.rayCast(topos, pos, dist, prop, face, xray)
	
	return r
