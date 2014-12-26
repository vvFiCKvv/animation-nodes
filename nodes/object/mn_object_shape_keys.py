import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.mn_execution_unit_generator import getOutputValueVariable

class mn_ObjectShapeKeysNode(Node, AnimationNode):
	"""A Class that extents an animation node witch represents a shape keys of an object and it's properties
	and have the functionality to dynamically create input add/or output sockets of shape keys properties.
	
	Attributes:
		bl_idname (str): Blender's id name is 'mn_ObjectShapeKeysNode'.
		bl_label (str): Blender's Label is 'Object Shape keys'.
		node_category (str): This node is type of 'Object'.
		shapeKeys (str):  The object shape key array witch this node is refer to.
		propertyName (str): The name of Shape key Property to add.
		propertyIOType (enum) The place to put a new socket 'INPUT' or 'OUTPUT' or 'BOTH'
	"""
	bl_idname = "mn_ObjectShapeKeysNode"
	bl_label = "Object Shape keys"
	node_category = "Object"
	shapeKeys = bpy.props.StringProperty(update = nodePropertyChanged)
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
#TODO: check when needs update tree node
	def init(self, context):
		"""Initialization of the node.
		
		Args:
			context:
		"""
		forbidCompiling()
		socket = self.inputs.new("mn_ObjectSocket", "Object")
		socket.showName = False
		socket = self.outputs.new("mn_ObjectSocket", "Object")
		allowCompiling()
	
	def draw_buttons(self, context, layout):
		try:
			#add's a dropbox with a entry foreach shape key property
			data = eval(self.shapeKeys)
#			layout = layout.box()
			layout.label("Add property:")
			layout.prop_search(self, "propertyName", data, "key_blocks", icon="NONE", text = "")
			#add selection for enum propertyIOType attribute
			layout.prop(self,"propertyIOType" , text="")
		except (KeyError, SyntaxError, ValueError, AttributeError):
			pass
	def addProperty(self, propertyName):
		"""This function called to add a shape key socket as input/output or both according to propertyIOType attribute of the node.
		
		Note:
			The new node socket has enabled attribute False, so execution string load it's proper value and enable it.
		
		Args:
			propertyName (str): The name of the property.
		"""
#TODO: clear ' ' name of socket
		forbidCompiling()
		# if propertyIOType is INPUT or BOTH add new input socket to the node
		if self.propertyIOType != 'OUTPUT':
			socket = self.inputs.new("mn_FloatSocket", propertyName)
			socket.removeable = True
			socket.callNodeToRemove = True
			socket.enabled = False
		# if propertyIOType is OUTPUT or BOTH add new output socket to the node
		if self.propertyIOType != 'INPUT':
			socket = self.outputs.new("mn_FloatSocket", propertyName)
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
			inputSocketNames[socket.identifier] = socket.identifier.replace(" ", "_")
		return inputSocketNames
	def getOutputSocketNames(self):
		outputSocketNames = {}
		for socket in self.outputs:
			outputSocketNames[socket.identifier] = socket.identifier.replace(" ", "_")
		return outputSocketNames
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		tabSpace = "    "
		# the node rna data path.
		thisNode = "bpy.data.node_groups['"  + self.id_data.name + "'].nodes['" + self.name + "']"
#		print("getInLineExecutionString called: ", thisNode)
		#  enumerate the node shapeKeys attribute
		codeLines.append("if %Object% is not None and %Object%.active_shape_key is not None:")
		codeLines.append(tabSpace + thisNode + ".shapeKeys = " + "\"bpy.data.shape_keys['\" + " + "%Object%.active_shape_key.id_data.name + \"']\"")
		# for each input socket enumerate it's value
		for inputSocket in self.inputs:
			if(inputSocket.identifier=="Object"):
				continue
			codeLines.append("try:")
			# if a socket is just created(this code block will run once for each new input socket)
			if(inputSocket.enabled==False):
				# the socket rna data path.
				thisSocket = thisNode + ".inputs['" + inputSocket.identifier + "']"
				# load shape key property value to socket.
				codeLines.append(tabSpace + thisSocket + ".setStoreableValue(" + self.shapeKeys + ".key_blocks['" + inputSocket.identifier + "'].value)")
#TODO: set min, max for inputsocket according to shape key
				# enable the socket.
				codeLines.append(tabSpace + thisSocket + ".enabled = True")
				# update node tree.
				codeLines.append(tabSpace + "nodeTreeChanged()")
			else:
				# update shape key property value according to socket input
				codeLines.append(tabSpace + self.shapeKeys + ".key_blocks['" + inputSocket.identifier + "'].value = %"+ inputSocket.identifier.replace(" ", "_") + "%")
			codeLines.append("except (KeyError, SyntaxError, ValueError, AttributeError, NameError):")
#			codeLines.append(tabSpace + "print('Error: " + inputSocket.identifier + "')")
			codeLines.append(tabSpace + "pass")
		# for each output socket witch is linked enumerate it's value
		for outputSocket in self.outputs:
			if(outputSocket.identifier=="Object" or not outputUse[outputSocket.identifier]):
				continue
			codeLines.append("try:")
			codeLines.append(tabSpace + "$"+ outputSocket.identifier.replace(" ", "_") + "$ =" + self.shapeKeys + ".key_blocks['" + outputSocket.identifier + "'].value")
			codeLines.append("except (KeyError, SyntaxError, ValueError, AttributeError, NameError):")
#			codeLines.append(tabSpace + "print('Error: " + outputSocket.identifier + "')")
			codeLines.append(tabSpace + "$" + outputSocket.identifier.replace(" ", "_") + "$ = None")
			codeLines.append(tabSpace + "pass")
		# enumerate object output socket
		if outputUse["Object"]:
			codeLines.append("$Object$ = %Object%")
		print("\n".join(codeLines))
		return "\n".join(codeLines)
