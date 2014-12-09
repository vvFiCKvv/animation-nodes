import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ObjectModifiersNode(Node, AnimationNode):
	bl_idname = "mn_ObjectModifiersNode"
	bl_label = "Object Modifier List Node"
	node_category = "Modifier"
	
	showDetails = bpy.props.BoolProperty(default = False)
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	objectNeedsUpdate = bpy.props.BoolProperty(default = False)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		allowCompiling()
		
	def draw_buttons_ext(self, context, layout):
		col = layout
		row = col.row(align = True)
#		wm.call_menu OBJECT_OT_modifier_add 
#bpy.ops.wm.call_menu(name="OBJECT_OT_modifier_add ")
#TODO: add modifier to proper object, not to selected		
		row.operator_menu_enum("object.modifier_add", "type")
		row = col.row(align = True)
		row = col.row(align = True)
		obj = eval("bpy.data.objects[\"" + self.objectName + "\"]")
		for modifier in obj.modifiers:
#			row.operator("object.modifier_move_up", icon="TRIA_UP", text="").modifier=self.modifierName
			op = row.operator("mn.object_modifier_operator", text = "", icon = "TRIA_UP")
			op.nodeTreeName = self.id_data.name
			op.nodeName = self.name
			op.objectName = self.objectName
			op.modifierName = modifier.name
			op.operatorName = "object.modifier_move_up"
			op.target = "objectNeedsUpdate"
			
#			row.operator("object.modifier_move_down", icon="TRIA_DOWN", text="").modifier=self.modifierName
			op = row.operator("mn.object_modifier_operator", text = "", icon = "TRIA_DOWN")
			op.nodeTreeName = self.id_data.name
			op.nodeName = self.name
			op.objectName = self.objectName
			op.modifierName = modifier.name
			op.operatorName = "object.modifier_move_down"
			op.target = "objectNeedsUpdate"
			
			row.prop(modifier, "name", text="")
#			row.operator("object.modifier_remove", icon="X", text="").modifier=self.modifierName
			op = row.operator("mn.object_modifier_operator", text = "", icon = "X")
			op.nodeTreeName = self.id_data.name
			op.nodeName = self.name
			op.objectName = self.objectName
			op.modifierName = modifier.name
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

	def draw_buttons(self, context, layout):
#		col = layout.box().column()
#		row = col.row(align = True)
		layout.prop(self, "showDetails", text = "Show Details")
		if self.showDetails:
			self.draw_buttons_ext(context, layout)
		return
		
	def initModifier(self,object):
		self.objectName = object.name 
		for outputSocket in self.outputs:
			print("remove item:", outputSocket)
			self.outputs.remove(outputSocket)
		objName = self.inputs["Object"].getStoreableValue()
		for modifier in object.modifiers:
			outputSocket = self.outputs.new("mn_ModifierSocket", modifier.name)
			outputSocket.objectName = objName
			outputSocket.modifierName = modifier.name
		return
		
	def execute(self,inputs):
		forbidCompiling()
		output = {}
		obj = self.inputs["Object"].getValue()
#		obj = inputs["Object"]
		if obj and (obj.name != self.objectName or len(self.outputs) != len(obj.modifiers) or self.objectNeedsUpdate):
			self.initModifier(obj)
		for outputSocket in self.outputs:
			if outputSocket.dataType  == "Modifier":
				outputValue =  outputSocket.getValue()
				if outputValue is None or self.objectNeedsUpdate == True:
					print("Modifier: ", outputSocket , " name changed")
					self.initModifier(obj)
					outputSocket.objectNeedsUpdate = False
				output[outputSocket.modifierName] = outputValue
		allowCompiling()
		return output

class ObjectModifierOperator(bpy.types.Operator):
	bl_idname = "mn.object_modifier_operator"
	bl_label = "Call Object Modifier Operator"
	operatorName = bpy.props.StringProperty()
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	target = bpy.props.StringProperty()
	objectName = bpy.props.StringProperty()
	modifierName = bpy.props.StringProperty()
	@classmethod
	def poll(self, context):
		if self.nodeTreeName is None or self.operatorName is None:
			return False
		return True
		
	def execute(self, context):
		print("exec: ", self.operatorName, self.nodeTreeName, self.nodeName, self.target, self.objectName, self.modifierName)
		if self.nodeTreeName is None or self.operatorName is None:
			return {'FINISHED'}
		node = getNode(self.nodeTreeName, self.nodeName)
		
#		selected = bpy.context.selected_objects
		active = bpy.context.scene.objects.active

		targetObject = bpy.data.objects[self.objectName]
		bpy.context.scene.objects.active = targetObject
#		targetObject.select = True
		if self.operatorName == "object.modifier_add":
			exec("bpy.ops.object.modifier_add()")
		exec("bpy.ops." + self.operatorName + "(modifier=\"" + self.modifierName + "\")")
		bpy.context.scene.objects.active = active
		if self.target is not None:
			setattr(node, self.target, True)
		return {'FINISHED'}
