import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ModifierOutputNode(Node, AnimationNode):
	bl_idname = "mn_ModifierOutputNode"
	bl_label = "Modifier Output Node"
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
		for inputSocket in self.inputs:
			if(inputSocket.name=="Modifier"):
				continue
			print("remove item:", inputSocket)
			self.inputs.remove(inputSocket)
		if modifier is None:
			self.modifierType = ""
			return
		print("Modifier from: ", self.modifierType," To: ", modifier.type)
		self.modifierType = modifier.type
		modifierDataPath =  self.inputs["Modifier"].getStoreableValue()
		for p in modifier.bl_rna.properties:
				if p.is_readonly:
					continue
				prop = p.identifier
				inputSocket = self.inputs.new("mn_PropertySocket", prop)
				inputSocket.dataPath = modifierDataPath
				inputSocket.name = prop
		return

	def execute(self,inputs):
		forbidCompiling()
		output = {}
		modifier = self.inputs["Modifier"].getValue()
		if modifier is None or modifier.type != self.modifierType:
			self.initModifier(modifier)
		for input in inputs:
			if(isSocketLinked(self.inputs[input])):
#				print("input: ", self.inputs[input], "new input: ", str(inputs[input]))
				self.inputs[input].setStoreableValue(inputs[input])
		allowCompiling()

		output["Modifier"] =  inputs["Modifier"]
		return output
