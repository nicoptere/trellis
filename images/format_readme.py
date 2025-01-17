import os

references = {
"castle" : "???",
"fox" : "https://civitai.com/images/2024422",
"mech" : "https://civitai.com/images/37815",
"bob" : "https://lexica.art/prompt/7e45b698-2a6d-4e18-a8b8-1fe997e18794",
"moto" : "https://lexica.art/prompt/ca1014d6-9ada-4034-aaf0-cdf164b31903",
"diorama" : "https://lexica.art/prompt/da05c0a4-9283-47eb-89cc-9b7b5f7b723e",
"hamster" : "https://civitai.com/images/50845478)",
"scifi" : "https://lexica.art/prompt/c48df098-ce5d-4198-98e0-2e0f2385d6f8",
"boy" : "https://lexica.art/prompt/ca4fa23b-a69f-41c5-809f-619bd684c6cb",
"watercolour" : "castle https://lexica.art/prompt/9196aa95-71e0-44a0-9656-51b868f795f7",
"girl" : "https://civitai.com/images/50855669",
"robot1" : "https://civitai.com/images/49923041",
"marine" : "https://civitai.com/images/1585134",
"building" : "https://civitai.com/images/8557405",
"camera" : "https://civitai.com/images/20597973",
"pony" : "https://civitai.com/images/13556724",
"room" : "https://civitai.com/images/1096324",
"bug-mesh" : "https://civitai.com/images/13556695",
"old-man" : "https://civitai.com/images/19605420",
"isometric-interior" : "https://civitai.com/images/476272",
"spider-mech" : "https://civitai.com/images/694508",
# "3d ring https://unsplash.com/photos/a-red-and-orange-object-floating-in-the-air-5O7e8A4I8u0",
# "kiki https://unsplash.com/photos/a-small-black-and-brown-dog-sitting-on-its-hind-legs-hz_BchTSLX8",
}

# get images in the 'images' folder
images = [ f for f in os.listdir('./') if '.' in f and not ".py" in f and not '.md' in f ]
links = [references[f.split( '.')[0]] for f in images]

# header text
text = """
# sources
the images are collected from internet, often generated from T2I models.
I'll try to keep track of the exact references here, as of now, they mostly come from [civit.ai](https://civit.ai/) and [lexica](https://lexica.art/)
<div style="padding:5vw;">
"""
# create image table
text += """
|images|||
|-|:-:|-:|"""

for i, (image, link) in enumerate( zip( images, links )  ):

  # start new line
  if i % 3 == 0:
    text += '\n|'
  name, ext = os.path.splitext(image)
  text += "[![%s](./%s)](%s) |" % (name, image, link) 

# finish the line
while ( i % 3 != 0):
  i += 1
  text += "|"
text += "</div>"
# save
open('README.md', 'w+').write(text)