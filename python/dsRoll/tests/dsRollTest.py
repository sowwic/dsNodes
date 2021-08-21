import pymel.core as pm
import os

MAYA_APP_DIR = mel.eval('getenv ("MAYA_APP_DIR")')
pluginName = "dsRoll"

pm.newFile(f=1)
pm.unloadPlugin(pluginName)
pm.loadPlugin(os.path.join(MAYA_APP_DIR, "scripts\dsNodes\dsRoll\plugins\{0}.py".format(pluginName)))
pm.openFile(os.path.join(MAYA_APP_DIR, "scripts\dsNodes\dsRoll\\tests\\testScene.ma"), f=1)


#### TEST ####
dsRollNode = pm.createNode("dsRoll")
pm.connectAttr(dsRollNode + ".rotation", "wheel_PLY.ry")
pm.connectAttr( "wheel_PLY.ty", dsRollNode + ".radius")
pm.connectAttr( "wheel_PLY.tz", dsRollNode + ".distance")
