"""

import bpy
from bpy.props import FloatProperty, IntProperty
from math import pi
from .select_operator import SelectImageOperator
from .trellis_operator import ComputeOperator

# properties 
# https://blender.stackexchange.com/posts/278152/revisions


#  TODO 
# add filepath as global var

# sparse & SLAT 
bpy.types.WindowManager.sparse_steps = IntProperty(name="sparse steps", default=10, min=1, max=100)
bpy.types.WindowManager.sparse_strength = FloatProperty(name="sparse cfg strength", default=8, min=0, max=50, step=0.1)
bpy.types.WindowManager.slat_steps = IntProperty(name="slat steps", default=10, min=1, max=100)
bpy.types.WindowManager.slat_strength = FloatProperty(name="slat cfg strength", default=5, min=0, max=50, step=0.1)

# GLB optimization settings
bpy.types.WindowManager.simplify = FloatProperty(name="simplfication", default=.8, min=0, max=1, step=0.01)
bpy.types.WindowManager.texture_size = IntProperty(name="texture size", default=1024, min=64, max=8192, step=1)


class TRELLIS(bpy.types.Panel):
    
    bl_label = "TRELLIS"
    bl_idname = "TRELLIS_PT_TOOL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TRELLIS"

    def draw(self, context):
        layout = self.layout
        scene = context.scene


        # del(bpy.types.Scene.myvar)

        # select image button
        row = layout.row()
        row.scale_y = 1.0
        row.operator("image.select_image")


        # optimisation settings
        layout.label(text="SLAT")
        
        row = layout.row()
        row.prop(context.window_manager, "sparse_steps")
        row = layout.row()
        row.prop(context.window_manager, "sparse_strength")
        row = layout.row()
        row.prop(context.window_manager, "slat_steps")
        row = layout.row()
        row.prop(context.window_manager, "slat_strength")

        print( "panel", context.window_manager.simplify )

        # compute SLAT 
        layout.label(text="optimize")
        
        row = layout.row()
        row.prop(context.window_manager, "simplify")
        row = layout.row()
        row.prop(context.window_manager, "texture_size")
        
        row = layout.row(align=True)
        row.scale_y = 1.0
        row.operator("object.compute")

        row = layout.row(align=True)
        row.scale_y = 1.0
        row.operator("render.render")

def register():
    SelectImageOperator.register()
    ComputeOperator.register()
    bpy.utils.register_class(TRELLIS)

    # Run after user selects path
    def end_fn(filepath): 
        
        print("image: ", filepath)
        ComputeOperator.image_path = filepath
        bpy.ops.object.empty_image_add(filepath=filepath, align='VIEW', location=(0, 0, 2), rotation=(pi/2, 0, 0), scale=(1, 1, 1))
        bpy.context.object.empty_display_size = 4.0
        
    def cancel_fn():
        print("user canceled")

    SelectImageOperator.end_fn = end_fn
    SelectImageOperator.cancel_fn = cancel_fn

def unregister():
    SelectImageOperator.unregister()
    ComputeOperator.unregister()
    bpy.utils.unregister_class(TRELLIS)

if __name__ == "__main__":
    TRELLIS.register()
"""
