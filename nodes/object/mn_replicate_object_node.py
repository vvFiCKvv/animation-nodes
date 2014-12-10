import bpy, time
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.nodes.mn_node_helper import *
from animation_nodes.utils.mn_object_utils import *
from animation_nodes.mn_cache import *

class mn_ObjectNamePropertyGroup(bpy.types.PropertyGroup):
	objectName = bpy.props.StringProperty(name = "Object Name", default = "", update = nodePropertyChanged)
	objectIndex = bpy.props.IntProperty(name = "Object Index", default = 0, update = nodePropertyChanged)

class mn_ReplicateObjectNode(Node, AnimationNode):
	bl_idname = "mn_ReplicateObjectNode"
	bl_label = "Replicate Object"
	
	def copyTypeChanged(self, context):
		self.free()
	
	linkedObjects = bpy.props.CollectionProperty(type = mn_ObjectNamePropertyGroup)
	unlinkedObjects = bpy.props.CollectionProperty(type = mn_ObjectNamePropertyGroup)
	setObjectData = bpy.props.BoolProperty(default = False)
	
	deepCopy = bpy.props.BoolProperty(default = False, update = copyTypeChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_IntegerSocket", "Instances")
		self.outputs.new("mn_ObjectListSocket", "Objects")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		setData = layout.operator("mn.set_object_data_on_all_objects")
		setData.nodeTreeName = self.id_data.name
		setData.nodeName = self.name
		
		layout.prop(self, "deepCopy", text = "Deep Copy")
		
	def draw_buttons_ext(self, context, layout):
		unlink = layout.operator("mn.unlink_instances_from_node")
		unlink.nodeTreeName = self.id_data.name
		unlink.nodeName = self.name
		
	def getInputSocketNames(self):
		return {"Object" : "sourceObject",
				"Instances" : "instances"}
	def getOutputSocketNames(self):
		return {"Objects" : "objects",}
		
	def execute(self, sourceObject, instances):
		instances = max(instances, 0)
		
		if sourceObject is None:
			self.unlinkAllObjects()
			return []
			
		while instances < len(self.linkedObjects):
			self.unlinkOneObject()
			
			
		objects = []
		allObjects = bpy.data.objects
		objectAmount = len(allObjects)
		
		outputObjectCounter = 0
		currentIndex = 0
		while(outputObjectCounter < instances):
			useObject = False
			incrementIndex = True
			if currentIndex < len(self.linkedObjects):
				item = self.linkedObjects[currentIndex]
				searchName = item.objectName
				if item.objectIndex < objectAmount:
					object = allObjects[item.objectIndex]
					if object.name == searchName: useObject = True
					else:
						index = allObjects.find(searchName)
						if index != -1:
							item.objectIndex = index
							object = allObjects[index]
							useObject = True
						else:
							self.unlinkObjectItemIndex(currentIndex)
							incrementIndex = False
				else: # duplicated code. have to find a cleaner solution
					index = allObjects.find(searchName)
					if index != -1:
						item.objectIndex = index
						object = allObjects[index]
						useObject = True
					else:
						self.unlinkObjectItemIndex(currentIndex)
						incrementIndex = False
			else:
				object = self.linkNextObjectToScene(sourceObject)
				useObject = True
				incrementIndex = False
			
			if useObject: 
				objects.append(object)
				outputObjectCounter += 1
			if incrementIndex: currentIndex += 1
		
		renewObjects = False
		if self.setObjectData:
			for object in objects:
				if object.type == sourceObject.type:
					if object.data != sourceObject.data:
						object.data = sourceObject.data
				else:
					renewObjects = True
			self.setObjectData = False
		if renewObjects: self.free()
		
		return objects
		
	def unlinkAllObjects(self):
		objectNames = []
		for item in self.linkedObjects:
			objectNames.append(item.objectName)
			
		for name in objectNames:
			object = bpy.data.objects.get(name)
			if object is not None:
				self.unlinkReplication(object)
		
	def unlinkOneObject(self):
		self.unlinkObjectItemIndex(len(self.linkedObjects)-1)
		
	def unlinkObjectItemIndex(self, itemIndex):
		item = self.linkedObjects[itemIndex]
		objectName = item.objectName
		objectIndex = item.objectIndex
		self.linkedObjects.remove(itemIndex)
		object = bpy.data.objects.get(objectName)
		if object is not None:
			try:
				self.unlinkReplication(object)
				newItem = self.unlinkedObjects.add()
				newItem.objectName = objectName
				newItem.objectIndex = objectIndex
			except: pass
			
	def linkNextObjectToScene(self, sourceObject):
		isNewObjectLinked = False
		while not isNewObjectLinked:
			if len(self.unlinkedObjects) == 0:
				self.newReplication(sourceObject)
			item = self.unlinkedObjects[0]
			object = bpy.data.objects.get(item.objectName)
			if object is not None:
				bpy.context.scene.objects.link(object)
				linkedItem = self.linkedObjects.add()
				linkedItem.objectName = item.objectName
				linkedItem.objectIndex = item.objectIndex
				isNewObjectLinked = True
			self.unlinkedObjects.remove(0)
		return object
			
	def newReplication(self, sourceObject):
		if self.deepCopy: data = sourceObject.data.copy()
		else: data = sourceObject.data
		newObject = bpy.data.objects.new(getPossibleObjectName("instance"), data)
		newObject.parent = getMainObjectContainer()
		item = self.unlinkedObjects.add()
		item.objectName = newObject.name
		item.objectIndex = 0
		
	def unlinkReplication(self, object):
		if bpy.context.mode != "OBJECT" and getActive() == object: bpy.ops.object.mode_set(mode = "OBJECT")
		bpy.context.scene.objects.unlink(object)
		
	def setObjectDataOnAllObjects(self):
		self.setObjectData = True
		
	def unlinkInstancesFromNode(self):
		self.linkedObjects.clear()
		self.unlinkedObjects.clear()
		self.inputs.get("Instances").number = 0
			
	def free(self):
		self.unlinkAllObjects()
		self.linkedObjects.clear()
		self.unlinkedObjects.clear()
			
	def copy(self, node):
		self.linkedObjects.clear()
		self.unlinkedObjects.clear()
		
class SetObjectDataOnAllObjects(bpy.types.Operator):
	bl_idname = "mn.set_object_data_on_all_objects"
	bl_label = "Set Correct Mesh"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.setObjectDataOnAllObjects()
		return {'FINISHED'}
		
class UnlinkInstancesFromNode(bpy.types.Operator):
	bl_idname = "mn.unlink_instances_from_node"
	bl_label = "Unlink Instances from Node"
	bl_description = "This will make sure that the objects won't be removed if you remove the Replicate Node."
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.unlinkInstancesFromNode()
		return {'FINISHED'}

