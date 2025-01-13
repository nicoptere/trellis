bl_info = {
    "name": "Trellis",
    "blender": (3, 0, 0),
    "category": "Object",
}

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
    from .trellis_operator import ComputeOperator, DiscretizeOperator

import bpy

# properties 
# https://blender.stackexchange.com/posts/278152/revisions

from bpy.types import WindowManager, Scene, Image, Object
from bpy.props import FloatProperty, IntProperty, PointerProperty


class TRELLIS(bpy.types.Panel):
    
    bl_label = "TRELLIS"
    bl_idname = "TRELLIS_PT_TOOL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TRELLIS"

    def checkGizmo(self, context):
        active = bpy.context.view_layer.objects.active
        if hasattr(active, "data"):
            if hasattr(active.data, "filepath" ):
                return active
        return None
    
    def draw(self, context):
        
        layout = self.layout
        
        # image browser
        layout.label(text="select an image")
        row = layout.row()
        layout.template_ID(context.window_manager, "image", open="image.open")
    
        # SLAT computation: convert image to point cloud
        layout.label(text="point cloud")
        box = layout.box()
        
        box.label(text="sparse")
        row = box.row()
        row.prop(context.window_manager, "sparse_steps")
        row.prop(context.window_manager, "sparse_strength")
        
        box.label(text="SLAT")
        row = box.row()
        row.prop(context.window_manager, "slat_steps")
        row.prop(context.window_manager, "slat_strength")
        
        row = box.row(align=True)
        row.operator("object.compute")
        
        # discretize SLAT model (convert point cloud to textured GLB)
        layout.label(text="discretize")
        box = layout.box()
        row = box.row()
        row.prop(context.window_manager, "simplify")
        row = box.row()
        row.prop(context.window_manager, "texture_size")
        
        row = box.row(align=True)
        row.operator("object.discretize")

        # check if user clicked on an Empty object (a drag dropped image)
        gizmo = self.checkGizmo(context) 
        if gizmo is not None:
            context.window_manager.gizmo = gizmo
            context.window_manager.image = gizmo.data



def register():
    # declare some variables
    WindowManager.image = PointerProperty(name="image", type=Image)
    WindowManager.gizmo = PointerProperty(name="gizmo", type=Object)

    # sparse & SLAT settings
    WindowManager.sparse_steps = IntProperty(name="steps", default=12, min=1, max=100)
    WindowManager.sparse_strength = FloatProperty(name="strength", default=7.5, min=0, max=50, step=0.1)

    WindowManager.slat_steps = IntProperty(name="steps", default=12, min=1, max=100)
    WindowManager.slat_strength = FloatProperty(name="strength", default=3, min=0, max=50, step=0.1)

    # GLB optimization settings
    WindowManager.simplify = FloatProperty(name="simplfication", default=0.95, min=0, max=1, step=0.01)
    WindowManager.texture_size = IntProperty(name="texture size", default=1024, min=64, max=8192, step=1)

    bpy.utils.register_class(ComputeOperator)
    bpy.utils.register_class(DiscretizeOperator)
    bpy.utils.register_class(TRELLIS)
    

def unregister():

    # dispose
    del WindowManager.image 
    del WindowManager.gizmo 
    del WindowManager.sparse_steps
    del WindowManager.sparse_strength
    del WindowManager.slat_steps
    del WindowManager.slat_strength
    del WindowManager.simplify
    del WindowManager.texture_size


    bpy.utils.unregister_class(ComputeOperator)
    bpy.utils.unregister_class(DiscretizeOperator)
    bpy.utils.unregister_class(TRELLIS)

if __name__ == "__main__":
    print( "calling TRELLIS main" ) 
    register()