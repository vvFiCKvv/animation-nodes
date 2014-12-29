import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.mn_execution_unit_generator import getOutputValueVariable

options = [ ("useFocal_Length", "Focal_Length"),
			("useDistance", "Distance"),
			("useAperture", "Aperture"),
			("useShutter_Speed", "Shutter_Speed"),
			("useExposure", "Exposure") ]

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
	
	def usePropertyChanged(self, context):
		self.setHideProperty()
		nodeTreeChanged()
	
	useFocal_Length = bpy.props.BoolProperty(update = usePropertyChanged, default = False)
	useAperture = bpy.props.BoolProperty(update = usePropertyChanged, default = False)
	useShutter_Speed = bpy.props.BoolProperty(update = usePropertyChanged, default = False)
	useExposure = bpy.props.BoolProperty(update = usePropertyChanged, default = False)
	useDistance = bpy.props.BoolProperty(update = usePropertyChanged, default = False)
	
#convert socket label from  "_" to " "
	def init(self, context):
		"""Initialization of the node.
		
		Args:
			context:
		"""
		forbidCompiling()
		socket = self.inputs.new("mn_ObjectSocket", "Camera")
		socket.showName = True
		self.outputs.new("mn_ObjectSocket", "Camera").showName = True
		
		socket = self.inputs.new("mn_FloatSocket", "Focal_Length")
		self.inputs.new("mn_FloatSocket", "Distance")
#TODO: This is only for cycles
		self.inputs.new("mn_FloatSocket", "Aperture")
		self.inputs.new("mn_FloatSocket", "Shutter_Speed")
		self.inputs.new("mn_FloatSocket", "Exposure")
		self.setHideProperty()
		allowCompiling()
	def draw_buttons(self, context, layout):
		pass
	def draw_buttons(self, context, layout):
		col = layout.column(align = True)
		
		for i, option in enumerate(options[:2]):
			col.prop(self, option[0], text = option[1])
			
	def draw_buttons_ext(self, context, layout):
		col = layout.column(align = True)
		
		for i, option in enumerate(options):
			if i in [2, 5]: col.separator(); col.separator()
			col.prop(self, option[0], text = option[1])
		
	def setHideProperty(self):
		for option in options:
			self.inputs[option[1]].hide = not getattr(self, option[0])
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
		codeLines.append("if %Camera% is not None and %Camera%.type == 'CAMERA':")
		if self.useFocal_Length:
			codeLines.append(tabSpace + "bpy.data.cameras[%Camera%.name].lens = %Focal_Length%")
			
		if self.useAperture:
			codeLines.append(tabSpace + "try:")
			codeLines.append(tabSpace + tabSpace + "bpy.data.cameras[%Camera%.name].cycles.aperture_size = %Aperture%")
			codeLines.append(tabSpace + "except(KeyError, SyntaxError, ValueError, AttributeError):")
			codeLines.append(tabSpace + tabSpace + "pass")
		if self.useShutter_Speed:
			codeLines.append(tabSpace + "try:")
			codeLines.append(tabSpace + tabSpace + "if %Camera%.name == bpy.context.scene.camera.name:")
			codeLines.append(tabSpace + tabSpace + tabSpace + "bpy.context.scene.render.motion_blur_shutter = %Shutter_Speed%")
			codeLines.append(tabSpace + "except(KeyError, SyntaxError, ValueError, AttributeError):")
			codeLines.append(tabSpace + tabSpace + "pass")
		if self.useExposure:
			codeLines.append(tabSpace + "try:")
			codeLines.append(tabSpace + tabSpace + "if %Camera%.name == bpy.context.scene.camera.name:")
			codeLines.append(tabSpace + tabSpace + tabSpace + "bpy.context.scene.cycles.film_exposure = %Exposure%")
			codeLines.append(tabSpace + "except(KeyError, SyntaxError, ValueError, AttributeError):")
			codeLines.append(tabSpace + tabSpace + "pass")
		if self.useDistance:
			codeLines.append(tabSpace + "try:")
			codeLines.append(tabSpace + tabSpace + "bpy.data.cameras[%Camera%.name].dof_distance = %Distance%")
			codeLines.append(tabSpace + "except(KeyError, SyntaxError, ValueError, AttributeError):")
			codeLines.append(tabSpace + tabSpace + "pass")
		codeLines.append(tabSpace +"pass")
		codeLines.append("$Camera$ = %Camera%")
		print("\n".join(codeLines))
		return "\n".join(codeLines)
