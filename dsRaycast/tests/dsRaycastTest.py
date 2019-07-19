import maya.cmds as mc

mc.file(new=1, f=1)
mc.unloadPlugin('dsRaycast')

mc.loadPlugin('/Users/dima/Library/Preferences/Autodesk/maya/scripts/dsNodes/dsRaycast/plugins/dsRaycast.py')