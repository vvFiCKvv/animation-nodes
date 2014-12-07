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
	showDetails = bpy.props.BoolProperty(default = False)
	objectNeedsUpdate = bpy.props.BoolProperty(default = False)
	
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
		col.separator()
		row = col.row(align = True)
		if(self.objectName):
			row.prop_search(self, "modifierName", bpy.context.scene.objects[self.objectName] , "modifiers", icon="NONE", text = "")
	def drawOutput(self, layout, node, text):
		col = layout.column()
		row = col.row(align = True)
		modifier = self.getValue()
		if(self.objectName and modifier is not None):
			if self.showDetails:
#				col = col.box().column()
				row = col.row(align = True)
				row = col.row(align = True)
				row = col.row(align = True)
				
#				row.operator("object.modifier_move_up", icon="TRIA_UP", text="").modifier=self.modifierName
				op = row.operator("mn.object_modifier_operator", text = "", icon = "TRIA_UP")
				op.nodeTreeName = node.id_data.name
				op.nodeName = node.name
				op.isOutput = self.is_output
				op.socketName = self.name
				op.operatorName = "object.modifier_move_up"
				op.target = "objectNeedsUpdate"
				
#				row.operator("object.modifier_move_down", icon="TRIA_DOWN", text="").modifier=self.modifierName
				op = row.operator("mn.object_modifier_operator", text = "", icon = "TRIA_DOWN")
				op.nodeTreeName = node.id_data.name
				op.nodeName = node.name
				op.isOutput = self.is_output
				op.socketName = self.name
				op.operatorName = "object.modifier_move_down"
				op.target = "objectNeedsUpdate"
				
				row.prop(modifier, "name", text="")
#				row.operator("object.modifier_remove", icon="X", text="").modifier=self.modifierName
				op = row.operator("mn.object_modifier_operator", text = "", icon = "X")
				op.nodeTreeName = node.id_data.name
				op.nodeName = node.name
				op.isOutput = self.is_output
				op.socketName = self.name
				op.operatorName = "object.modifier_remove"
				op.target = "objectNeedsUpdate"
				
				row = col.row(align = True)
				row.alignment = "CENTER"
				row.prop(modifier,"show_render", text="")
				row.prop(modifier,"show_viewport", text="")
				row.prop(modifier,"show_in_editmode", text="")
				row.prop(modifier,"show_on_cage", text="")
				row = col.row(align = True)
				row = col.row(align = True)

			else:
				row.prop(modifier, "name", text="")

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

class ObjectModifierOperator(bpy.types.Operator):
	bl_idname = "mn.object_modifier_operator"
	bl_label = "Call Object Modifier Operator"
	operatorName = bpy.props.StringProperty()
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	isOutput = bpy.props.BoolProperty()
	socketName = bpy.props.StringProperty()
	target = bpy.props.StringProperty()
	
	@classmethod
	def poll(self, context):
		if self.socketName is None or self.nodeTreeName is None or self.operatorName is None or self.isOutput is None:
			return False
		return True
		
	def execute(self, context):
		if self.socketName is None or self.nodeTreeName is None or self.operatorName is None or self.isOutput is None:
			return {'FINISHED'}
		node = getNode(self.nodeTreeName, self.nodeName)
		socket = getSocketFromNode(node, self.isOutput, self.socketName)
		
#		selected = bpy.context.selected_objects
		active = bpy.context.scene.objects.active

		targetObject = bpy.data.objects[socket.objectName]
		bpy.context.scene.objects.active = targetObject
#		targetObject.select = True
		exec("bpy.ops." + self.operatorName + "(modifier=\"" + socket.modifierName + "\")")
		bpy.context.scene.objects.active = active
		if socket is not None and self.target is not None:
			setattr(socket, self.target, True)
		return {'FINISHED'}

