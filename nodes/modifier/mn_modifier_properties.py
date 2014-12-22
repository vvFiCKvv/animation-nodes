import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.mn_execution_unit_generator import getOutputValueVariable

class mn_ModifierPropertiesNode(Node, AnimationNode):
	"""A Class that extents an animation node witch represents a modifier of an object 
	and have the functionality to create input sockets for each property of the Modifier.
	
	Note: 
		Tho node may be linked to an object socket input.
	
	Attributes:
		bl_idname (str): Blender's id name is 'mn_ModifierNode'.
		bl_label (str): Blender's Label is 'Modifier Node'.
		node_category (str): This node is type of 'Modifier'.
		objectName (str): The name of blender Object witch this node is refer to.
		modifierSubClass (str): The subClass of blender Modifier witch this node is refer to.
		propertyName (str): The name of blender Modifier Property witch this node is refer to.
	"""
	bl_idname = "mn_ModifierPropertiesNode"
	bl_label = "Modifier Properties Node"
	node_category = "Modifier"
	modifierSubClass = bpy.props.StringProperty(update = nodePropertyChanged)
	def setPropertyName(self, value):
		self.addProperty(value)
	propertyName = bpy.props.StringProperty(update = nodePropertyChanged, default = "",  set=setPropertyName)

	socketIOType = [
		("INPUT", "Input", "", 1),
		("OUTPUT", "Output", "", 2),
		("BOTH", "Input and Output", "", 3),
		]
	propertyIOType = bpy.props.EnumProperty(items=socketIOType, default = 'BOTH')

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
			data = eval("bpy.types." + self.modifierSubClass + ".bl_rna")
#			layout = layout.box()
			layout.label("Add property:")
			layout.prop_search(self, "propertyName", data, "properties", icon="NONE", text = "")
			layout.prop(self,"propertyIOType" , text="")
		except (KeyError, SyntaxError, ValueError, AttributeError):
			pass
	def addProperty(self, propertyName):
		"""This function called when the name of the modifier property changes and is is responsible for enumerate the input - output sockets.
		
		Note:
			Clears the already existed socket's.
		
		Args:
			modifier (bpy.types.Modifier): The name of the correct modifier.
		"""
		socketType = getSocketTypeByDataPath("bpy.types." + self.modifierSubClass + ".bl_rna.properties['" + propertyName + "']")
#		if socketType:
#			print("Socket: ", socketType)
		forbidCompiling()
#TODO: import values from object properties
		#if propertyIOType is INPUT or BOTH add new input socket to the node
		if self.propertyIOType != 'OUTPUT' and socketType is not None:
			socket = self.inputs.new(socketType, propertyName)
			socket.removeable = True
			socket.callNodeToRemove = True
#TODO: use socket identifier instead of name and replace '_' from name with ' '
		#if propertyIOType is OUTPUT or BOTH add new output socket to the node
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
			if socket.name == "...":
				inputSocketNames["..."] = "EMPTYSOCKET"
			else:
				inputSocketNames[socket.identifier] = socket.identifier
		return inputSocketNames
	def getOutputSocketNames(self):
		outputSocketNames = {}
		for socket in self.outputs:
			if socket.name == "...":
				outputSocketNames["..."] = "EMPTYSOCKET"
			else:
				outputSocketNames[socket.identifier] = socket.identifier
		return outputSocketNames
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []		
		tabSpace = "    "
		thisNode = "bpy.data.node_groups['"  + self.id_data.name + "'].nodes['" + self.name + "']"
#		print("getInLineExecutionString called: ", thisNode)
		codeLines.append("if %Modifier% is None or %Modifier%.__class__.__name__ != " + thisNode + ".modifierSubClass:")
		codeLines.append(tabSpace + thisNode + ".modifierSubClass = %Modifier%.__class__.__name__")
		for inputSocket in self.inputs:
			if(inputSocket.identifier=="Modifier"):
				continue
			codeLines.append("try:")
			codeLines.append(tabSpace + "%Modifier%." + inputSocket.identifier + " = %"+ inputSocket.identifier + "%")
			codeLines.append("except (KeyError, SyntaxError, ValueError, AttributeError):")
			codeLines.append(tabSpace + "pass")
		for outputSocket in self.outputs:
			if(outputSocket.identifier=="Modifier" or not outputUse[outputSocket.identifier]):
				continue
			codeLines.append("try:")
			codeLines.append(tabSpace + "$"+ outputSocket.identifier + "$ = %Modifier%." + outputSocket.identifier)
			codeLines.append("except (KeyError, SyntaxError, ValueError, AttributeError):")
			codeLines.append(tabSpace + "print('Error', outputSocket.identifier)")
			codeLines.append(tabSpace + "$" + outputSocket.identifier + "$ = None")
			codeLines.append(tabSpace + "pass")
		if outputUse["Modifier"]:
			codeLines.append("$Modifier$ = %Modifier%")
#		print("\n".join(codeLines))
		return "\n".join(codeLines)
