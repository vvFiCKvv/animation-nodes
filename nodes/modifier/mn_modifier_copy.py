import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ModifierCopyToObject(Node, AnimationNode):
	bl_idname = "mn_ModifierCopyToObject"
	bl_label = "Modifier Copy"
	node_category = "Modifier"
	
#TODO: fix this node ui
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ModifierSocket", "From")
		self.inputs.new("mn_ObjectSocket", "To")
		allowCompiling()
	def draw_buttons(self, context, layout):
		return
	def getInputSocketNames(self):
		return {"To" : "object",
				"From" : "modifier"}
	def getOutputSocketNames(self):
		return {}
	def execute(self,object, modifier):
		forbidCompiling()
		output = {}
		if object is not None and modifier is not None:
			newModifier = object.modifiers.get(modifier.name, None)
			if not newModifier:
				newModifier = object.modifiers.new(modifier.name, modifier.type)
			properties = [p.identifier for p in modifier.bl_rna.properties
						  if not p.is_readonly]
			for prop in properties:
				setattr(newModifier, prop, getattr(modifier, prop))
		allowCompiling()
		return output
