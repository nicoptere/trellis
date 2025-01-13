import bpy
from math import sin, cos, pi

def clear():
    #clear stage
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def resetStage():
    return 
    #camera
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0), rotation=(1.20079, -1.25822e-06, 0.872667), scale=(1, 1, 1))
    bpy.context.object.location[0] = -3
    bpy.context.object.location[1] = -5
    bpy.context.object.location[2] = 5

    bpy.context.object.rotation_euler[0] = 1.14843
    bpy.context.object.rotation_euler[1] = 0
    bpy.context.object.rotation_euler[2] = -0.54105
    bpy.context.object.data.lens = 25


    #lights
    bpy.ops.object.light_add(type='POINT', radius=1, align='WORLD', location=(0, -3, 4), scale=(1, 1, 1))
    bpy.context.object.rotation_euler[1] = 0.261799
    bpy.context.object.rotation_euler[2] = -1

    bpy.context.object.data.type = 'SUN'
    bpy.context.object.data.energy = 25

    steps = 6
    step = pi * 2 / steps
    radius = 4
    for i in range( steps ):
        
        angle = i * step
        x = cos( angle ) * radius
        y = 3 if i % 2 == 0 else 1 
        z = sin( angle ) * radius
        print( x, z )
        
        bpy.ops.object.light_add(type='POINT', radius=1, align='WORLD', location=(x, z, y), scale=(1, 1, 1))
        bpy.context.object.data.type = 'AREA'
        bpy.context.object.data.energy = 500
        
        polar = pi / 16
        
        bpy.context.object.rotation_euler[0] = pi / 2  + ( -polar if i % 2 == 0 else polar )
        bpy.context.object.rotation_euler[1] = 0
        bpy.context.object.rotation_euler[2] = ( pi / 2 + angle  )
        
        bpy.context.object.data.use_shadow = False #i % 2 == 0
