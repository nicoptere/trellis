


import addon_utils
import os



path = addon_utils.paths()
path = [str for str in path if not '_core' in str ][0]
print( path )

filename = path + "/trellis/server/server.py"
print( filename, os.path.exists( filename  ) )

exec(compile(open(filename).read(), filename, 'exec'))