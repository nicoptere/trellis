import bpy
import requests
import os 
from math import pi
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

def placeModel( context, object ):
    gizmo = context.window_manager.gizmo
    object.scale *= 2
    object.location[2] = 1
    if gizmo is not None:
        s = gizmo.empty_display_size
        object.location = gizmo.location
        object.rotation_mode = 'XYZ'
        object.rotation_euler = gizmo.rotation_euler
        object.rotation_euler[0] -= pi /2
        object.scale = (s,s,s)
        # reset position 
        context.window_manager.gizmo = None

def displayPLY( context, model_name ):

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
    placeModel( context, bpy.context.object )

    # store ref to mesh   
    mesh = bpy.data.objects[name]

    #create geometry node
    geom_node = mesh.modifiers.new('geom_node',type='NODES')

    #Create a pointer to the node tree
    tree = bpy.data.node_groups[0]
    group = bpy.data.node_groups
    for g in group:
        if g.name == "ply_geom_node":
            tree = g
        
    #Set that tree to your modifier
    mesh.modifiers['geom_node'].node_group = tree

    #set the "Color" attribute as the output of the Geometry node
    geom_node["Socket_2_attribute_name"] = "Color"

def displayGLB( context, model ):
    
    name  = os.path.basename(model)
    objects = bpy.data.objects
    meshes = bpy.data.meshes

    # receive result
    bpy.ops.import_scene.gltf(filepath=model, files=[{"name":name, "name":name}], loglevel=20)

    world = bpy.context.view_layer.objects.active
    objects.remove(world, do_unlink=True)
    bpy.ops.object.parent_clear(type='CLEAR')

    # find the mesh and rename it's geometry
    mesh = None
    for obj in objects:
        if obj.name == "geometry_0":
            obj.name = name
            meshes[ "geometry_0" ].name = name
            mesh = obj
            mat = mesh.data.materials[0]
            bpy.data.images["Image_0"].name = "Image_"+name
            break
    
    # assign custom shader 
    mesh.data.materials.clear()
    mat = bpy.data.materials.get("direct_diffuse").copy()
    mesh.data.materials.append(mat)

    # set proper image as texture
    for n in mat.node_tree.nodes:
        if n.name == "Image Texture":
            n.image = bpy.data.images["Image_"+name]

    # upscale & translate model
    placeModel( context, mesh )

def sanitizePath(context):    
    image_path = None
    try:
        image_path = context.window_manager.image.filepath
    except:
        print( 'file name is empty')
        return None
    image_path = bpy.path.abspath(os.path.join(image_path))
    if os.path.exists(image_path) == False:
        return None
    return image_path

def displayImagePreview(image_path):
    clear()
    bpy.ops.object.empty_image_add(filepath=image_path, location=(0, 3, 2.5), rotation=(1.5708, 0, 0), scale=(1, 1, 1))
    

class ComputeOperator(bpy.types.Operator):
    bl_idname = "object.compute"
    bl_label = "compute SLAT"
   
    def execute(self, context):
        # get image path
        image_path = sanitizePath(context)
        if image_path is None:
            return {"FINISHED"}
        print( "TRELLIS compute", image_path )

        # add an image placeholder
        # displayImagePreview(image_path)

        # check if file already exists        
        name = os.path.splitext(image_path)[0]
        model = "%s.ply" % name
        if os.path.exists(model):            
            resetStage()
            displayPLY( context, model )
            return {"FINISHED"}
        else:
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
                displayPLY( context, model )
                return {"FINISHED"}
            else:
                print('something went wrong:', response.status_code)
            return {"FINISHED"}
        

class DiscretizeOperator(bpy.types.Operator):
    bl_idname = "object.discretize"
    bl_label = "discretize SLAT model"
    
    def execute(self, context):
        # get image path
        image_path = sanitizePath(context)
        if image_path is None:
            return {"FINISHED"}
        print( "TRELLIS discretize", image_path )

        # add an image placeholder
        # displayImagePreview(image_path)

        # check if file already exists        
        name = os.path.splitext(image_path)[0]
        model = "%s.glb" % name
        if os.path.exists(model):            
            resetStage()
            displayGLB( context, model )
            return {"FINISHED"}
        else:
            #send image ref to TRELLIS
            json_data = {
                "image": image_path,
                "params": getParams(context)
            }
            response = requests.post('http://localhost:8080/discretize', json=json_data)
            if response.status_code == 200:
                model = response.json()["value"]
                resetStage()
                displayGLB( context, model )
                return {"FINISHED"}

            else:
                print('something went wrong:', response.status_code)
            return {"FINISHED"}