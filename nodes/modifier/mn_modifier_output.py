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
		bl_label (str): Blender's Label is 'Modifier Output'.
		node_category (str): This node is type of 'Modifier'.
		objectName (str): The name of blender Object witch this node is refer to.
		modifierSubClass (str): The sub Class type of blender Modifier witch this node is refer to.
		ignoreUnLinkedSockets (Bool): if it's True each unlinked input socket will get it's value from the modifier
	"""
	bl_idname = "mn_ModifierOutputNode"
	bl_label = "Modifier Output"
	node_category = "Modifier"
	
	modifierSubClass = bpy.props.StringProperty(update = nodePropertyChanged)
	ignoreUnLinkedSockets = bpy.props.BoolProperty(update = nodeTreeChanged)
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
		layout.prop(self, "ignoreUnLinkedSockets", text = "ignore unlinked")
		return
	def initModifier(self,modifier):
		"""Initialize the node socket's, one for each property of the modifier.
		
		Note:
			Clears the already existed socket's.
		
		Args:
			modifier (bpy.types.Modifier): The pointer to correct modifier.
		"""
#TODO: check for bugs
		# if modifier is None don't change the node socket's just ignore them.
		if modifier is None:
			return
		# removes each input property socket and corrects the object 
		# name and the modifier type of the node instance.
		for inputSocket in self.inputs:
			if(inputSocket.name=="Modifier"):
				continue
			print("remove item:", inputSocket)
			self.outputs.remove(inputSocket)
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
				if prop == "name":
					continue
				socketType = getSocketTypeByData(p)
				if socketType is not None:
					inputSocket = self.inputs.new(socketType, prop)
					inputSocket.removeable = True
					inputSocket.callNodeToRemove = True
					inputSocket.enabled = False
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
		# the node rna data path.
		thisNode = "bpy.data.node_groups['"  + self.id_data.name + "'].nodes['" + self.name + "']"
#		print("getInLineExecutionString called: ", thisNode)
		# if modifier type changes enumerate the node modifierSubClass attribute
		codeLines.append("if %Modifier% is None or %Modifier%.__class__.__name__ != " + thisNode + ".modifierSubClass:")
		codeLines.append(tabSpace + thisNode + ".initModifier(%Modifier%)")
		# for each input socket enumerate it's value
		for inputSocket in self.inputs:
			if(inputSocket.identifier=="Modifier"):
				continue
			codeLines.append("try:")
			# if a socket is just created(this code block will run once for each new input socket)
			if(inputSocket.enabled==False or (self.ignoreUnLinkedSockets and not inputSocket.is_linked)):
				# the socket rna data path.
				thisSocket = thisNode + ".inputs['" + inputSocket.identifier + "']"
				# load modifier property value to socket.
				codeLines.append(tabSpace + thisSocket + ".setStoreableValue(%Modifier%." + inputSocket.identifier + ")")
				# enable the socket.
				codeLines.append(tabSpace + thisSocket + ".enabled = True")
				# update node tree.
				codeLines.append(tabSpace + "nodeTreeChanged()")
			else:
				# update modifier property value according to socket input
				codeLines.append(tabSpace + "%Modifier%." + inputSocket.identifier + " = %"+ inputSocket.identifier + "%")
			codeLines.append("except (KeyError, SyntaxError, ValueError, AttributeError, NameError):")
#			codeLines.append(tabSpace + "print('Error: " + inputSocket.identifier + "')")
			codeLines.append(tabSpace + "pass")
		if outputUse["Modifier"]:
			codeLines.append("$Modifier$ = %Modifier%")
#		print("\n".join(codeLines))
		return "\n".join(codeLines)
