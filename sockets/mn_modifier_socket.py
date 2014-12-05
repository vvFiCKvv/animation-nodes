import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_ModifierSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_ModifierSocket"
	bl_label = "Modifier Socket"
	dataType = "Modifier"
	allowedInputTypes = ["Modifier"]
	drawColor = (0, 0, 1, 1)
	
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	modifierName = bpy.props.StringProperty(update = nodePropertyChanged)
	showName = bpy.props.BoolProperty(default = True)
	
	def drawInput(self, layout, node, text):
		col = layout.column()
		row = col.row(align = True)
		if self.showName:
			row.label(text)

		row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = "")
		row = col.row(align = True)
		if self.showName:
			row.label(text)
		if(self.objectName):
			row.prop_search(self, "modifierName", bpy.context.scene.objects[self.objectName] , "modifiers", icon="NONE", text = "")
		
	def getValue(self):
		if not self.objectName:
			return
		if not self.modifierName:
			return
#		print("getValue: return: ", bpy.data.objects[self.objectName].modifiers.get(self.modifierName))
		return bpy.data.objects[self.objectName].modifiers.get(self.modifierName)
		
	def setStoreableValue(self, data):
#		print("mn_modifiier setStoreableValue: ", data.id_data.name, " -> ", data.name)
		self.objectName = data.id_data.name
		self.modifierName = data.name
		
	def getStoreableValue(self):
		return "bpy.data.objects[\""+self.objectName+"\"].modifiers[\""+self.modifierName+"\"]"


