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
#		selector = row.operator("mn.assign_active_object_to_socket", text = "", icon = "EYEDROPPER")
#		selector.nodeTreeName = node.id_data.name
#		selector.nodeName = node.name
#		selector.isOutput = self.is_output
#		selector.socketName = self.name
#		selector.target = "objectName"
#		col.separator()
		
	def getValue(self):
		if not self.objectName:
			return
		if not self.modifierName:
			return
		return bpy.data.objects[self.objectName].modifiers.get(self.modifierName)
		
	def setStoreableValue(self, data):
		dataTable = data.split(":")
		self.objectName = dataTable[0]
		self.modifierName = dataTable[1]
	def getStoreableValue(self):
		return self.objectName + ":" + self.modifierName
	
	
#class AssignActiveObjectToNode(bpy.types.Operator):
#	bl_idname = "mn.assign_active_object_to_socket"
#	bl_label = "Assign Active Object"
	
#	nodeTreeName = bpy.props.StringProperty()
#	nodeName = bpy.props.StringProperty()
#	target = bpy.props.StringProperty()
#	isOutput = bpy.props.BoolProperty()
#	socketName = bpy.props.StringProperty()
	
#	@classmethod
#	def poll(cls, context):
#		return getActive() is not None
		
#	def execute(self, context):
#		obj = getActive()
#		node = getNode(self.nodeTreeName, self.nodeName)
#		socket = getSocketFromNode(node, self.isOutput, self.socketName)
#		setattr(socket, self.target, obj.name)
#		return {'FINISHED'}

