import bpy
from animation_nodes.mn_execution import nodePropertyChanged
from animation_nodes.mn_node_base import *

class mn_StringSearchSocket(mn_BaseSocket, mn_SocketProperties):
	bl_idname = "mn_StringSearchSocket"
	bl_label = "Search String Socket"
	dataType = "String"
	allowedInputTypes = ["String"]
	drawColor = (1, 1, 1, 1)
	
	string = bpy.props.StringProperty(default = "", update = nodePropertyChanged)
	searchPath = bpy.props.StringProperty(default = "", update = nodePropertyChanged)
	searchProperty = bpy.props.StringProperty(default = "", update = nodePropertyChanged)
	showName = bpy.props.BoolProperty(default = True)
	
	def drawInput(self, layout, node, text):
		col = layout.column()
		row = col.row(align = True)
		if self.showName: 
			row.label(text)
			row = col.row(align = True)
		text = ""
		try:
			if self.searchPath == "":
				 raise NameError('name is not define')
			searchData = eval(self.searchPath)
			row.prop_search(self, "string", searchData , self.searchProperty, icon="NONE", text = "")
		except (NameError, KeyError):
			row.prop(self, "string", text = text)
		
	def getValue(self):
		return self.string
		
	def setStoreableValue(self, data):
		self.string = data
	def getStoreableValue(self):
		return self.string
