import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ModifierOutputNode(Node, AnimationNode):
	bl_idname = "mn_ModifierOutputNode"
	bl_label = "Modifier Output Node"
	node_category = "Modifier"
	
	modifierDataPath = bpy.props.StringProperty(update = nodePropertyChanged)

	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ModifierSocket", "Modifier").showName = False
		self.outputs.new("mn_ModifierSocket", "Modifier").showName = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		return
		
	def initModifier(self,modifier):
		try:
			oldModifierType = eval(self.modifierDataPath).type
		except:
			oldModifierType = "NoneType"
		if modifier is not None and oldModifierType == modifier.type:
			self.modifierDataPath =  self.inputs["Modifier"].getStoreableValue()
			for inputSocket in self.inputs:
				if(inputSocket.name=="Modifier"):
					continue
				inputSocket.dataPath = self.modifierDataPath
			return
		for inputSocket in self.inputs:
			if(inputSocket.name=="Modifier"):
				continue
			print("remove item:", inputSocket)
			self.inputs.remove(inputSocket)
		if modifier is None:
			self.modifierDataPath = ""
			return
		print("Modifier from: ", self.modifierDataPath," To: ", self.inputs["Modifier"].getStoreableValue())
		self.modifierDataPath =  self.inputs["Modifier"].getStoreableValue()
		for p in modifier.bl_rna.properties:
				if p.is_readonly:
					continue
				prop = p.identifier
				if prop[0:5] == "show_":
					continue
				if prop[0:10] == "use_apply_":
					continue
				inputSocket = self.inputs.new("mn_PropertySocket", prop)
				inputSocket.dataPath = self.modifierDataPath
				inputSocket.name = prop
		return

	def execute(self,inputs):
		forbidCompiling()
		output = {}
		modifier = self.inputs["Modifier"].getValue()
		if modifier is None or self.inputs["Modifier"].getStoreableValue() != self.modifierDataPath:
			self.initModifier(modifier)
		for input in inputs:
			if(isSocketLinked(self.inputs[input])):
#				print("input: ", self.inputs[input], "new input: ", str(inputs[input]))
				self.inputs[input].setStoreableValue(inputs[input])
		allowCompiling()

		output["Modifier"] =  inputs["Modifier"]
		return output
