import bpy
import requests
import os 
from .utils import resetStage, clear

def getParams( context ):
    return  {
                    "slat" : {
                        "sparse" : {
                            "steps": context.window_manager.sparse_steps,
                            "cfg_strength": context.window_manager.sparse_strength,
                        },
                        "slat" : {
                            "steps": context.window_manager.slat_steps,
                            "cfg_strength": context.window_manager.slat_strength,
                        },
                    },
                    "glb":{
                        "simplify" : context.window_manager.simplify,
                        "texture_size" : context.window_manager.texture_size
                    }
                }

def displayPLY( model_name ):

    name, ext = os.path.splitext( os.path.basename(model_name) )

    #impoprt PLY 
    bpy.ops.wm.ply_import(
        filepath=model_name, 
        import_colors="LINEAR",
        import_attributes=True 
    )
    # doc:
    # https://docs.blender.org/api/current/bpy.ops.wm.html

    # create the color attribute on the object's geometry
    bpy.ops.geometry.color_attribute_add(name="Color")

    # upscale & translate model
    bpy.context.object.scale *= 4
    bpy.context.object.location[2] = 2

    # store ref to mesh   
    mesh = bpy.data.objects[name]

    #create geometry node
    geom_node = mesh.modifiers.new('geom_node',type='NODES')

    #Create a pointer to the node tree
    tree = bpy.data.node_groups[0] # TODO get by name

    #Set that tree to your modifier
    mesh.modifiers['geom_node'].node_group = tree

    #set the "Color" attribute as the output of the Geometry node
    geom_node["Socket_2_attribute_name"] = "Color"


class ComputeOperator(bpy.types.Operator):
    bl_idname = "object.compute"
    bl_label = "compute"
   
    def execute(self, context):
        image_path = None
        try:
            image_path = context.window_manager.image.filepath
        except:
            print( 'file name is empty')
        
        if image_path is None:
            return {"FINISHED"}
        
        image_path = bpy.path.abspath(os.path.join(image_path))
        print( "TRELLIS compute", image_path )

        # add an image placeholder
        clear()
        bpy.ops.object.empty_image_add(filepath=image_path, location=(0, 2, 3), rotation=(1.5708, 0, 0), scale=(1, 1, 1))
        
        #send image ref to TRELLIS
        json_data = {
            "image": image_path,
            "params": getParams(context)
        }
        response = requests.post('http://localhost:8080/compute', json=json_data)
        
        if response.status_code == 200:

            # display the result
            model = response.json()["value"]
            resetStage()
            displayPLY( model )

            return {"FINISHED"}

        else:
            print('something went wrong:', response.status_code)
        return {"FINISHED"}
        

class DiscretizeOperator(bpy.types.Operator):
    bl_idname = "object.discretize"
    bl_label = "discretize"
    
    def execute(self, context):
        image_path = None
        try:
            image_path = context.window_manager.image.filepath
        except:
            print( 'file name is empty')
        
        if image_path is None:
            return {"FINISHED"}
        
        image_path = bpy.path.abspath(os.path.join(image_path))
        print( "TRELLIS discretize", image_path )

        # add an image placeholder
        clear()
        bpy.ops.object.empty_image_add(filepath=image_path, location=(0, 2, 3), rotation=(1.5708, 0, 0), scale=(1, 1, 1))
        
        #send image ref to TRELLIS
        json_data = {
            "image": image_path,
            "params": getParams(context)
        }
        response = requests.post('http://localhost:8080/discretize', json=json_data)
        
        if response.status_code == 200:

            resetStage()
            
            model = response.json()["value"]
            name  = os.path.basename(model)

            # receive result
            bpy.ops.import_scene.gltf(filepath=model, files=[{"name":name, "name":name}], loglevel=20)

            # upscale & translate model
            bpy.context.object.scale *= 4
            bpy.context.object.location[2] = 2

            return {"FINISHED"}

        else:
            print('something went wrong:', response.status_code)
        return {"FINISHED"}