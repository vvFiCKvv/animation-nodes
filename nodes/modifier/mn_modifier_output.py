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
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ModifierSocket", "Modifier").showName = False
		self.outputs.new("mn_ModifierSocket", "Modifier").showName = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		return
	def changeObject(self, modifier):
		self.objectName = modifier.id_data.name
#		print("Modifier Change Object To:", self.objectName)
		modifierDataPath = self.inputs["Modifier"].getStoreableValue()
		for inputSocket in self.inputs:
			if(inputSocket.name=="Modifier"):
				continue
			inputSocket.dataPath = modifierDataPath
		return
	
	def initModifier(self,modifier):
		for inputSocket in self.inputs:
			if(inputSocket.name=="Modifier"):
				continue
			print("remove item:", inputSocket)
			self.inputs.remove(inputSocket)
		if modifier is None:
			self.modifierType = ""
			self.objectName = ""
			return
		else:
			self.modifierType = modifier.type
			self.objectName = modifier.id_data.name
		modifierDataPath = self.inputs["Modifier"].getStoreableValue()
		print("Modifier changes To: ", modifierDataPath)
		for p in modifier.bl_rna.properties:
				if p.is_readonly:
					continue
				prop = p.identifier
				if prop[0:5] == "show_":
					continue
				if prop[0:10] == "use_apply_":
					continue
				inputSocket = self.inputs.new("mn_PropertySocket", prop)
				inputSocket.dataPath = modifierDataPath
				inputSocket.name = prop
		return

	def execute(self,inputs):
		forbidCompiling()
		output = {}
		self.inputs["Modifier"].setStoreableValue(inputs["Modifier"])
		modifier = self.inputs["Modifier"].getValue()
#if modifier type change call inti modifier to re-create the correct socket inputs
		if modifier is None or modifier.type != self.modifierType:
			self.initModifier(modifier)
#if only object changes re-point the existing sockets to the correct ones
		else:
			if modifier.id_data.name != self.objectName:
				self.changeObject(modifier)
		
#update values of linked input sockets
		for input in inputs:
			if(isSocketLinked(self.inputs[input]) and input != "Modifier"):
#				print("input: ", self.inputs[input], "new input: ", str(inputs[input]))
				self.inputs[input].setStoreableValue(inputs[input])


		allowCompiling()

		output["Modifier"] =  inputs["Modifier"]
		return output
