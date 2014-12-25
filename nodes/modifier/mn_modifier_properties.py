import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.mn_execution_unit_generator import getOutputValueVariable

class mn_ModifierPropertiesNode(Node, AnimationNode):
	"""A Class that extents an animation node witch represents a modifier and it's properties
	and have the functionality to dynamically create input add/or output sockets of Modifier properties.
	
	Attributes:
		bl_idname (str): Blender's id name is 'mn_ModifierNode'.
		bl_label (str): Blender's Label is 'Modifier Properties'.
		node_category (str): This node is type of 'Modifier'.
		modifierSubClass (str):  The sub Class type of blender Modifier witch this node is refer to.
		propertyName (str): The name of blender Modifier Property witch this node is refer to.
		propertyIOType (enum) The place to put a new socket 'INPUT' or 'OUTPUT' or 'BOTH'
	"""
	bl_idname = "mn_ModifierPropertiesNode"
	bl_label = "Modifier Properties"
	node_category = "Modifier"
	modifierSubClass = bpy.props.StringProperty(update = nodePropertyChanged)
	def setPropertyName(self, value):
		self.addProperty(value)
	# doesn't need update = nodePropertyChanged because function addProperty calls nodeTreeChanged
	propertyName = bpy.props.StringProperty(default = "",  set=setPropertyName)
	# enum witch define the type of a socket input/output or both
	socketIOType = [
		("INPUT", "Input", "", 1),
		("OUTPUT", "Output", "", 2),
		("BOTH", "Input and Output", "", 3),
		]
	propertyIOType = bpy.props.EnumProperty(items=socketIOType, default = 'BOTH')
#TODO: fix crashing bug
#TODO: check when needs update tree node
	def init(self, context):
		"""Initialization of the node.
		
		Args:
			context:
		"""
		forbidCompiling()
		socket = self.inputs.new("mn_ModifierSocket", "Modifier")
		socket.showName = True
		socket = self.outputs.new("mn_ModifierSocket", "Modifier")
		allowCompiling()
	
	def draw_buttons(self, context, layout):
		socket = self.outputs["Modifier"]
		try:
			#add's a dropbox with a entry foreach modifier property
			data = eval("bpy.types." + self.modifierSubClass + ".bl_rna")
#			layout = layout.box()
			layout.label("Add property:")
			layout.prop_search(self, "propertyName", data, "properties", icon="NONE", text = "")
			#add selection for enum propertyIOType attribute
			layout.prop(self,"propertyIOType" , text="")
		except (KeyError, SyntaxError, ValueError, AttributeError):
			pass
	def addProperty(self, propertyName):
		"""This function called to add a modifier property socket as input/output or both according to propertyIOType attribute of the node.
		
		Note:
			The new node socket has enabled attribute False, so execution string load it's proper value and enable it.
			Needs modifierSubClass attribute of node to determine the type of the socket.
		
		Args:
			propertyName (str): The name of the property.
		"""
		socketType = getSocketTypeByDataPath("bpy.types." + self.modifierSubClass + ".bl_rna.properties['" + propertyName + "']")
#		print("Socket: ", socketType)
		forbidCompiling()
		# if propertyIOType is INPUT or BOTH add new input socket to the node
		if self.propertyIOType != 'OUTPUT' and socketType is not None:
			socket = self.inputs.new(socketType, propertyName)
			socket.removeable = True
			socket.callNodeToRemove = True
			socket.enabled = False
#TODO: use socket identifier instead of name and replace '_' from name with ' '
		# if propertyIOType is OUTPUT or BOTH add new output socket to the node
		if self.propertyIOType != 'INPUT' and socketType is not None:
			socket = self.outputs.new(socketType, propertyName)
			socket.removeable = True
			socket.callNodeToRemove = True
		allowCompiling()
		nodeTreeChanged()
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
		codeLines.append(tabSpace + thisNode + ".modifierSubClass = %Modifier%.__class__.__name__")
		# for each input socket enumerate it's value
		for inputSocket in self.inputs:
			if(inputSocket.identifier=="Modifier"):
				continue
			codeLines.append("try:")
			# if a socket is just created(this code block will run once for each new input socket)
			if(inputSocket.enabled==False):
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
		# for each output socket witch is linked enumerate it's value
		for outputSocket in self.outputs:
			if(outputSocket.identifier=="Modifier" or not outputUse[outputSocket.identifier]):
				continue
			codeLines.append("try:")
			codeLines.append(tabSpace + "$"+ outputSocket.identifier + "$ = %Modifier%." + outputSocket.identifier)
			codeLines.append("except (KeyError, SyntaxError, ValueError, AttributeError, NameError):")
#			codeLines.append(tabSpace + "print('Error: " + outputSocket.identifier + "')")
			codeLines.append(tabSpace + "$" + outputSocket.identifier + "$ = None")
			codeLines.append(tabSpace + "pass")
		# enumerate modifier output socket
		if outputUse["Modifier"]:
			codeLines.append("$Modifier$ = %Modifier%")
#		print("\n".join(codeLines))
		return "\n".join(codeLines)
