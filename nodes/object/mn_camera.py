import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.mn_execution_unit_generator import getOutputValueVariable

class mn_CameraNode(Node, AnimationNode):
	"""A Class that extents an animation node witch represents a camera and it's properties
	
	Attributes:
		bl_idname (str): Blender's id name is 'mn_CameraNode'.
		bl_label (str): Blender's Label is 'Camera'.
		node_category (str): This node is type of 'Object'.
		shapeKeys (str):  The object shape key array witch this node is refer to.
		cameraName (str): The name of Camera this node refers to.
		propertyIOType (enum) The place to put a new socket 'INPUT' or 'OUTPUT' or 'BOTH'
	"""
	bl_idname = "mn_CameraNode"
	bl_label = "Camera"
	node_category = "Object"
	cameraName = bpy.props.StringProperty()
	def setUseCustomName(self, value):
		try:
			if value == True:
				self.inputs["Camera"].enabled = True
				self.inputs["Camera"].setStoreableValue(self.cameraName)
			else:
				self.inputs["Camera"].enabled = False
				self.cameraName = self.inputs["Camera"].getStoreableValue()
		except (KeyError, SyntaxError, ValueError, AttributeError):
			pass
	def getUseCustomName(self):
		try:
			return self.inputs["Camera"].enabled
		except (KeyError, SyntaxError, ValueError, AttributeError):
			return False
	# using update = nodeTreeChanged to update execution strings.
	useCustomName = bpy.props.BoolProperty(set = setUseCustomName, get = getUseCustomName, update = nodeTreeChanged)
	# enum witch define the type of a socket input/output or both
	socketIOType = [
		("INPUT", "Input", "", 1),
		("OUTPUT", "Output", "", 2),
#		("BOTH", "Input and Output", "", 3),
		]
	def updatePropertyIOType(self, context):
		for socket in self.inputs:
			if socket.identifier == "Camera":
				continue
			socket.enabled = (self.propertyIOType != "OUTPUT" and eval("self.use" + socket.identifier))
		for socket in self.outputs:
			if socket.identifier == "Camera":
				continue
			socket.enabled = (self.propertyIOType != "INPUT"  and eval("self.use" + socket.identifier))
		nodeTreeChanged()
	propertyIOType = bpy.props.EnumProperty(items=socketIOType, default = 'INPUT', update = updatePropertyIOType)

	useFocal_Length = bpy.props.BoolProperty(update = updatePropertyIOType, default = False)
	useAperture = bpy.props.BoolProperty(update = updatePropertyIOType, default = False)
	useShutter_Speed = bpy.props.BoolProperty(update = updatePropertyIOType, default = False)
	useExposure = bpy.props.BoolProperty(update = updatePropertyIOType, default = False)
#	useFocus = bpy.props.BoolProperty(update = updatePropertyIOType, default = False)
	useDistance = bpy.props.BoolProperty(update = updatePropertyIOType, default = False)
	
#convert socket label from  "_" to " "
	def init(self, context):
		"""Initialization of the node.
		
		Args:
			context:
		"""
		forbidCompiling()
		socket = self.inputs.new("mn_StringSocket", "Camera")
		socket.showName = False
		self.useCustomName = False
		self.outputs.new("mn_ObjectSocket", "Camera").showName = False
		
		socket = self.inputs.new("mn_FloatSocket", "Focal_Length")
#TODO: This is only for cycles
		self.inputs.new("mn_FloatSocket", "Aperture")
		self.inputs.new("mn_FloatSocket", "Shutter_Speed")
		self.inputs.new("mn_FloatSocket", "Exposure")
#		self.inputs.new("mn_ObjectSocket", "Focus")
		self.inputs.new("mn_FloatSocket", "Distance")
		
		self.outputs.new("mn_FloatSocket", "Focal_Length")
#TODO: This is only for cycles
		self.outputs.new("mn_FloatSocket", "Aperture")
		self.outputs.new("mn_FloatSocket", "Shutter_Speed")
		self.outputs.new("mn_FloatSocket", "Exposure")
#		self.outputs.new("mn_ObjectSocket", "Focus")
		self.outputs.new("mn_FloatSocket", "Distance")
		
		for socket in self.inputs:
			if socket.identifier == "Camera":
				continue
			socket.removeable = True
			socket.callNodeToRemove = True
		for socket in self.outputs:
			if socket.identifier == "Camera":
				continue
			socket.removeable = True
			socket.callNodeToRemove = True
		self.propertyIOType = "INPUT"
		allowCompiling()
	
	def draw_buttons(self, context, layout):
		layout.prop(self, "useCustomName", text="Custom Name")
		if self.useCustomName == False :
			try:
				data =  eval("bpy.data")
				layout.prop_search(self, "cameraName", data, "cameras", icon="NONE", text = "")
			except (KeyError, SyntaxError, ValueError, AttributeError):
				pass
			#add selection for enum propertyIOType attribute
			layout.prop(self,"propertyIOType" , text="")
			
			if not self.useFocal_Length:
				layout.prop(self, "useFocal_Length", text="Focal Length")
			if not self.useAperture:
				layout.prop(self, "useAperture", text="Aperture")
			if not self.useShutter_Speed:
				layout.prop(self, "useShutter_Speed", text="Shutter Speed")
			if not self.useExposure:
				layout.prop(self, "useExposure", text="Exposure")
#			if not self.useFocus:
#				layout.prop(self, "useFocus", text="Focus")
			if not self.useDistance:
				layout.prop(self, "useDistance", text="Distance")
	def removeSocket(self, socket):
		setattr(self, "use" + socket.identifier, False)
		socket.enabled = False
#TODO: convert to static socket names
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
#		print("\n".join(codeLines))
		return "\n".join(codeLines)
