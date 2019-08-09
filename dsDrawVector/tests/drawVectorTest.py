import maya.cmds as mc

mc.file(new=1,f=1)
mc.unloadPlugin('drawVector')
mc.loadPlugin('C:\Users\dmitris\Documents\maya\scripts\dsNodes\dsDrawVector\plugins\drawVector.py')

###### Test #########
#Basic test
sourceObj = mc.polyCube()[0]
aimObj = mc.polyCube()[0]

vectorNode = mc.createNode('footPrint')
mc.connectAttr(sourceObj + '.t', vectorNode + '.sp')
mc.connectAttr(aimObj + '.t', vectorNode + '.ap')

mc.move( 2, 5, 10, aimObj)
