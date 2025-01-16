

# https://www.open3d.org/docs/release/tutorial/geometry/mesh.html
import open3d as o3d
# from open3d import copy
import numpy as np
from random import random



path = "../../models/bob.glb"
mesh = o3d.io.read_triangle_mesh(path)

# Step 1: Cluster connected triangles
prune = False
if prune:
    indices, count, _ = mesh.cluster_connected_triangles()
    indices = np.asarray(indices)
    count = np.asarray(count)

    # remove isolated faces
    keepers = count[indices] <= 1
    mesh.remove_triangles_by_mask(keepers)

# recompute connected components
indices, count, _ = mesh.cluster_connected_triangles()
indices = np.asarray(indices)
count = np.asarray(count)

print( 'indices', len( np.unique(indices) ) )
print( 'tri per cluster', len( np.unique(count) ) )
print( 'mesh tris', len( np.unique(mesh.triangles) ))

# Step 2: Create submeshes for each cluster
submeshes = []
combined_mesh = o3d.geometry.TriangleMesh()
for i in count:
    
    # recreate the whole mesh
    submesh = o3d.geometry.TriangleMesh(mesh.vertices, mesh.triangles)
    
    # preserve only this patch 
    keeperss = count[indices] != i
    submesh.remove_triangles_by_mask(keeperss)
    submesh.remove_unreferenced_vertices()

    # assign random color
    submesh.paint_uniform_color([random(), random(), random()])
    
    # export as attribute
    colors = np.full(( len(submesh.vertices), 3),[random(), random(), random()] )
    submesh.vertex_colors = o3d.utility.Vector3dVector(colors)

    # add to buffer
    combined_mesh += submesh

# save result
o3d.io.write_triangle_mesh(path.replace('.glb', '.obj'), combined_mesh)
# visualize result
combined_mesh.compute_vertex_normals()
o3d.visualization.draw_geometries([combined_mesh])
