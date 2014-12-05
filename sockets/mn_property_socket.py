import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_PropertySocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_PropertySocket"
	bl_label = "RNA property node socket type"
	dataType = "Property"
	allowedInputTypes = ["all"]
	drawColor = (0, 1, 0, 1)
	
	dataPath = bpy.props.StringProperty(update = nodePropertyChanged)
	name = bpy.props.StringProperty(update = nodePropertyChanged)
	
	def drawInput(self, layout, node, text):
		col = layout.column()
		row = col.row(align = True)
		if not self.dataPath or not self.name:
			row.label("Missing property")
			return
		row.prop(eval(self.dataPath), self.name, text = text)
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
		exec(self.dataPath + "." + self.name + " = " + str(data))
		
	def getStoreableValue(self):
		return eval(self.dataPath+self.name)


