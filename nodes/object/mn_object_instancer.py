import bpy, time
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *
from animation_nodes.nodes.mn_node_helper import *
from animation_nodes.utils.mn_name_utils import *
from animation_nodes.mn_cache import *

objectTypes = ["Mesh", "Text", "Camera", "Point Lamp"]
objectTypeItems = [(type, type, "") for type in objectTypes]

class mn_ObjectNamePropertyGroup(bpy.types.PropertyGroup):
	objectName = bpy.props.StringProperty(name = "Object Name", default = "", update = nodePropertyChanged)
	objectIndex = bpy.props.IntProperty(name = "Object Index", default = 0, update = nodePropertyChanged)

class mn_ObjectInstancer(Node, AnimationNode):
	bl_idname = "mn_ObjectInstancer"
	bl_label = "Object Instancer"
	
	def copyFromSourceChanged(self, context):
		self.inputs["Source"].hide = not self.copyFromSource
		self.resetInstancesEvent(context)
		
	def resetInstancesEvent(self, context):
		self.resetInstances = True
	
	linkedObjects = bpy.props.CollectionProperty(type = mn_ObjectNamePropertyGroup)
	resetInstances = bpy.props.BoolProperty(default = False, update = nodePropertyChanged)
	
	copyFromSource = bpy.props.BoolProperty(default = True, name = "Copy from Source", update = copyFromSourceChanged)
	deepCopy = bpy.props.BoolProperty(default = False, update = resetInstancesEvent, name = "Deep Copy", description = "Make the instances independent of the source object (e.g. copy mesh)")
	objectType = bpy.props.EnumProperty(default = "Mesh", name = "Object Type", items = objectTypeItems, update = resetInstancesEvent)
	copyObjectProperties = bpy.props.BoolProperty(default = False, update = resetInstancesEvent, description = "Enable this to copy modifiers/constrains/... from the source objec.)")
	
	parentInstances = bpy.props.BoolProperty(default = True, name = "Parent to Main Container", update = resetInstancesEvent)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Instances").setMinMax(0, 100000)
		self.inputs.new("mn_ObjectSocket", "Source").showName = False
		self.outputs.new("mn_ObjectListSocket", "Objects")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "copyFromSource")
		if self.copyFromSource:
			layout.prop(self, "copyObjectProperties", text = "Copy Full Object")
			layout.prop(self, "deepCopy")
		else:
			layout.prop(self, "objectType", text = "")
		
	def draw_buttons_ext(self, context, layout):
		layout.prop(self, "parentInstances")
	
		setData = layout.operator("mn.reset_object_data_on_all_objects")
		setData.nodeTreeName = self.id_data.name
		setData.nodeName = self.name
	
		unlink = layout.operator("mn.unlink_instances_from_node")
		unlink.nodeTreeName = self.id_data.name
		unlink.nodeName = self.name
		
	def getInputSocketNames(self):
		return {"Instances" : "instancesAmount",
				"Source" : "sourceObject"}
	def getOutputSocketNames(self):
		return {"Objects" : "objects",}
		
	def execute(self, instancesAmount, sourceObject):
		instancesAmount = max(instancesAmount, 0)
			
		if self.copyFromSource and sourceObject is None:
			self.removeAllObjects()
			return []
			
		if self.resetInstances:
			self.removeAllObjects()
			self.resetInstances = False
			
		while instancesAmount < len(self.linkedObjects):
			self.removeLastObject()
			
		return self.getOutputObjects(instancesAmount, sourceObject)
		
	def getOutputObjects(self, instancesAmount, sourceObject):
		objects = []
		objectAmount = len(bpy.data.objects)
		counter = 0
		
		while(counter < instancesAmount):
			if counter < len(self.linkedObjects):
				object = self.getObjectFromItemIndex(counter, objectAmount)
				if object is None:
					self.removeObjectFromItemIndex(counter)
			else:
				object = self.appendNewObject(sourceObject)
				
			if object is not None:
				objects.append(object)
				counter += 1
			
		return objects
	
	# at first try to get the object by index, because it's faster and then search by name
	def getObjectFromItemIndex(self, itemIndex, objectAmount):
		item = self.linkedObjects[itemIndex]
		if item.objectIndex < objectAmount:
			object = bpy.data.objects[item.objectIndex]
			if object.name == item.objectName:
				return object
				
		index = bpy.data.objects.find(item.objectName)
		if index == -1: return None
		
		item.objectIndex = index
		return bpy.data.objects[index]
		
	def removeAllObjects(self):
		objectNames = []
		for item in self.linkedObjects:
			objectNames.append(item.objectName)
			
		for name in objectNames:
			object = bpy.data.objects.get(name)
			if object is not None:
				self.removeObject(object)
				
		self.linkedObjects.clear()
		
	def removeLastObject(self):
		self.removeObjectFromItemIndex(len(self.linkedObjects)-1)
		
	def removeObjectFromItemIndex(self, itemIndex):
		item = self.linkedObjects[itemIndex]
		objectName = item.objectName
		self.linkedObjects.remove(itemIndex)
		object = bpy.data.objects.get(objectName)
		if object is not None:
			self.removeObject(object)
			
	def removeObject(self, object):
		self.unlinkInstance(object)
		if object.users == 0:
			data = object.data
			type = object.type
			bpy.data.objects.remove(object)
			self.removeObjectData(data, type)
			
	def removeObjectData(self, data, type):
		if data.users == 0:
			if type == "MESH":
				bpy.data.meshes.remove(data)
			elif type == "CAMERA":
				bpy.data.cameras.remove(data)
			elif type in ["FONT", "CURVE", "SURFACE"]:
				bpy.data.curves.remove(data)
			elif type == "META":
				bpy.data.metaballs.remove(data)
			elif type == "ARMATURE":
				bpy.data.armatures.remove(data)
			elif type == "LATTICE":
				bpy.data.lattices.remove(data)
			elif type == "LAMP":
				bpy.data.lamps.remove(data)
			elif type == "SPEADER":
				bpy.data.speakers.remove(data)
			
	def appendNewObject(self, sourceObject):
		object = self.newInstance(sourceObject)
		bpy.context.scene.objects.link(object)
		linkedItem = self.linkedObjects.add()
		linkedItem.objectName = object.name
		linkedItem.objectIndex = bpy.data.objects.find(object.name)
		return object
			
	def newInstance(self, sourceObject):
		instanceData = self.getSourceObjectData(sourceObject)
		if self.copyObjectProperties and self.copyFromSource:
			newObject = sourceObject.copy()
			newObject.data = instanceData
		else:
			newObject = bpy.data.objects.new(getPossibleObjectName("instance"), instanceData)
			
		if self.parentInstances:
			newObject.parent = getMainObjectContainer()
		return newObject
		
	def getSourceObjectData(self, sourceObject):
		if self.copyFromSource:
			if self.deepCopy:
				return sourceObject.data.copy()
			else:
				return sourceObject.data
		else:
			if self.objectType == "Mesh":
				return bpy.data.meshes.new(getPossibleMeshName("instance mesh"))
			elif self.objectType == "Text":
				return bpy.data.curves.new(getPossibleCurveName("instance text"), type = "FONT")
			elif self.objectType == "Camera":
				return bpy.data.cameras.new(getPossibleCameraName("instance camera"))
			elif self.objectType == "Point Lamp":
				return bpy.data.lamps.new(getPossibleLampName("instance lamp"), type = "POINT")
		return None
		
	def unlinkInstance(self, object):
		if bpy.context.mode != "OBJECT" and getActive() == object: 
			bpy.ops.object.mode_set(mode = "OBJECT")
		bpy.context.scene.objects.unlink(object)
		
	def resetObjectDataOnAllInstances(self):
		self.resetInstances = True
		
	def unlinkInstancesFromNode(self):
		self.linkedObjects.clear()
		self.inputs.get("Instances").number = 0
			
	def free(self):
		self.removeAllObjects()
			
	def copy(self, node):
		self.linkedObjects.clear()
		
class ResetObjectDataOnAllInstances(bpy.types.Operator):
	bl_idname = "mn.reset_object_data_on_all_objects"
	bl_label = "Reset Source Data"
	bl_description = "Reset the source data on all instances"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.resetObjectDataOnAllInstances()
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

