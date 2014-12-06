import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ModifierInfoNode(Node, AnimationNode):
	bl_idname = "mn_Modifier"
	bl_label = "Modifier Info Node"
	node_category = "Modifier"
	
	modifierType = bpy.props.StringProperty(update = nodePropertyChanged)

	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ModifierSocket", "Modifier").showName = False
		self.outputs.new("mn_ModifierSocket", "Modifier").showName = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		return
		
	def initModifier(self,modifier):
		print("Modifier from: ", self.modifierType," To: ", modifier.type)
		self.modifierType = modifier.type
		for outputSocket in self.outputs:
			if(outputSocket.name=="Modifier"):
				continue
			print("remove item:", inputSocket)
			self.outputSocket.remove(inputSocket)
			
		for p in modifier.bl_rna.properties:
				if p.is_readonly:
					continue
				prop = p.identifier
				outputSocket = self.outputs.new("mn_PropertySocket",prop)
				outputSocket.dataPath = self.outputs["Modifier"].getStoreableValue()
				outputSocket.name = prop
		return

	def execute(self,inputs):
		forbidCompiling()
		output = {}
		modifier = self.inputs["Modifier"].getValue()
		if modifier and modifier.type != self.modifierType:
			self.initModifier(modifier)
#		for input in inputs:
#			if(isSocketLinked(self.inputs[input])):
#				print("input: ", self.inputs[input], "new input: ", str(inputs[input]))
#				self.inputs[input].setStoreableValue(inputs[input])
		allowCompiling()

		output["Modifier"] =  inputs["Modifier"]
		return output
