import bpy
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
	propertyName = bpy.props.StringProperty(update = nodePropertyChanged)
	isInput = bpy.props.BoolProperty(default = True)
	isOutput = bpy.props.BoolProperty(default = True)
	
	def selectSocket(self, dataPath):
		print(dataPath)
		try:
			dataType = eval("type(" + dataPath + ")")
		except:
			return None
		if(dataType is int):
			return "mn_IntegerSocket"
		if(dataType is float):
			return "mn_FloatSocket"
		if(dataType is bpy.types.Object):
			return "mn_ObjectSocket"
#		if(dataType is Vector):
#			return "mn_VectorSocket"
		if(dataType is str):
			return "mn_StringSocket"
		if(dataType is bool):
			return "mn_BooleanSocket"
		return "mn_GenericSocket"
	def init(self, context):
		"""Initialization of the node.
		
		Args:
			context:
		"""
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_StringSearchSocket", "Modifier").showName = True
		self.inputs.new("mn_StringSearchSocket", "Property").showName = True
		
		self.outputs.new("mn_ObjectSocket", "Object").showName = False
		self.outputs.new("mn_StringSearchSocket", "Modifier").showName = False
		allowCompiling()
	
	def draw_buttons(self, context, layout):
		layout.prop(self,"isInput", text="input")
		layout.prop(self,"isOutput", text="output")
		return
	def changeObject(self, objectName):
		"""This function called when the name of the object changes and is responsible for enumerate the input - output sockets.
		
		Args:
			object (bpy.types.Object): The name to correct object.
		"""
		self.inputs["Modifier"].searchPath = "bpy.context.scene.objects['" + objectName + "']"
		self.inputs["Modifier"].searchProperty = "modifiers"
		self.objectName = objectName
		return
	def changeModifier(self,modifierName):
		"""This function called when the name of the modifier changes and is is responsible for enumerate the input - output sockets.
		
		Note:
			Clears the already existed socket's.
		
		Args:
			modifier (bpy.types.Modifier): The name of the correct modifier.
		"""
		self.inputs["Property"].searchPath = "bpy.context.scene.objects['" + self.objectName + "'].modifiers['" + modifierName + "']" + ".bl_rna"
		self.inputs["Property"].searchProperty = "properties"
		self.modifierName = modifierName
		return
	def changeProperty(self,propertyName):
		"""This function called when the name of the modifier property changes and is is responsible for enumerate the input - output sockets.
		
		Note:
			Clears the already existed socket's.
		
		Args:
			modifier (bpy.types.Modifier): The name of the correct modifier.
		"""
		try:
			self.inputs.remove(self.inputs[self.propertyName])
		except KeyError:
			print("Key" + self.propertyName + "not found")
		try:
			self.outputs.remove(self.outputs[self.propertyName])
		except KeyError:
			print("Key" + self.propertyName + "not found")
		self.propertyName = propertyName
		dataPath = "bpy.context.scene.objects['" + self.objectName + "'].modifiers['" + self.modifierName + "']." + propertyName
		socketType = self.selectSocket(dataPath)
		if self.isInput and socketType is not None:
			self.inputs.new(socketType, propertyName)
		if self.isOutput and socketType is not None:
			self.outputs.new(socketType, propertyName)
		
		return
		
	def execute(self,inputs):
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
		if inputs["Modifier"] != self.modifierName:
			self.changeModifier(inputs["Modifier"])
		if inputs["Property"] != self.propertyName:
			self.changeProperty(inputs["Property"])
		for inputName in inputs:
			try:
				outputSocket = self.outputs[inputName]
			except KeyError:
				continue
			output[inputName] = inputs[inputName]
		dataPath = "bpy.context.scene.objects['" + self.objectName + "'].modifiers['" + self.modifierName + "']." + self.propertyName
		try:
			exec(dataPath + " = " + str(inputs[self.propertyName]))
		except:
			print("Error:", dataPath + " = " + str(inputs[self.propertyName]))
#TODO: Convert execute to getInLineExecutionString
		allowCompiling()
		return output
