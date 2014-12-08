import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_PropertySocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_PropertySocket"
	bl_label = "RNA property node socket type"
	dataType = "Property"
	allowedInputTypes = ["all"]
	drawColor = (0.6, 0.3, 0.3, 0.7)
	
	dataPath = bpy.props.StringProperty(update = nodePropertyChanged)
	name = bpy.props.StringProperty(update = nodePropertyChanged)
	def propertyType(self):
		return eval("type(" + self.dataPath + "." + self.name + ")")
	def draw_color(self, context, node):
		propertyType = self.propertyType()
		if(propertyType is int):
			return bpy.types.mn_IntegerSocket.drawColor
		if(propertyType is float):
			return bpy.types.mn_FloatSocket.drawColor
		if(propertyType is bpy.types.Object):
			return bpy.types.mn_ObjectSocket.drawColor
#		if(propertyType is Vector):
#			return bpy.types.mn_VectorSocket.drawColor
		if(propertyType is str):
			return bpy.types.mn_StringSocket.drawColor
		if(propertyType is bool):
			return bpy.types.mn_BooleanSocket.drawColor
#		print("Undefine drow color for:", self.dataPath + " : " + self.name , " with Type:", propertyType)
		return self.drawColor
	def drawInput(self, layout, node, text):
		col = layout.column()
		row = col.row(align = True)
		if not self.dataPath or not self.name:
			row.label("Missing property")
			return
		try:
			row.prop(eval(self.dataPath), self.name, text = text.replace("_", " "))
		except KeyError:
			return
	
	def drawOutput(self, layout, node, text):
		col = layout.column()
		row = col.row(align = True)
		if not self.dataPath or not self.name:
			row.label("Missing property")
			return
#		row.enabled = False
		try:
			row.prop(eval(self.dataPath), self.name, text = text.replace("_", " "))
		except KeyError:
			return
	
	def drawLinked(self, layout, node, text):
		col = layout.column()
		row = col.row(align = True)
		if not self.dataPath or not self.name:
			row.label("Missing property")
			return
		row.enabled = False
		try:
			row.prop(eval(self.dataPath), self.name, text = text.replace("_", " "))
		except KeyError:
			return
		
	def getValue(self):
		if not self.dataPath:
			return
		if not self.name:
			return
		return eval(self.dataPath + "." + self.name)

	def setStoreableValue(self, data):
		if not self.dataPath:
			return
		if not self.name:
			return
		value = str(data)
		if(self.propertyType() is bpy.types.Object):
			value = "bpy.data.objects['" + str(data.name) + "']"
		exec(self.dataPath + "." + self.name + " = " + value)
		
	def getStoreableValue(self):
		return eval(self.dataPath+self.name)


