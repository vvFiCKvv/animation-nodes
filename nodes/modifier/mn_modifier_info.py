import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ModifierInfoNode(Node, AnimationNode):
	"""A Class that extents an animation node witch represents a modifier of an object 
	and have the functionality to create output sockets for each property of the Modifier.
	
	Note: 
		Tho node may be linked to an object socket input.
	
	Attributes:
		bl_idname (str): Blender's id name is 'mn_ModifierInfoNode'.
		bl_label (str): Blender's Label is 'Modifier Info Node'.
		node_category (str): This node is type of 'Modifier'.
		modifierSubClass (str): The sub Class type of blender Modifier witch this node is refer to.
	"""
	bl_idname = "mn_ModifierInfoNode"
	bl_label = "Modifier Info Node"
	node_category = "Modifier"
	
	modifierSubClass = bpy.props.StringProperty(update = nodePropertyChanged)
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
#TODO: add automatic - manual refresh icon is FILE_REFRESH
		return
		
	def initModifier(self,modifier):
		"""Initialize the node socket's, one for each property of the modifier.
		
		Note:
			Clears the already existed socket's.
		
		Args:
			modifier (bpy.types.Modifier): The pointer to correct modifier.
		"""
#TODO: check for bugs and correct link values or hide them or something.
		#if modifier is None don't change the node socket's just ignore them.
		if modifier is None:
			return
		# removes each input property socket and corrects the object 
		# name and the modifier type of the node instance.
		for outputSocket in self.outputs:
			if(outputSocket.name=="Modifier"):
				continue
			print("remove item:", outputSocket)
			self.outputs.remove(outputSocket)
		if modifier is None:
			self.modifierSubClass = ""
			return
		else:
			self.modifierSubClass = modifier.__class__.__name__
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
				socketType = getSocketTypeByData(p)
				if socketType is not None:
					outputSocket = self.outputs.new(socketType, prop)
					outputSocket.removeable = True
					outputSocket.callNodeToRemove = True
		return
	def removeSocket(self, socket):
		if socket.is_output:
			self.outputs.remove(socket)
		else:
			self.inputs.remove(socket)
	def getInputSocketNames(self):
		inputSocketNames = {}
		for socket in self.inputs:
			inputSocketNames[socket.identifier] = socket.identifier
		return inputSocketNames
	def getOutputSocketNames(self):
		outputSocketNames = {}
		for socket in self.outputs:
			outputSocketNames[socket.identifier] = socket.identifier
		return outputSocketNames
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		tabSpace = "    "
		#the node rna data path.
		thisNode = "bpy.data.node_groups['"  + self.id_data.name + "'].nodes['" + self.name + "']"
#		print("getInLineExecutionString called: ", thisNode)
		#if modifier type changes enumerate the node modifierSubClass attribute
		codeLines.append("if %Modifier% is None or %Modifier%.__class__.__name__ != " + thisNode + ".modifierSubClass:")
		codeLines.append(tabSpace + thisNode + ".initModifier(%Modifier%)")
		#for each output socket witch is linked enumerate it's value
		for outputSocket in self.outputs:
			if(outputSocket.name=="Modifier" or not outputUse[outputSocket.identifier]):
				continue
			codeLines.append("try:")
			codeLines.append(tabSpace + "$"+ outputSocket.identifier + "$ = %Modifier%." + outputSocket.identifier)
			codeLines.append("except (KeyError, SyntaxError, ValueError, AttributeError, NameError):")
#			codeLines.append(tabSpace + "print('Error: " + outputSocket.identifier + "')")
			codeLines.append(tabSpace + "$" + outputSocket.identifier + "$ = None")
			codeLines.append(tabSpace + "pass")
		if outputUse["Modifier"]:
			codeLines.append("$Modifier$ = %Modifier%")
#		print("\n".join(codeLines))
		return "\n".join(codeLines)
