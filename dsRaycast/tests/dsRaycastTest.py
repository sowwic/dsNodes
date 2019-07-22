import maya.cmds as mc
from rigging.functions import *

mc.file(new=1,f=1)
mc.unloadPlugin("dsRaycast")

mc.loadPlugin('C:\Users\dmitris\Documents\maya\scripts\dsNodes\dsRaycast\plugins\dsRaycast.py')

###### Test #########
mesh = mc.polyPlane()[0]
mc.move(0, 4, 0, mesh)
mc.scale(50, 50, 50, mesh)
source = create.locator(name='sourse')
source.translate = [0, 10, 0]
aim = create.locator(name='aim')
aim.translate = [0, 1, 0]

dsRaycast = mc.createNode('dsRaycast')

mc.connectAttr(mesh + '.worldMesh', dsRaycast + '.tm')
source.translate > dsRaycast + '.srs'
aim.translate > dsRaycast + '.aim'

cube = mc.polyCube(n='testBoi00')

mc.connectAttr(dsRaycast + ".hitPoint", cube[0] + ".t")


