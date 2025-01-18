
import trimesh as tm
import numpy as np
import matplotlib.pyplot as plt
from math import floor
from skimage.morphology import medial_axis, skeletonize


def get_bounding_box(vertices):
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

    return mins, maxs

    mins = np.full(3, 10) #np.array(volume.shape)
    maxs = np.zeros(3, -10)
    for z in range(volume.shape[0]):
        for y in range(volume.shape[1]):
            for x in range(volume.shape[2]):
                if volume[z, y, x]:
                    if z < mins[0]:
                        mins[0] = z
                    elif z > maxes[0]:
                        maxes[0] = z
                    if y < mins[1]:
                        mins[1] = y
                    elif y > maxes[1]:
                        maxes[1] = y
                    if x < mins[2]:
                        mins[2] = x
                    elif x > maxes[2]:
                        maxes[2] = x
    return mins, maxes

name = "boy"
mesh = tm.load_mesh('C:/Users/barra/Documents/blender/models/%s/%s.glb' % (name, name) )
print( mesh.geometry )
mesh = mesh.geometry['geometry_0']


vs = mesh.vertices
# print( get_bounding_box(vs) )
dim = 32
voxels = np.zeros( (dim, dim, dim), dtype=np.int8)

def getIndex( v ):

    x = ( floor( ( .5 + v[0] ) * dim ) / dim ) * dim
    y = ( floor( ( .5 + v[1] ) * dim ) / dim ) * dim
    z = ( floor( ( .5 + v[2] ) * dim ) / dim ) * dim
    
    x = int( max( 0, min( x, dim - 1 )) )
    y = int( max( 0, min( y, dim - 1 )) )
    z = dim - 1 - int( max( 0, min( z, dim - 1 )) )

    return x,y,z

for v in vs:
    x, y, z = getIndex(v)
    voxels[ x, y, z ] = 1
    

# print( voxels.shape )
# print( voxels )

ax = plt.figure().add_subplot(projection='3d')
mi, ma = get_bounding_box(vs)
size = (
    ma[0] - mi[0],
    ma[2] - mi[2],
    ma[1] - mi[1],
)
ax.set_box_aspect(size)

# render voxels
x, z, y = voxels.nonzero()
ax.scatter(x, y, z, c=y, s=10, alpha=.35, edgecolors='none')
# ax.voxels(voxels, color="orange", alpha=0.2, linestyle='', edgecolor='None')

skel = skeletonize(voxels)
x, z, y = np.where( skel, 1, 0 ).nonzero()
# todo find lines 
ax.scatter(x, y, z, c='orange', s=10, alpha=1, edgecolors='none')
plt.show()

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