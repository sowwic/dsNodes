import maya.cmds as mc
from maya.api import OpenMaya as om2


def getMObject(node):
    node = str(node)
    mSelectionList = om2.MSelectionList()
    try:
        mSelectionList.add(node)
    except:
        raise ValueError("No object matches name: " + node)
    return mSelectionList.getDependNode(0)

class BiDirectionalConstr:

    def __init__(self):
        self.driver = None
        self.offset = None
        self.mFirstNode = getMObject('pCone1')
        self.mSecondNode = getMObject('pCube1')
        
        #callbacksDict = {'firstDirtyplugCBID'   : None,
        #                 'secondDirtyplugCBID'  : None, 
        #                 'firstAttrChangeCBID'  : None,
        #                 'secondAttrChangeCBID' : None 
        #                }

        #for callbackName in callbacksDict.keys():
        #    if callbackName in globals().keys():
        #        om2.MMessage.removeCallback(callbacksDict[callbackName])

        firstDirtyplugCBID = om2.MNodeMessage.addNodeDirtyPlugCallback(self.mFirstNode, self.dirtyPlugCBfunc, [self.mFirstNode ,self.mSecondNode])
        #callbacksDict['firstDirtyplugCBID'] = firstDirtyplugCBID
        secondDirtyplugCBID = om2.MNodeMessage.addNodeDirtyPlugCallback(self.mSecondNode, self.dirtyPlugCBfunc, [self.mSecondNode ,self.mFirstNode])
        #callbacksDict['secondDirtyplugCBID'] = secondDirtyplugCBID

        firstAttrChangeCBID = om2.MNodeMessage.addAttributeChangedCallback(self.mFirstNode, self.attrChangedCBfunc, [self.mFirstNode ,self.mSecondNode])
        #callbacksDict['firstAttrChangeCBID'] = firstAttrChangeCBID
        secondAttrChangeCBID = om2.MNodeMessage.addAttributeChangedCallback(self.mSecondNode, self.attrChangedCBfunc, [self.mSecondNode ,self.mFirstNode])
        #callbacksDict['secondAttrChangeCBID'] = secondAttrChangeCBID

    def dirtyPlugCBfunc(self, node, plug, nodes):  
        #print "dirt", self.driver if self.driver is None else om2.MDagPath.getAPathTo(self.driver).partialPathName(), plug.name()
        #Get parent/child
        parent, child = nodes[0], nodes[1]

        if self.driver:
            #print "exiting early from dirty callback"
            return
        else:
            #print "dirtyPlug", plug.name(), om2.MDagPath.getAPathTo(nodes[0]).partialPathName()
            self.driver = parent

            parentPath = om2.MDagPath.getAPathTo(parent)
            childPath = om2.MDagPath.getAPathTo(child)
            
            #Matricies
            parentMtx = om2.MDagPath.inclusiveMatrix(parentPath)
            childMtx = om2.MDagPath.inclusiveMatrix(childPath)
            self.offset = childMtx * parentMtx.inverse()


    def attrChangedCBfunc(self, msg, plug, otherPlug, nodes):
        if self.driver and self.driver == nodes[1]:
            #print "exiting early from attr change callback"
            return

        if not (msg & om2.MNodeMessage.kAttributeSet):
            return

        if not self.offset:
            mc.warning("No offset")
            return

        #print "attrChanged", plug.name()

        parent, child = nodes[0], nodes[1]
        parentPath = om2.MDagPath.getAPathTo(parent)

        #PostTransform
        parentPostMtx = om2.MDagPath.inclusiveMatrix(parentPath)
        childPostMtx = self.offset * parentPostMtx

        transformMtx = om2.MTransformationMatrix(childPostMtx)
        om2.MFnTransform(child).setTransformation(transformMtx)

        def a():
            #print "stop driving"
            self.driver = None
        mc.evalDeferred(a)
        #self.driver = None
        
        

if __name__ == '__main__':
    mc.file(new=1, f=1)
    mc.polyCube()
    mc.setAttr(mc.polyCone()[0] + ".t", 5, 5, 5)
    biConstr = BiDirectionalConstr()
    
    