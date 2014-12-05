import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_Modifier(Node, AnimationNode):
	bl_idname = "mn_Modifier"
	bl_label = "Modifier Output Node"
	node_category = "Modifier"
	
	modifierType = bpy.props.StringProperty(update = nodePropertyChanged)

	def init(self, context):
		forbidCompiling()
#		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_ModifierSocket", "Modifier").showName = False
		self.outputs.new("mn_ModifierSocket", "Modifier").showName = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		return
		objName = self.inputs["Modifier"].objectName
		modName = self.inputs["Modifier"].modifierName
		if not objName:
			return
		if not modName:
			return
		obj = bpy.data.objects[objName]
		mod = obj.modifiers[modName]
		
		layout.label("Modifier:" + mod.name)
#		for all properties of modifier mod
		for p in mod.bl_rna.properties:
			if p.is_readonly:
				continue
			prop = p.identifier
#           print("\t\t" , prop , " : " , getattr(mod, prop))
			layout.prop(mod, prop) 
		return
		
	def initModifier(self,modifier):
		objName = self.inputs["Modifier"].objectName
		modName = self.inputs["Modifier"].modifierName
		if not objName:
			return
		if not modName:
			return
			
		print("Modifier from: ", self.modifierType," To: ", modifier.type)
		self.modifierType = modifier.type
		for inputSocket in self.inputs:
			if(inputSocket.name=="Modifier"):
				continue
			
			print("remove item:", inputSocket)
			self.inputs.remove(inputSocket)
			
		for p in modifier.bl_rna.properties:
				if p.is_readonly:
					continue
				prop = p.identifier
				inputSocket = self.inputs.new("mn_PropertySocket",prop)
				inputSocket.dataPath = "bpy.data.objects[\""+objName+"\"].modifiers[\""+modName+"\"]"
				inputSocket.name = prop
		return
	
	def loadModifierProperties(self, modifier):
		
		
		for link in self.links:
			inputSocket = link.to_socket
			fromSocket = getOriginSocket(inputSocket)
			inputSocket.setStoreableValue(fromSocket.getStoreableValue())
#		objName = self.inputs["Modifier"].objectName
#		modName = self.inputs["Modifier"].modifierName
#		
#		for inputSocket in self.inputs:
#			if(inputSocket.name=="Modifier"):
#				continue
#
#			if not inputSocket.is_linked:
#				continue
#TODO: To be removed
#			print(inputSocket.links[0].from_node.inputs[0].getStoreableValue())
#			inputSocket.setValue(inputSocket.links[0].from_socket.getStoreableValue())
		return

	def execute(self,inputs):
#		forbidCompiling()
		objName = self.inputs["Modifier"].objectName
		modName = self.inputs["Modifier"].modifierName
		if not objName:
			return
		if not modName:
			return
		output = {}
		modifier = self.inputs["Modifier"].getValue()
		if modifier.type != self.modifierType:
			self.initModifier(modifier)
#		self.loadModifierProperties()
		for input in inputs:
			if(isSocketLinked(self.inputs[input])):
#				print("input: ", self.inputs[input], "new input: ", str(inputs[input]))
				self.inputs[input].setStoreableValue(str(inputs[input]))
#			print(input)
#		allowCompiling()

		output["Modifier"] =  inputs["Modifier"]
		return output

#TODO: Fix names
#	def getInputSocketNames(self):
#		return {"Modifier" : "modifier",
#				"levels" : "levels" }
#	def getOutputSocketNames(self):
#		return {"Modifier" : "modifier"}
#	
#	
#	def useInLineExecution(self):
#		return True
#	def getInLineExecutionString(self, useOutput):
#		codeLines = []
#		objName = self.inputs["Modifier"].objectName
#		modName = self.inputs["Modifier"].modifierName
#		if not objName:
#			return "\n".join(codeLines)
#		if not modName:
#			return "\n".join(codeLines)
#		self.loadModifierProperties(eval("bpy.data.objects[\""+objName+"\"].modifiers[\""+modName+"\"]"))
#		if useOutput["Modifier"]:
#			print("$modifier$ = bpy.data.objects[\""+objName+"\"].modifiers[\""+modName+"\"]")
#			codeLines.append("$modifier$ = bpy.data.objects[\""+objName+"\"].modifiers[\""+modName+"\"]")
#		return "\n".join(codeLines)

#	def execute(self, modifier):
#		if(modifier):
#			print("modifier input is used: object: ", self.inputs["Modifier"].objectName," modifier: ", self.inputs["Modifier"].modifierName)
#			self.inputs["Modifier"].objectName = modifier.id_data.name
#			self.inputs["Modifier"].modifierName =  modifier.name
#			self.loadModifierProperties(modifier)
#			
#			
#		return modifier
