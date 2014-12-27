import bpy
from types import MethodType
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *


class mn_ParticleSystemNode(Node, AnimationNode):
	"""A Class that extents an animation node witch represents a Particle System
	and have the functionality to create input sockets for each property of the Modifier.
	
	Attributes:
		bl_idname (str): Blender's id name is 'mn_ParticleSystemNode'.
		bl_label (str): Blender's Label is 'Particle Node'.
		node_category (str): This node is type of 'Modifier'.
	"""
	bl_idname = "mn_ParticleSystemNode"
	bl_label = "Particle Node"
	node_category = "Particle"
	particleName = bpy.props.StringProperty()
	def setUseCustomName(self, value):
		try:
			if value == True:
				self.inputs["Particle"].enabled = True
				self.inputs["Particle"].setStoreableValue(self.particleName)
			else:
				self.inputs["Particle"].enabled = False
				self.particleName = self.inputs["Particle"].getStoreableValue()
		except (KeyError, SyntaxError, ValueError, AttributeError):
			pass
	def getUseCustomName(self):
		try:
			return self.inputs["Particle"].enabled
		except (KeyError, SyntaxError, ValueError, AttributeError):
			return False
	# using update = nodeTreeChanged to update execution strings.
	useCustomName = bpy.props.BoolProperty(set = setUseCustomName, get = getUseCustomName, update = nodeTreeChanged)
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
	
	def init(self, context):
		"""Initialization of the node.
		
		Args:
			context:
		"""
		forbidCompiling()
		socket = self.inputs.new("mn_StringSocket", "Particle")
		socket.showName = False
		self.useCustomName = False
		self.outputs.new("mn_StringSocket", "Particle").showName = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "useCustomName", text="Custom Name")
		if self.useCustomName == False :
			try:
				data =  eval("bpy.data")
				layout.prop_search(self, "particleName", data, "particles", icon="NONE", text = "")
			except (KeyError, SyntaxError, ValueError, AttributeError):
				pass
		try:
			data = eval("bpy.data.particles['" + self.particleName + "'].bl_rna")
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
		socketType = getSocketTypeByDataPath("bpy.data.particles['" + self.particleName + "'].bl_rna.properties['" + propertyName + "']")
#		print("Socket: ", socketType)
		forbidCompiling()
		# if propertyIOType is INPUT or BOTH add new input socket to the node
		if self.propertyIOType != 'OUTPUT' and socketType is not None:
			try:
				# Search for existing socket with the same name so no duplicates exists
				socket = self.inputs[propertyName]
			except KeyError:
				socket = self.inputs.new(socketType, propertyName)
			socket.removeable = True
			socket.callNodeToRemove = True
			socket.enabled = False
#TODO: replace '_' from name with ' '
		# if propertyIOType is OUTPUT or BOTH add new output socket to the node
		if self.propertyIOType != 'INPUT' and socketType is not None:
			try:
				# Search for existing socket with the same name so no duplicates exists
				socket = self.outputs[propertyName]
			except KeyError:
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
		thisNode = "bpy.data.node_groups['"  + self.id_data.name + "'].nodes['" + self.name + "']"
		codeLines.append("if " + thisNode + ".useCustomName and %Particle% != " + thisNode + ".particleName:")
		codeLines.append(tabSpace + thisNode + ".particleName = %Particle%")
		#enumerate particle output
		if outputUse["Particle"]:
			codeLines.append("$Particle$ = " + thisNode + ".particleName")
		# for each input socket enumerate it's value
		for inputSocket in self.inputs:
			if(inputSocket.identifier=="Particle"):
				continue
			codeLines.append("try:")
			#the path of shape key value
			valuePAth = "bpy.data.particles['" + self.particleName + "']." + inputSocket.identifier
			# if a socket is just created(this code block will run once for each new input socket)
			if(inputSocket.enabled==False):
				# the socket rna data path.
				thisSocket = thisNode + ".inputs['" + inputSocket.identifier + "']"
				# load modifier property value to socket.
				codeLines.append(tabSpace + thisSocket + ".setStoreableValue(" + valuePAth + ")")
				# enable the socket.
				codeLines.append(tabSpace + thisSocket + ".enabled = True")
				# update node tree.
				codeLines.append(tabSpace + "nodeTreeChanged()")
			else:
				# update modifier property value according to socket input
				codeLines.append(tabSpace + valuePAth + " = %" + inputSocket.identifier + "%")
			codeLines.append("except (KeyError, SyntaxError, ValueError, AttributeError, NameError):")
#			codeLines.append(tabSpace + "print('Error: " + inputSocket.identifier + "')")
			codeLines.append(tabSpace + "pass")
		# for each output socket witch is linked enumerate it's value
		for outputSocket in self.outputs:
			if(outputSocket.identifier=="Particle" or not outputUse[outputSocket.identifier]):
				continue
			codeLines.append("try:")
			valuePAth = "bpy.data.particles['" + self.particleName + "']." + inputSocket.identifier
			codeLines.append(tabSpace + "$"+ outputSocket.identifier + "$ =" + valuePAth)
			codeLines.append("except (KeyError, SyntaxError, ValueError, AttributeError, NameError):")
#			codeLines.append(tabSpace + "print('Error: " + outputSocket.identifier + "')")
			codeLines.append(tabSpace + "$" + outputSocket.identifier + "$ = None")
			codeLines.append(tabSpace + "pass")
#		print("\n".join(codeLines))
		return "\n".join(codeLines)
