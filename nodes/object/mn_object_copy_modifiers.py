import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ObjectCopyModifiers(Node, AnimationNode):
	bl_idname = "mn_ObjectCopyModifiers"
	bl_label = "Copy Modifiers from Object to Object Node"
#	node_category = "Object"
	copyProperties = bpy.props.BoolProperty(default = False, update = nodePropertyChanged)
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "ObjectFrom").showName = False
		self.inputs.new("mn_ObjectSocket", "ObjectTo").showName = False
		self.copyProperties = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "copyProperties", text = "Copy Properties")
		return
	def execute(self,inputs):
		output = {}
		objFrom = inputs["ObjectFrom"]
		objTo = inputs["ObjectTo"]
		if objFrom is None or objTo is None:
			return output
		forbidCompiling()
		index = 0
		for modifierFrom in objFrom.modifiers:
			newModifier = None
			while True :
				try:
					newModifier = objTo.modifiers[index]
				except IndexError:
					newModifier = None
				if(newModifier is not None and newModifier.type != modifierFrom.type):
					objTo.modifiers.remove(newModifier)
				else:
					if newModifier is None:
						newModifier = objTo.modifiers.new(modifierFrom.name, modifierFrom.type)
					if self.copyProperties:
						properties = [p.identifier for p in modifierFrom.bl_rna.properties
									  if not p.is_readonly]
						for prop in properties:
							setattr(newModifier, prop, getattr(modifierFrom, prop))
					
					index = index + 1
					break
		if len(objFrom.modifiers) != len(objTo.modifiers):
			for modifier in objTo.modifiers:
				try:
					objFrom.modifiers[modifier.name]
				except KeyError:
					objTo.modifiers.remove(modifier)
		allowCompiling()
		return output
