import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ModifierOutputNode(Node, AnimationNode):
	"""A Class that extents an animation node witch represents a modifier of an object 
	and have the functionality to create input sockets for each property of the Modifier.
	
	Note: 
		Tho node may be linked to an object socket input.
	
	Attributes:
		bl_idname (str): Blender's id name is 'mn_ModifierOutputNode'.
		bl_label (str): Blender's Label is 'Modifier Output Node'.
		node_category (str): This node is type of 'Modifier'.
		objectName (str): The name of blender Object witch this node is refer to.
		modifierType (str): The type of blender Modifier witch this node is refer to.
	"""
	bl_idname = "mn_ModifierOutputNode"
	bl_label = "Modifier Output Node"
	node_category = "Modifier"
	
	modifierType = bpy.props.StringProperty(update = nodePropertyChanged)
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)

	def init(self, context):
		"""Initialization of the node.
		
		Args:
			context:
		"""
		forbidCompiling()
		self.inputs.new("mn_ModifierSocket", "Modifier").showName = False
		self.outputs.new("mn_ModifierSocket", "Modifier").showName = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		return
	def changeObject(self, modifier):
		"""This function called when the name of the object changes and is responsible for enumerate the input sockets.
		
		Args:
			modifier (bpy.types.Modifier): The pointer to correct modifier.
		"""
		# enumerate the name of the object
		self.objectName = modifier.id_data.name
#		print("Modifier Change Object To:", self.objectName)
		#get the path to the modifier
		modifierDataPath = self.inputs["Modifier"].getStoreableValue()
		# for each property socket correct their data path.
		for inputSocket in self.inputs:
			if(inputSocket.name=="Modifier"):
				continue
			inputSocket.dataPath = modifierDataPath
		return
	
	def initModifier(self,modifier):
		"""Initialize the node socket's, one for each property of the modifier.
		
		Note:
			Clears the already existed socket's.
		
		Args:
			modifier (bpy.types.Modifier): The pointer to correct modifier.
		"""
		# removes each input property socket and corrects the object 
		# name and the modifier type of the node instance.
		for inputSocket in self.inputs:
			if(inputSocket.name=="Modifier"):
				continue
			print("remove item:", inputSocket)
			self.inputs.remove(inputSocket)
		if modifier is None:
			self.modifierType = ""
			self.objectName = ""
			return
		else:
			self.modifierType = modifier.type
			self.objectName = modifier.id_data.name
		# get the path to the modifier
		modifierDataPath = self.inputs["Modifier"].getStoreableValue()
		print("Modifier changes To: ", modifierDataPath)
		# for each property of the modifier(except the uselless ones)
		# create a input socket with the correct datapath.
		for p in modifier.bl_rna.properties:
				if p.is_readonly:
					continue
				prop = p.identifier
				if prop[0:5] == "show_":
					continue
				if prop[0:10] == "use_apply_":
					continue
				inputSocket = self.inputs.new("mn_PropertySocket", prop)
				inputSocket.dataPath = modifierDataPath
				inputSocket.name = prop
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
		# try to set the input socket of the modifier to the correct modifier.
		self.inputs["Modifier"].setStoreableValue(inputs["Modifier"])
		# get back the modifier from the socket or None if the input socket is linked to an Object.
		modifier = self.inputs["Modifier"].getValue()
		# if modifier type change then call initModifier to re-create the correct socket inputs
		if modifier is None or modifier.type != self.modifierType:
			self.initModifier(modifier)
		# if only the object name changes then re-point the existing sockets to the correct properties.
		else:
			if modifier.id_data.name != self.objectName:
				self.changeObject(modifier)
		
		# update values of the linked input sockets
		for input in inputs:
			if(isSocketLinked(self.inputs[input]) and input != "Modifier"):
#				print("input: ", self.inputs[input], "new input: ", str(inputs[input]))
				self.inputs[input].setStoreableValue(inputs[input])
		allowCompiling()
		# set the correct output of the node.
		output["Modifier"] =  inputs["Modifier"]
		return output
