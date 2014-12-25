import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ModifierCopyToObject(Node, AnimationNode):
	bl_idname = "mn_ModifierCopyToObject"
	bl_label = "Modifier Copy"
	node_category = "Modifier"
	
	modifierDataPath = bpy.props.StringProperty(update = nodePropertyChanged)
#TODO: fix this node ui and logic
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ModifierSocket", "Modifier").showName = False
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		return
	def initModifier(self,modifier):
		if modifier is not None:
			self.modifierDataPath =  self.inputs["Modifier"].getStoreableValue()
		return
	def execute(self,inputs):
		forbidCompiling()
		output = {}
		modifier = self.inputs["Modifier"].getValue()
		obj = inputs["Object"]
		if modifier is None or self.inputs["Modifier"].getStoreableValue() != self.modifierDataPath:
			self.initModifier(modifier)
		if obj is not None:
			newModifier = obj.modifiers.get(modifier.name, None)
			if not newModifier:
				newModifier = obj.modifiers.new(modifier.name, modifier.type)
			properties = [p.identifier for p in modifier.bl_rna.properties
                          if not p.is_readonly]
			for prop in properties:
				setattr(newModifier, prop, getattr(modifier, prop))
		allowCompiling()
		return output
