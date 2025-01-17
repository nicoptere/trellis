import os
os.environ['ATTN_BACKEND'] = 'xformers'   # Can be 'flash-attn' or 'xformers', default is 'flash-attn'
os.environ['SPCONV_ALGO'] = 'native'        # Can be 'native' or 'auto', default is 'auto'.
                                            # 'auto' is faster but will do benchmarking at the beginning.
                                            # Recommended to set to 'native' if run only once.
import pickle
import torch
import sys
from PIL import Image
from easydict import EasyDict as edict
from typing import Tuple

from trellis.representations import Gaussian, MeshExtractResult
from trellis.utils import postprocessing_utils

# pipeline instance
pipeline = None
overwrite = True
def pack_state(gs: Gaussian, mesh: MeshExtractResult, trial_id: str) -> dict:
    return {
        'gaussian': {
            **gs.init_params,
            '_xyz': gs._xyz.cpu().numpy(),
            '_features_dc': gs._features_dc.cpu().numpy(),
            '_scaling': gs._scaling.cpu().numpy(),
            '_rotation': gs._rotation.cpu().numpy(),
            '_opacity': gs._opacity.cpu().numpy(),
        },
        'mesh': {
            'vertices': mesh.vertices.cpu().numpy(),
            'faces': mesh.faces.cpu().numpy(),
        },
        'trial_id': trial_id,
    }
    
    
def unpack_state(state: dict) -> Tuple[Gaussian, edict, str]:
    gs = Gaussian(
        aabb=state['gaussian']['aabb'],
        sh_degree=state['gaussian']['sh_degree'],
        mininum_kernel_size=state['gaussian']['mininum_kernel_size'],
        scaling_bias=state['gaussian']['scaling_bias'],
        opacity_bias=state['gaussian']['opacity_bias'],
        scaling_activation=state['gaussian']['scaling_activation'],
    )
    gs._xyz = torch.tensor(state['gaussian']['_xyz'], device='cuda')
    gs._features_dc = torch.tensor(state['gaussian']['_features_dc'], device='cuda')
    gs._scaling = torch.tensor(state['gaussian']['_scaling'], device='cuda')
    gs._rotation = torch.tensor(state['gaussian']['_rotation'], device='cuda')
    gs._opacity = torch.tensor(state['gaussian']['_opacity'], device='cuda')
    
    mesh = edict(
        vertices=torch.tensor(state['mesh']['vertices'], device='cuda'),
        faces=torch.tensor(state['mesh']['faces'], device='cuda'),
    )
    
    return gs, mesh, state['trial_id']


# todo pass params
def process( img, params = None ):

    # file names
    
    path = os.path.splitext(img)[0]
    name, ext  = os.path.splitext( os.path.basename(img) )
    os.makedirs(path, exist_ok=True)

    ply_file = '%s/%s-gaussian.ply' %  (path, name)
    pickle_file = '%s/%s.pickle' %  (path, name)
    if os.path.exists( ply_file ) == True :
        if overwrite == False:
            return ply_file
    
    gaussian = None
    mesh = None

    print( 'computing SLAT' )
    print( 'processing path:', path )
    print( 'processing params:', params )
    # Load an image
    image = Image.open(img)

    # Run the pipeline
    global pipeline
    outputs = pipeline.run(
        image,
        # Optional parameters
        seed=-1,
        sparse_structure_sampler_params={
            "steps": params.slat.sparse.steps,
            "cfg_strength": params.slat.sparse.cfg_strength,
        },
        slat_sampler_params={
            "steps": params.slat.slat.steps,
            "cfg_strength": params.slat.slat.cfg_strength,
        },
        

    )
    # save Gaussian Splat model
    print( '\t SLAT computed, saving GAUSSIAN SPLAT model under:', ply_file)
    gaussian = outputs['gaussian'][0]
    mesh = outputs['mesh'][0]
    gaussian.save_ply(ply_file) 
    
    # save intermediate state
    print( '\t SLAT computed, saving pickled model under:', pickle_file )
    content = pack_state( gaussian, mesh, "1" )
    pickle.dump(content, open( pickle_file, "wb" ) )
    del mesh
    del content
    del gaussian
    return ply_file


def optimize( img, params = None ):
    
    # file names
    path = os.path.splitext(img)[0]
    name, ext  = os.path.splitext( os.path.basename(img) )
    os.makedirs(path, exist_ok=True)

    glb_file = '%s/%s.glb' % (path, name)
    pickle_file = '%s/%s.pickle' %  (path, name)
    if os.path.exists( glb_file ) == True:
        if overwrite == False:
            return glb_file

    print( 'processing name:', path )
    print( 'processing params:', params )

    # (debug) bail out if model not initialized 
    global pipeline
    if pipeline is None:
        return glb_file

    gaussian = None
    mesh = None

    # check if the pickle file exists
    if os.path.exists( pickle_file ) == False:

        # if not create it
        print( 'need to compute the SLAT first' )
        process(img, params)
    
    raw = pickle.load( open( pickle_file, "rb" ) )
    outputs = unpack_state( raw )
    gaussian = outputs[0]
    mesh = outputs[1]

    # GLB files can be extracted from the outputs
    if os.path.exists( glb_file ) == False:
        glb = postprocessing_utils.to_glb(
            gaussian,
            mesh,
            simplify=params.glb.simplify,          # Ratio of triangles to remove in the simplification process
            texture_size=params.glb.texture_size,      # Size of the texture used for the GLB
        )
        glb.export(glb_file)

    del mesh
    del gaussian
    return glb_file



def checkInitialization():
    global pipeline
    if pipeline == None:    
        from trellis.pipelines import TrellisImageTo3DPipeline
        pipeline = TrellisImageTo3DPipeline.from_pretrained("JeffreyXiang/TRELLIS-image-large")
        pipeline.cuda()


if __name__ == "__main__":

    
    checkInitialization()
    path = sys.argv[1]
    
    params = edict({
        "slat" : {
            "sparse" : {
                "steps": 12,
                "cfg_strength": 7.5,
            },
            "slat" : {
                "steps": 12,
                "cfg_strength": 3,
            },
        },
        "glb":{
            "simplify" : 0.95,
            "texture_size" : 2048
        }
    })

    exclude = [".ply", '.pickle', '.md', '.glb' '.obj', '.avif']
    for r, s, fs in os.walk(path):
        fs.sort()
        for f in fs:
            _, ext = os.path.splitext(f)
            if ext in exclude:
                continue
            # compute
            image = os.path.abspath( path + f )
            model = optimize( image, params )


