import maya.cmds as mc

mc.file(new=1,f=1)
mc.unloadPlugin('drawVector')
mc.loadPlugin('C:\Users\dmitris\Documents\maya\scripts\dsNodes\dsDrawVector\plugins\drawVector.py')

###### Test #########
#Basic test