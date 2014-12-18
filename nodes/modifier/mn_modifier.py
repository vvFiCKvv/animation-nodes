import bpy
from types import MethodType
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *


class mn_ModifierNode(Node, AnimationNode):
	"""A Class that extents an animation node witch represents a modifier of an object 
	and have the functionality to create input sockets for each property of the Modifier.
	
	Note: 
		Tho node may be linked to an object socket input.
	
	Attributes:
		bl_idname (str): Blender's id name is 'mn_ModifierNode'.
		bl_label (str): Blender's Label is 'Modifier Node'.
		node_category (str): This node is type of 'Modifier'.
		objectName (str): The name of blender Object witch this node is refer to.
		modifierName (str): The name of blender Modifier witch this node is refer to.
		propertyName (str): The name of blender Modifier Property witch this node is refer to.
	"""
	bl_idname = "mn_ModifierNode"
	bl_label = "Modifier Node"
	node_category = "Modifier"
	
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	modifierName = bpy.props.StringProperty(update = nodePropertyChanged)
	
	def drawSearchSocket(a, self, layout, node, text):
		print("Mpika")
		layout.label("OK")
#		layout.prop_search(self, "string", searchData , self.searchProperty, icon="NONE", text = "")

	def init(self, context):
		"""Initialization of the node.
		
		Args:
			context:
		"""
		forbidCompiling()
		socket = self.inputs.new("mn_ObjectSocket", "Object")
		socket.showName = False
		socket = self.inputs.new("mn_StringSearchSocket", "Modifier")
#		socket = self.inputs.new("mn_StringSocket", "Modifier")
#		print(getattr(socket, 'drawInput'))
#		setattr(socket, "drawInput", MethodType(self.drawSearchSocket, socket))
#		setattr(socket.__class__, "drawInput", classmethod(self.drawSearchSocket))
#		socket.drawInput = staticmethod(self.drawSearchSocket)
#		print(getattr(socket, 'drawInput'))
		
		socket.showName = True
		self.outputs.new("mn_ModifierSocket", "Modifier").showName = False
		allowCompiling()
		
	def changeObject(self, objectName):
		"""This function called when the name of the object changes and is responsible for enumerate the input - output sockets.
		
		Args:
			object (bpy.types.Object): The name to correct object.
		"""
		forbidCompiling()
		self.inputs["Modifier"].searchPath = "bpy.context.scene.objects['" + objectName + "']"
		self.inputs["Modifier"].searchProperty = "modifiers"
		self.objectName = objectName
		allowCompiling()
		return


	def execute(self, inputs):
		"""Maintain the node values and structure according to the input changes.
		
		Note:
			The input for Modifier Socket may be the pointer to a Modifier or the pointer to an object.
			if is an pointer to an object, the name of the moidifier will assigned from the UI of the node.
		
		Args:
			inputs (Array): the key to the Array is the socket names or their identifiers
			and the value is the pointer to the data either throw the link of the
			input socket either throw the value of it.
		"""
		forbidCompiling()
		output = {}
		if inputs["Object"] is not None and inputs["Object"].name != self.objectName:
			self.changeObject(inputs["Object"].name)
		try:
			if inputs["Object"] is not None and inputs["Modifier"] is not None:
				output["Modifier"] = inputs["Object"].modifiers[inputs["Modifier"]]
		except (KeyError, SyntaxError, ValueError):
			pass
		allowCompiling()
		return output
