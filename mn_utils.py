'''
Copyright (C) 2014 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy, random, ast
	
# simple general functions
##########################
	
def getActive():
	return bpy.context.scene.objects.active
def setActive(object):
	bpy.context.scene.objects.active = object
	object.select = True
def getSelectedObjects():
	try: return bpy.context.selected_objects
	except: return []
def deselectAll():
	bpy.ops.object.select_all(action = "DESELECT")
def deselectAllFCurves(object):
	if object.animation_data is not None:
		if object.animation_data.action is not None:
			for fCurve in object.animation_data.action.fcurves:
				fCurve.select = False
def getCurrentFrame():
	try: return bpy.context.scene.frame_current_final
	except: return 1
def getRandom(min, max):
	return random.random() * (max - min) + min
def getRandomString(length):
	return ''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(length))
def clampInt(value, minValue, maxValue):
	return int(max(min(value, maxValue), minValue))
def isAnimationPlaying():
	try:	
		return bpy.context.screen.is_animation_playing
	except:	return False
def nameToPath(name):
	return '["' + name + '"]'
def printTimeSpan(name, timeSpan, extraInfo = ""):
	print(name + " " + str(round(timeSpan, 7)).rjust(13) + " s  -  " + str(round(1.0 / timeSpan, 5)).rjust(13) + " fps  " + extraInfo)
	
# nodes and sockets
######################

def getNode(treeName, nodeName):
	return bpy.data.node_groups[treeName].nodes[nodeName]
def getSocketFromNode(node, isOutputSocket, name):
	if isOutputSocket:
		return node.outputs.get(name)
	else:
		return node.inputs.get(name)
def getSocketByIdentifier(node, isOutputSocket, identifier):
	if isOutputSocket: return getSocketFromListByIdentifier(node.outputs, identifier)
	return getSocketFromListByIdentifier(node.inputs, identifier)
def getSocketFromListByIdentifier(sockets, identifier):
	for socket in sockets:
		if socket.identifier == identifier: return socket
	return None
def getNodeIdentifier(node):
	return node.id_data.name + node.name
	
def getConnectionDictionaries(node):
	inputSocketConnections = {}
	outputSocketConnections = {}
	for socket in node.inputs:
		value = socket.getStoreableValue()
		if hasLinks(socket):
			inputSocketConnections[socket.identifier] = (value, socket.links[0].from_socket, socket.bl_idname)
		else:
			inputSocketConnections[socket.identifier] = (value, None, socket.bl_idname)
	for socket in node.outputs:
		outputSocketConnections[socket.identifier] = []
		for link in socket.links:
			outputSocketConnections[socket.identifier].append(link.to_socket)
	return (inputSocketConnections, outputSocketConnections)
def tryToSetConnectionDictionaries(node, connections):
	nodeTree = node.id_data
	#inputs
	inputConnections = connections[0]
	for identifier in inputConnections:
		nodeSocket = getSocketFromListByIdentifier(node.inputs, identifier)
		if nodeSocket is not None:
			if nodeSocket.bl_idname == inputConnections[identifier][2]:
				nodeSocket.setStoreableValue(inputConnections[identifier][0])
			if inputConnections[identifier][1] is not None:
				nodeTree.links.new(nodeSocket, inputConnections[identifier][1])

	#outputs
	outputConnections = connections[1]
	for identifier in outputConnections:
		nodeSocket = getSocketFromListByIdentifier(node.outputs, identifier)
		if nodeSocket is not None:
			for toSocket in outputConnections[identifier]:
				nodeTree.links.new(toSocket, nodeSocket)
	
# socket origins
######################
	
def isSocketLinked(socket):
	origin = getOriginSocket(socket)
	return isOtherOriginSocket(socket, origin)
	
def isOtherOriginSocket(socket, origin):
	return origin is not None and origin.node.name != socket.node.name
		
def getOriginSocket(socket):
	if hasLinks(socket):
		fromSocket = socket.links[0].from_socket
		if fromSocket.node.type == "REROUTE":
			return getOriginSocket(fromSocket.node.inputs[0])
		else:
			return fromSocket
	else:
		if socket.node.type == "REROUTE":
			return None
		else:
			return socket
		
def hasLinks(socket):
	return len(socket.links) > 0
	
	
# code
########################

def isValidCode(code):
	try:
		ast.parse(code)
	except SyntaxError:
		return False
	return True
