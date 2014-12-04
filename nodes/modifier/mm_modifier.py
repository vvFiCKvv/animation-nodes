import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
	
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

	def getInputSocketNames(self):
		return {"Modifier" : "modifier"}
	def getOutputSocketNames(self):
		return {"Modifier" : "modifier"}
		
	def loadModifierProperties(self, modifier):
		if modifier.type == self.modifierType:
			return
		print("Modifier changed to : ", self.modifierType)
		self.modifierType = modifier.type
		for inputSocket in self.inputs:
			if(inputSocket.name=="Modifier"):
				continue
			self.inputs.remove(inputSocket)
			
		for p in modifier.bl_rna.properties:
				if p.is_readonly:
					continue
				prop = p.identifier
				self.inputs.new("mn_GenericSocket",prop)
		return
	def execute(self, modifier):
		if(modifier):
			self.inputs["Modifier"].objectName = modifier.id_data.name
			self.inputs["Modifier"].modifierName =  modifier.name
			self.loadModifierProperties(modifier)
		return modifier
