import pymel.core as pm
import os

MAYA_APP_DIR = mel.eval('getenv ("MAYA_APP_DIR")')
pluginName = "dsAttractDeformer"

pm.newFile(f=1)
try:
    pm.unloadPlugin(pluginName)
except:
    pass
pm.loadPlugin(os.path.join(MAYA_APP_DIR, "scripts\dsNodes\dsAttractDeformer\plugins\{0}.py".format(pluginName)))
pm.openFile(os.path.join(MAYA_APP_DIR, "scripts\dsNodes\dsAttractDeformer\\tests\\dsAttractDeformerTest.ma"), f=1)


#### TEST ####
dsAttractDeformer = pm.deformer("pTorus1", typ="dsAttractDeformer")[0]
for i in range(0,8):
    pm.connectAttr("sticky_CRV.cv[{0}]".format(i), dsAttractDeformer + ".ap[{0}]".format(i))