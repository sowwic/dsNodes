from maya import cmds as mc, mel
import os

MAYA_APP_DIR = mel.eval('getenv ("MAYA_APP_DIR")')


mc.file(new=1,f=1)
mc.unloadPlugin('dsDrawVector')
mc.loadPlugin(os.path.join(MAYA_APP_DIR, 'scripts\dsNodes\dsDrawVector\plugins\dsDrawVector.py'))

###### Test #########
#Basic test
sourceObj = mc.polyCube()[0]
aimObj = mc.polyCube()[0]

vectorNode = mc.createNode('drawVector')
mc.connectAttr(sourceObj + '.t', vectorNode + '.sp')
mc.connectAttr(aimObj + '.t', vectorNode + '.ap')

mc.move( 2, 5, 10, aimObj)
