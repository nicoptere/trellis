# TRELLIS for blender

addon to bind [TRELLIS](https://github.com/Microsoft/TRELLIS) to blender, it allows to compute 3D models from an image and display the result in Blender.

this is an experimental **toy project**, mostly to learn how to create a Blender add-on, it will not be maintained or updated in a foreseable future.

#### writing some [dev notes](#notes) as I go (things I learnt the hard way)

## ⚠️ pre-requisite ⚠️

### You need to install and set up [TRELLIS](https://github.com/Microsoft/TRELLIS) on your computer.

this means you need a beefy GPU with a minimum of 16Go VRAM and CUDA installed.


### start the server to compute TRELLIS files
for many reasons, the TRELLIS computations are handled in a separate terminal.
the server is located in the add-ons foolder, you can find the server here:

```python
import os
import addon_utils
path = addon_utils.paths()
path = [str for str in path if not '_core' in str ][0]
server_file = path + "/trellis/server/server.py"
# this should be the server file location
print( server_file )
```

run the server in a separate terminal, for instance on Windows:
```shell
python 'C:\Users\_USER_\AppData\Roaming\Blender Foundation\Blender\4.3\scripts\addons/trellis/server/server.py'
```



## install

download or clone this repo "somewhere".

open Blender and install the add-on from the **edit > preferences > addons menu**, choose install from disk and select the **trellis.zip** file from "somewhere". 

![install](doc/install.png)

then activate it if it doesn't start automatically. the panel should be available under the **'item', 'tool' 'view'** tools.

![panel](doc/panel.png)

## usage

first, select an image from the image browser or drag drop an image file from your desktop or select an drag-dropped image. 

then you can change the SLAT generation settings. they correspond to [these TRELLIS settings](https://github.com/microsoft/TRELLIS/blob/main/example.py#L23-L31). in doubt, leave them "as is".

hitting **compute** will call the SLAT generation, this step is fast and will produce a Gaussian Splatting model that gives a good idea of the final result.

![gaussian](doc/gaussian.png)

the second step is to discretize the Gaussian Splatting model, you can tweak the mesh **simplification ratio** and the model's **texture size**. higher simplification ratios compute much faster but produce 'blobby' results.

hitting **discretize** will ... well ... discretize the Gaussian Splatting model and turn it into a triangular mesh. this step is slow, especially with low simplification ratios. it should produces something like this:
![discreet](doc/discreet.png)

hitting discretize directly will run both the SLAT and the discretization steps.

post process step:
not sure if useful but the scripting layout of the blender file contains a decimate/triangulate modifier that can be ran to collapse coplanar faces.
![robot](doc/robot.png)



# <a name="notes">#</a> dev notes, caveats etc.

* Blender runs its own Python version. a script / add-on is executed in the context of this Python environment. we can't install dependecies (pip) at runtime, anything else must run in separate Python installs/terminals on the system. an add-on can't run python script in separate terminals and comunication with servers is slow.

* it's impossible to set the properties of an object directly from a Panel ; any change must be performed by an operator. variables and references must be stored so that Operators can perform the changes. 

* storing is tedious (need a wrapper) but makes everything very responsive 
```python
from bpy.types import WindowManager, Image, Object
from bpy.props import FloatProperty, IntProperty, PointerProperty
# storing an int
WindowManager.sparse_steps = IntProperty(name="steps", default=12, min=1, max=100)
# storing a float
WindowManager.slat_strength = FloatProperty(name="strength", default=3, min=0, max=50, step=0.1)
# storing an object
WindowManager.gizmo = PointerProperty(name="gizmo", type=Object)
# storing an image object
WindowManager.image = PointerProperty(name="image", type=Image)
```

* accessing the `context` is still a mystery, need to dig further. an unavailable context blocks most operations.

* remote servedr calls block the execution, even when using async calls.
the workaround looks convoluted (modal & timers)
