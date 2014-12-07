import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ObjectModifiersNode(Node, AnimationNode):
	bl_idname = "mn_ObjectModifiersNode"
	bl_label = "Object Modifier List Node"
	node_category = "Modifier"
	
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		return
		
	def initModifier(self,object):
		self.objectName = object.name 
		for outputSocket in self.outputs:
			print("remove item:", outputSocket)
			self.outputs.remove(outputSocket)
		objName = self.inputs["Object"].getStoreableValue()
		for modifier in object.modifiers:
			outputSocket = self.outputs.new("mn_ModifierSocket", modifier.name)
			outputSocket.objectName = objName
			outputSocket.modifierName = modifier.name
		return
		
	def execute(self,inputs):
		forbidCompiling()
		output = {}
		obj = self.inputs["Object"].getValue()
		if obj and (obj.name != self.objectName):
			self.initModifier(obj)
		for outputSocket in self.outputs:
			if outputSocket.dataType  == "Modifier":
				outputValue =  outputSocket.getValue()
				if outputValue is None:
					print("Modifier: ", outputSocket , " name changed")
					self.initModifier(obj)
				output[outputSocket.modifierName] = outputValue
		allowCompiling()
		return output
