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
dsAttractDeformer = pm.deformer("pTorus1", typ="dsAttract")[0]
pm.connectAttr("sticky_CRVShape.local", dsAttractDeformer+".inputShape")
pm.connectAttr("sticky_CRV.worldMatrix[0]", dsAttractDeformer+".inputMatrix")