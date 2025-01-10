bl_info = {
    "name": "Trellis",
    "blender": (4, 3, 1),
    "category": "Object",
}

# import addon_utils
# print(addon_utils.paths())

if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    importlib.reload(trellis_operator)
    # ...
else:
    import bpy
    from . import (
        utils,
        trellis_operator
        # ...
    )
    from .utils import blop
    from .trellis_operator import ComputeOperator, DiscretizeOperator

import bpy

# properties 
# https://blender.stackexchange.com/posts/278152/revisions

from bpy.types import WindowManager, Scene, Image
from bpy.props import FloatProperty, IntProperty, PointerProperty

#  TODO 

# sparse & SLAT 
WindowManager.sparse_steps = IntProperty(name="steps", default=10, min=1, max=100)
WindowManager.sparse_strength = FloatProperty(name="strength", default=8, min=0, max=50, step=0.1)
WindowManager.slat_steps = IntProperty(name="steps", default=10, min=1, max=100)
WindowManager.slat_strength = FloatProperty(name="strength", default=5, min=0, max=50, step=0.1)

# GLB optimization settings
WindowManager.simplify = FloatProperty(name="simplfication", default=0.8, min=0, max=1, step=0.01)
WindowManager.texture_size = IntProperty(name="texture size", default=2048, min=64, max=8192, step=1)

class TRELLIS(bpy.types.Panel):
    
    bl_label = "TRELLIS"
    bl_idname = "TRELLIS_PT_TOOL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TRELLIS"

    def draw(self, context):
        layout = self.layout
        
        # select image button
        layout.label(text="select an image")
        row = layout.row()
        layout.template_ID(context.window_manager, "image", open="image.open")
    
        # COMPUTE

        # computation settings
        layout.label(text="SLAT settings")
        
        row = layout.row()
        row.prop(context.window_manager, "sparse_steps")
        row.prop(context.window_manager, "sparse_strength")
        row = layout.row()
        row.prop(context.window_manager, "slat_steps")
        row.prop(context.window_manager, "slat_strength")

        # compute SLAT model
        row = layout.row(align=True)
        row.scale_y = 1.0
        row.operator("object.compute")


        # DISCRETIZE 
        
        # discretization settings
        layout.label(text="discretize")
        row = layout.row()
        row.prop(context.window_manager, "simplify")
        row = layout.row()
        row.prop(context.window_manager, "texture_size")
        
        # discretize SLAT model (convert to textured GLB)
        row = layout.row(align=True)
        row.scale_y = 1.0
        row.operator("object.discretize")

        # call render
        row = layout.row(align=True)
        row.operator("render.render")

def register():
    print( 'hello')
    WindowManager.image = PointerProperty(name="image", type=Image)
    bpy.utils.register_class(ComputeOperator)
    bpy.utils.register_class(DiscretizeOperator)
    bpy.utils.register_class(TRELLIS)
    blop(4)
    

def unregister():
    print( 'goodbye')
    blop(2)
    bpy.utils.unregister_class(ComputeOperator)
    bpy.utils.unregister_class(DiscretizeOperator)
    bpy.utils.unregister_class(TRELLIS)
    del WindowManager.image 

if __name__ == "__main__":
    print( "calling main" ) 
    blop(1)
    register()


"""
class ObjectCursorArray(bpy.types.Operator):
    bl_idname = "object.cursor_array"
    bl_label = "Cursor Array"
    bl_options = {'REGISTER', 'UNDO'}

    # moved assignment from execute() to the body of the class...
    total: bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor.location
        obj = context.active_object

        total = self.total

        for i in range(total):
            obj_new = obj.copy()
            scene.collection.objects.link(obj_new)

            obj_new.location[0] = obj.location[0] + i
            obj_new.location[1] = obj.location[1] + i
            obj_new.location[2] = obj.location[2] + i

        return {'FINISHED'}
    
def menu_func(self, context):
    self.layout.operator(ObjectCursorArray.bl_idname)

def register():
    print( 'hello')
    blop()
    blop()
    blop()
    blop()
    blop()
    bpy.utils.register_class(ObjectCursorArray)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    print( 'goodbye')
    blop()
    blop()
    bpy.utils.unregister_class(ObjectCursorArray)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    print( "calling main" ) 
    blop(1)
    register()
"""
