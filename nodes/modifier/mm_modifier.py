import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
	
class mn_Modifier(Node, AnimationNode):
	bl_idname = "mn_Modifier"
	bl_label = "Modifier Output Node"
	node_category = "Modifier"

	def init(self, context):
		forbidCompiling()
#		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_ModifierSocket", "Modifier").showName = False
		self.outputs.new("mn_ModifierSocket", "Modifier").showName = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		return
		
	def execute(self, input):
		return
		output = {}
		output["Uppercase"] = input["Text"].upper()
		return output
