import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_ModifierSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_ModifierSocket"
	bl_label = "Modifier Socket"
	dataType = "Modifier"
	allowedInputTypes = ["Modifier", "Object"]
	drawColor = (0.4, 0.6, 0.8, 1)
	
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	modifierName = bpy.props.StringProperty(update = nodePropertyChanged)
	
	def drawInput(self, layout, node, text):
		col = layout.column()
		row = col.row(align = True)
		row.prop_search(self, "objectName",  bpy.context.scene, "objects", icon="NONE", text = "")
		selector = row.operator("mn.assign_active_object_to_socket", text = "", icon = "EYEDROPPER")
		selector.nodeTreeName = node.id_data.name
		selector.nodeName = node.name
		selector.isOutput = self.is_output
		selector.socketName = self.name
		selector.target = "objectName"
#		col.separator()
		row = col.row(align = True)
		if(self.objectName):
			row.prop_search(self, "modifierName", bpy.context.scene.objects[self.objectName] , "modifiers", icon="NONE", text = "")
		col.separator()
		
	def getValue(self):
		if not self.objectName:
			return
		if not self.modifierName:
			return
#		print("getValue: return: ", bpy.data.objects[self.objectName].modifiers.get(self.modifierName))
		return bpy.data.objects[self.objectName].modifiers.get(self.modifierName)
		
	def setStoreableValue(self, data):
#		print(data.name)
#		print("mn_modifiier setStoreableValue: ", data.id_data.name, " -> ", data.name)
		if data is bpy.types.Object: 
			self.objectName = data.name
			self.modifierName = None
		else:
			self.objectName = data.id_data.name
			self.modifierName = data.name
		
	def getStoreableValue(self):
		return "bpy.data.objects[\""+self.objectName+"\"].modifiers[\""+self.modifierName+"\"]"


