bl_info = {
	"name": "OpenStreetMap Georeferencing",
	"author": "Vladimir Elistratov <vladimir.elistratov@gmail.com>",
	"version": (1, 0, 0),
	"blender": (2, 6, 9),
	"location": "View 3D > Object Mode > Tool Shelf",
	"description" : "OpenStreetMap based object georeferencing",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "https://github.com/vvoovv/blender-geo/issues",
	"support": "COMMUNITY",
	"category": "3D View",
}

import bpy
import math

import sys
sys.path.append("D:\\projects\\blender\\blender-geo")
from transverse_mercator import TransverseMercator
import utils

class OsmGeoreferencingPanel(bpy.types.Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_context = "objectmode"
	bl_label = "Georeferencing"

	def draw(self, context):
		l = self.layout
		c = l.column()
		c.operator("object.set_original_position")
		c.operator("object.do_georeferencing")

class SetOriginalPosition(bpy.types.Operator):
	bl_idname = "object.set_original_position"
	bl_label = "Set original position"
	bl_description = "Remember original position"

	def execute(self, context):
		# remember the location and orientation of the reference object
		# take the first selected object as a reference object
		refObject = context.selected_objects[0]
		refObjectData = (refObject, refObject.location.copy(), refObject.rotation_euler[2])
		bpy.refObjectData = refObjectData
		return {"FINISHED"}

class DoGeoreferencing(bpy.types.Operator):
	bl_idname = "object.do_georeferencing"    
	bl_label = "Perform georeferencing"
	bl_description = "Perform georeferencing"

	def execute(self, context):
		# try to find an empty Blender object with "latitude" and "longitude" as custom properties
		geoObject = utils.findEmptyGeoObject(context)
		
		if not geoObject:
			self.report({"ERROR"}, "Import OpenStreetMap data first!")
			return {"FINISHED"}
		
		if not hasattr(bpy, "refObjectData"):
			self.report({"ERROR"}, "Set original position of your object first!")
			return {"FINISHED"}
		
		refObjectData = bpy.refObjectData
		refObject = refObjectData[0]
		# calculationg new position of the reference object center
		p = refObject.matrix_world * (-refObjectData[1])
		projection = TransverseMercator(lat=geoObject["latitude"], lon=geoObject["longitude"])
		(lat, lon) = projection.toGeographic(p[0], p[1])
		context.scene["longitude"] = lon
		context.scene["latitude"] = lat
		context.scene["heading"] = (refObject.rotation_euler[2]-refObjectData[2])*180/math.pi

		# restoring original objects location and orientation
		bpy.ops.transform.rotate(value=-(refObject.rotation_euler[2]-refObjectData[2]), axis=(0,0,1))
		bpy.ops.transform.translate(value=-(refObject.location-refObjectData[1]))
		# cleaning up
		del bpy.refObjectData
		return {"FINISHED"}

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)