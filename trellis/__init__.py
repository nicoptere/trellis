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

# sparse & SLAT 
WindowManager.sparse_steps = IntProperty(name="steps", default=12, min=1, max=100)
WindowManager.sparse_strength = FloatProperty(name="strength", default=7.5, min=0, max=50, step=0.1)

WindowManager.slat_steps = IntProperty(name="steps", default=12, min=1, max=100)
WindowManager.slat_strength = FloatProperty(name="strength", default=3, min=0, max=50, step=0.1)

# GLB optimization settings
WindowManager.simplify = FloatProperty(name="simplfication", default=0.95, min=0, max=1, step=0.01)
WindowManager.texture_size = IntProperty(name="texture size", default=1024, min=64, max=8192, step=1)

class TRELLIS(bpy.types.Panel):
    
    bl_label = "TRELLIS"
    bl_idname = "TRELLIS_PT_TOOL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "TRELLIS"

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


# Empty image panel 
class ImagePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_process"
    bl_label = "TRELLIS"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    # bl_options = {'DEFAULT_CLOSED'}
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def checkGizmo(self, context):
        gizmo = bpy.context.view_layer.objects.active
        if hasattr(gizmo, "data"):
            if hasattr(gizmo.data, "filepath" ):
                return gizmo
        return None

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Panel")

    def draw(self, context):
        
        layout = self.layout
        gizmo = self.checkGizmo(context) 
        if gizmo is not None:
            
            context.window_manager.gizmo  = gizmo
            context.window_manager.image  = gizmo.data


            # box = layout.box()
            # image_path = context.window_manager.image.filepath
            # box.label(text="image: " + image_path)
            # box.operator("object.compute")
            # box.operator("object.discretize")
            

def register():
    WindowManager.image = PointerProperty(name="image", type=Image)
    WindowManager.gizmo = PointerProperty(name="gizmo", type=Object)
    bpy.utils.register_class(ComputeOperator)
    bpy.utils.register_class(DiscretizeOperator)
    bpy.utils.register_class(TRELLIS)
    bpy.utils.register_class(ImagePanel)
    

def unregister():
    bpy.utils.unregister_class(ComputeOperator)
    bpy.utils.unregister_class(DiscretizeOperator)
    bpy.utils.unregister_class(TRELLIS)
    bpy.utils.unregister_class(ImagePanel)
    del WindowManager.image 
    del WindowManager.gizmo 

if __name__ == "__main__":
    print( "calling TRELLIS main" ) 
    register()