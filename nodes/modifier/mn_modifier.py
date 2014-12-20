import bpy
from types import MethodType
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *


class mn_ModifierNode(Node, AnimationNode):
	"""A Class that extents an animation node witch represents a modifier of an object 
	and have the functionality to create input sockets for each property of the Modifier.
	
	Note: 
		Tho node may be linked to an object socket input.
	
	Attributes:
		bl_idname (str): Blender's id name is 'mn_ModifierNode'.
		bl_label (str): Blender's Label is 'Modifier Node'.
		node_category (str): This node is type of 'Modifier'.
		objectName (str): The name of blender Object witch this node is refer to.
		modifierName (str): The name of blender Modifier witch this node is refer to.
		propertyName (str): The name of blender Modifier Property witch this node is refer to.
	"""
	bl_idname = "mn_ModifierNode"
	bl_label = "Modifier Node"
	node_category = "Modifier"
#	TODO: Check if needed update = nodePropertyChanged because it changes only in execution string.
	objectName = bpy.props.StringProperty()
#	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	modifierName = bpy.props.StringProperty(update = nodePropertyChanged)
	
	def init(self, context):
		"""Initialization of the node.
		
		Args:
			context:
		"""
		forbidCompiling()
		socket = self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.outputs.new("mn_ModifierSocket", "Modifier").showName = False
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		try:
			data =  eval("bpy.context.scene.objects['" + self.objectName + "']")
			layout.prop_search(self, "modifierName", data, "modifiers", icon="NONE", text = "")
		except (KeyError, SyntaxError, ValueError, AttributeError):
			pass
		return
	def changeObject(self, objectName):
		"""This function called when the name of the object changes and is responsible for enumerate the input - output sockets.
		
		Args:
			object (bpy.types.Object): The name to correct object.
		"""
		self.objectName = objectName
		return
	def getInputSocketNames(self):
		return {"Object" : "Object"}
	def getOutputSocketNames(self):
		return {"Modifier" : "Modifier"}
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		tabSpace = "    "
		thisNode = "bpy.data.node_groups['"  + self.id_data.name + "'].nodes['" + self.name + "']"
		codeLines.append("if %Object% is not None and %Object%.name != " + thisNode + ".objectName:")
		codeLines.append(tabSpace + thisNode + ".changeObject(%Object%.name)")
		if outputUse["Modifier"]:
			codeLines.append("try:")
			codeLines.append(tabSpace + "$Modifier$ = %Object%.modifiers[" + thisNode + ".modifierName" + "]")
			codeLines.append("except (KeyError, SyntaxError, ValueError, AttributeError) as exp:")
			codeLines.append(tabSpace + "$Modifier$ = None")
			codeLines.append(tabSpace + "pass")
#		print("\n".join(codeLines))
		return "\n".join(codeLines)
