import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *


class mn_ModifierSocket(mn_BaseSocket, mn_SocketProperties):
	"""A Class that extents an animation node socket witch represents a modifier of an object.
	
	Note: 
		Tho node socket may be linked to an object socket input.
	
	Attributes:
		bl_idname (str): Blender's id name is 'mn_ModifierSocket'.
		bl_label (str): Blender's Label is 'Modifier Socket'.
		dataType (str): This socket has an animation socket type of 'Modifier'.
		allowedInputTypes (Array of str): This animation socket is IO compatible with Object and Modifier type of sockets.
		drowColor (vertex Color): The color of this socket is cyan-ish
		objectName (str): The name of blender Object witch this socket is refer to.
		modifierName (str): The name of blender Modifier witch this socket is refer to.
	"""
	bl_idname = "mn_ModifierSocket"
	bl_label = "Modifier Socket"
	dataType = "Modifier"
	
	allowedInputTypes = ["Modifier"]
	drawColor = (0.4, 0.6, 0.8, 1)
	
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	modifierName = bpy.props.StringProperty(update = nodePropertyChanged)
	
	def drawInput(self, layout, node, text):
		"""This function is responsible to draw the graphics of an input animation socket.
		
		Draws a drop down textbox to select the name of the object, an button to select 
		the name of the active blender object and a dynamic drop down textbox to select the name of the 
		Modifier when a blender object is specified.
		
		Args:
			layout (UIlayout): the canvas to draw.
			node (Node): the node that this socket is associated to.
			text (str) a custom text to draw to canvas.
		"""
		col = layout.column()
		row = col.row(align = True)
		# draw the object name dropdown textbox
		row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = "")
		# draw the button to select the active object
		selector = row.operator("mn.assign_active_object_to_socket", text = "", icon = "EYEDROPPER")
		selector.nodeTreeName = node.id_data.name
		selector.nodeName = node.name
		selector.isOutput = self.is_output
		selector.socketName = self.name
		selector.target = "objectName"
#		col.separator()
		row = col.row(align = True)
		# draw the modifier name dropdown textbox only when object name is assigned.
		if(self.objectName):
			row.prop_search(self, "modifierName", bpy.context.scene.objects[self.objectName] , "modifiers", icon="NONE", text = "")
		col.separator()
	def getValue(self):
		""" Gets the value of the object's modifier this socket is represent to.
		
		Returns:
			bpy.Types.Modifier Modifier witch this socket is represents, 
			Node if this socket is not associated with a object's modifier.
			 
		"""
		if not self.objectName:
			return None
		if not self.modifierName:
			return None
#		print("getValue: return: ", bpy.data.objects[self.objectName].modifiers.get(self.modifierName))
		return bpy.data.objects[self.objectName].modifiers.get(self.modifierName)
		
	def setStoreableValue(self, data):
		"""Adjust the animation node socket to represent an new modifier.
		
		Note: 
			Tho node socket may be linked to an object socket input.
		Args:
			data (bpy.Types.Modifier or bpy.Types.Object): The pointer to an object or to a specific modifier os  object.
			Node if this socket is not associated with a object's modifier.
			 
		"""
#		print("mn_modifiier setStoreableValue: ", data.id_data.name, " -> ", data.name)
		if data is None:
			return
		self.objectName = data.id_data.name
		self.modifierName = data.name
		
	def getStoreableValue(self):
		""" Get a storeable representation of the object's modifier this socket is represent to.
		
		Returns: 
			The RNA path of the modifier as a string,
			an empty string name if this socket is not associated with a modifier.
		"""
		if not self.objectName:
			return ""
		if not self.modifierName:
			return ""
		return "bpy.data.objects[\""+self.objectName+"\"].modifiers[\""+self.modifierName+"\"]"


