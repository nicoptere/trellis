
import trimesh as tm
import numpy as np
import os
import matplotlib.pyplot as plt
from math import floor
from skimage.morphology import medial_axis, skeletonize
from collections import defaultdict
from scipy.spatial import Delaunay
from tqdm import tqdm

def alpha_shape_3D(pos, alpha):
    """
    Compute the alpha shape (concave hull) of a set of 3D points.
    Parameters:
        pos - np.array of shape (n,3) points.
        alpha - alpha value.
    return
        outer surface vertex indices, edge indices, and triangle indices
    """

    tetra = Delaunay(pos)
    print( tetra )
    # Find radius of the circumsphere.
    # By definition, radius of the sphere fitting inside the tetrahedral needs 
    # to be smaller than alpha value
    # http://mathworld.wolfram.com/Circumsphere.html
    tetrapos = np.take(pos,tetra.simplices,axis=0)
    normsq = np.sum(tetrapos**2,axis=2)[:,:,None]
    ones = np.ones((tetrapos.shape[0],tetrapos.shape[1],1))
    a = np.linalg.det(np.concatenate((tetrapos,ones),axis=2))
    Dx = np.linalg.det(np.concatenate((normsq,tetrapos[:,:,[1,2]],ones),axis=2))
    Dy = -np.linalg.det(np.concatenate((normsq,tetrapos[:,:,[0,2]],ones),axis=2))
    Dz = np.linalg.det(np.concatenate((normsq,tetrapos[:,:,[0,1]],ones),axis=2))
    c = np.linalg.det(np.concatenate((normsq,tetrapos),axis=2))
    r = np.sqrt(Dx**2+Dy**2+Dz**2-4*a*c)/(2*np.abs(a))

    # Find tetrahedrals
    tetras = tetra.simplices[r<alpha,:]
    # triangles
    TriComb = np.array([(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)])
    Triangles = tetras[:,TriComb].reshape(-1,3)
    Triangles = np.sort(Triangles,axis=1)
    # Remove triangles that occurs twice, because they are within shapes
    TrianglesDict = defaultdict(int)
    for tri in Triangles:TrianglesDict[tuple(tri)] += 1
    Triangles=np.array([tri for tri in TrianglesDict if TrianglesDict[tri] ==1])
    #edges
    EdgeComb=np.array([(0, 1), (0, 2), (1, 2)])
    Edges=Triangles[:,EdgeComb].reshape(-1,2)
    Edges=np.sort(Edges,axis=1)
    Edges=np.unique(Edges,axis=0)

    Vertices = np.unique(Edges)
    return Vertices,Edges,Triangles



def clamp( value, mini=0, maxi=1 ):
    return min( maxi, max( value, mini ) )

def bounding_box(vertices):
    """Bounding function to bound large arrays and np.memmaps"""
    mins =[10,10,10]#np.array(volume.shape)
    maxs =[-10,-10,-10]

    for v in vertices:
        mins[0] = min( v[0], mins[0] )
        mins[1] = min( v[1], mins[1] )
        mins[2] = min( v[2], mins[2] )

        maxs[0] = max( v[0], maxs[0] )
        maxs[1] = max( v[1], maxs[1] )
        maxs[2] = max( v[2], maxs[2] )

    size = (
        maxs[0] - mins[0],
        maxs[2] - mins[2],
        maxs[1] - mins[1],
    )
    return mins, maxs, size

def is_inside(point, mesh, direction=np.array([1, 0, 0]), tol=1e-5):
    
    intersections, _, _ = mesh.ray.intersects_location(
        ray_origins=[point - direction * tol],
        ray_directions=[direction],
    )
    count = len(intersections) % 2
    return count % 2 == 1


def snap_vertex( v, dim ):

    x = int( ( floor( clamp( .5 + v[0] ) * dim ) / dim ) * (dim-1) )
    y = int( ( floor( clamp( .5 + v[1] ) * dim ) / dim ) * (dim-1) )
    z = int( ( floor( clamp( .5 + v[2] ) * dim ) / dim ) * (dim-1) )
    
    z = dim - 1 - z # faces camera
    return x,y,z

def adjacency( voxels, x, y, z, diagonals=False ):

  tmp = [];
  w, h, d = voxels.shape()
  print( w,h,d )

  if y - 1 >= 0:
    tmp.append((y - 1) * w + x);
  if x + 1 < w:
    tmp.append(y * w + (x + 1));
  if y + 1 < h:
    tmp.append((y + 1) * w + x);
  if x - 1 >= 0:
    tmp.append(y * w + (x - 1));

  if diagonals == True:
    if x - 1 >= 0 and y - 1 >= 0:
        tmp.append((y - 1) * w + (x - 1));
    if x + 1 < w and y - 1 >= 0:
        tmp.append((y - 1) * w + (x + 1));
    if x + 1 < w and y + 1 < h:
        tmp.append((y + 1) * w + (x + 1));
    if x - 1 >= 0 and y + 1 < h:
        tmp.append((y + 1) * w + (x - 1));
  
  return tmp



# test 
name = "castle"
dim = 32
alpha = 0.5

mesh = tm.load_mesh('C:/Users/barra/Documents/blender/models/%s/%s.glb' % (name, name), process=False )

mesh = mesh.geometry['geometry_0']
# try to fix mesh
# mesh.process()
# # mesh = mesh.simplify_quadric_decimation(face_count=len( mesh.faces )//4 * 3 )
# 
# mesh.fill_holes()
# mesh.merge_vertices()

vs = mesh.vertices

while( mesh.is_watertight == False ):
    print( "computing alpha:", alpha )
    _, _, faces = alpha_shape_3D(vs, alpha * .1 )
    mesh.faces = faces
    mesh.fix_normals()
    alpha += .1

# print( -mesh.face_normals )
# mesh.show()
# quit()


voxel_file = "%s-%s-%s.npy" % (name,dim, alpha)
if os.path.exists( voxel_file )==False:

    # if not mesh.is_watertight:
    #     print("Mesh does not have consistent winding.")

    pos = []
    col = []
    margin = 0.01
    mins, maxs, _ = bounding_box(vs) 
    mi_x = mins[0] - margin
    mi_y = mins[1] - margin
    mi_z = mins[2] - margin
    ma_x = maxs[0] + margin
    ma_y = maxs[1] + margin
    ma_z = maxs[2] + margin

    step = 1/dim

    voxels = np.zeros( (dim, dim, dim), dtype=np.int8)
    for x in tqdm( np.arange( mi_x, ma_x, step) ):
        for y in np.arange( mi_y, ma_y, step):
            for z in np.arange( mi_z, ma_z, step):
                    v = [x,y,z]
                    if is_inside(v, mesh) :

                        pos.append( v )
                        col.append( [255,0,0])

                        vx, vy, vz = snap_vertex(v, dim)
                        voxels[ vx, vy, vz ] = 1

                        # pos.append( [vx, vy, vz] ) # 3D positions as a voxel grid 

    np.save(voxel_file, voxels)

    # view the volume
    inout = tm.PointCloud(pos, colors=col)
    # inout.show(line_settings={'point_size': 10})

    scene = tm.Scene([mesh, inout])
    scene.show( line_settings={'point_size': 10, "line_width":1}, flags={'wireframe': True} )
    

voxels = np.load( os.path.abspath( voxel_file ) )

"""
gauss = tm.load_mesh('C:/Users/barra/Documents/blender/models/%s/%s-gaussian.ply' % (name, name) )
vs_gaussian = gauss.vertices
colors = []
for v in tqdm( vs ):
    if is_inside(v, mesh) :
        colors.append( [255,0,0])
    else:
        colors.append( [0,0,255])

print( colors )
gaussian = tm.PointCloud(vs, colors=colors)
gaussian.show(line_settings={'point_size': 10})

# quit()
"""

"""
dim = 16
voxels = np.zeros( (dim, dim, dim), dtype=np.int8)
for v in vs:
    # x, y, z = snap_vertex(v, dim)
    voxels[ x, y, z ] = 1
"""

    
#  display
ax = plt.figure().add_subplot(projection='3d')
mi, ma, size = bounding_box(vs)
ax.set_box_aspect(size)

# render voxels
# x, z, y = voxels.nonzero()
# ax.scatter(x, y, z, c=y, s=10, alpha=.35, edgecolors='none')

# compute and render skeleton
skel = skeletonize(voxels)
x, z, y = np.where( skel, 1, 0 ).nonzero()
ax.scatter(x, y, z, c='orange', s=10, alpha=1, edgecolors='none')
plt.show()

# todo visualize the skeleton in GL

"""
function furthestPoint(p1, p2, points) {
  let dmax = 0;
  let maxI = -1;
  for (let i = 0; i < points.length; i++) {
    const dtemp = perpendicularDist(points[i], p1, p2);

    if (dtemp > dmax) {
      dmax = dtemp;
      maxI = i;
    }
  }

  return { index: maxI, dist: dmax };
}

function perpendicularDist(p, p1, p2) {
  if (p1 == p || p == p2) return 0;
  const a = p.copy().sub(p1);
  const b = p.copy().sub(p2);
  const c = a.cross(b).mag();
  const d = p2.copy().sub(p1).mag();
  return c / d;
}

"""

quit()