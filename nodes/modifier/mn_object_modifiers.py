import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ObjectModifiersNode(Node, AnimationNode):
	bl_idname = "mn_ObjectModifiersNode"
	bl_label = "Object Modifiers List"
	node_category = "Modifier"
	
	onlyAdd = bpy.props.BoolProperty(default = False)
	automaticUpdate = bpy.props.BoolProperty(default = True, update = nodeTreeChanged)
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "automaticUpdate", text = "Update")
		layout.prop(self, "onlyAdd", text = "Don't Remove")
		return
	def socketsUpdate(self, object):
		if object is not None:
			for modifier in object.modifiers:
				try:
					outputSocket = self.outputs[modifier.name]
				except KeyError:
					outputSocket = self.outputs.new("mn_ModifierSocket", modifier.name)
					outputSocket.removeable = True
					outputSocket.callNodeToRemove = True
		if self.onlyAdd:
			return
		if object is None  or len(self.outputs) != len(object.modifiers):
			for outputSocket in self.outputs:
				try:
					object.modifiers[outputSocket.name]
				except (KeyError, SyntaxError, ValueError, AttributeError, NameError ):
					print("remove item:", outputSocket)
					self.outputs.remove(outputSocket)
		return
	def removeSocket(self, socket):
		if socket.is_output:
			self.outputs.remove(socket)
		else:
			self.inputs.remove(socket)
	def getInputSocketNames(self):
		return {"Object" : "Object"}
	def getOutputSocketNames(self):
		outputSocketNames = {}
		for socket in self.outputs:
			outputSocketNames[socket.identifier] = socket.identifier
		return outputSocketNames
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		tabSpace = "    "
		if self.automaticUpdate:
			#the node rna data path.
			thisNode = "bpy.data.node_groups['"  + self.id_data.name + "'].nodes['" + self.name + "']"
			codeLines.append(thisNode + ".socketsUpdate(%Object%)")
		for outputSocket in self.outputs:
			if not outputSocket.is_linked:
				continue
			codeLines.append("try:")
			codeLines.append(tabSpace + "$" + outputSocket.identifier + "$ = %Object%.modifiers['" + outputSocket.identifier + "']")
			codeLines.append("except (KeyError, SyntaxError, ValueError, AttributeError, NameError):")
#			codeLines.append(tabSpace + "print('Error: " + outputSocket.identifier + "')")
			codeLines.append(tabSpace + "$" + outputSocket.identifier + "$ = None")
			codeLines.append(tabSpace + "pass")
#		print("\n".join(codeLines))
		return "\n".join(codeLines)
