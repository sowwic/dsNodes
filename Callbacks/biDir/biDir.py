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
        self.updateOffset()
        
        callbacksDict = {
                         'firstAttrChangeCBID'  : None,
                         'secondAttrChangeCBID' : None 
                        }

        for callbackName in callbacksDict.keys():
            if callbackName in globals().keys():
                print ' removing existing callback {}'.format(callbacksDict[callbackName])
                om2.MMessage.removeCallback(callbacksDict[callbackName])


        firstAttrChangeCBID = om2.MNodeMessage.addAttributeChangedCallback(self.mFirstNode, self.attrChangedCBfunc, [self.mFirstNode ,self.mSecondNode])
        callbacksDict['firstAttrChangeCBID'] = firstAttrChangeCBID
        secondAttrChangeCBID = om2.MNodeMessage.addAttributeChangedCallback(self.mSecondNode, self.attrChangedCBfunc, [self.mSecondNode ,self.mFirstNode])
        callbacksDict['secondAttrChangeCBID'] = secondAttrChangeCBID

    def updateOffset(self):
        parentPath = om2.MDagPath.getAPathTo(self.mFirstNode)
        childPath = om2.MDagPath.getAPathTo(self.mSecondNode)
        
        #Matricies
        parentMtx = om2.MDagPath.inclusiveMatrix(parentPath)
        childMtx = om2.MDagPath.inclusiveMatrix(childPath)
        self.offset = childMtx * parentMtx.inverse()


    def attrChangedCBfunc(self, msg, plug, otherPlug, nodes):
        evalAttr = om2.MDagPath.getAPathTo(self.mFirstNode).partialPathName() + ".eval"

        if plug.name() == evalAttr:
            if evalAttr:
                self.updateOffset()

        if not mc.getAttr(om2.MDagPath.getAPathTo(self.mFirstNode).partialPathName() + ".eval"):
            return

        if not self.driver:
            self.driver = nodes[0]

        if self.driver == nodes[1]:
            def a():
                self.driver = None
            mc.evalDeferred(a)
            return

        if not (msg & om2.MNodeMessage.kAttributeSet):
            return

        if not self.offset:
            mc.warning("No offset")
            return


        parent, child = nodes[0], nodes[1]
        parentPath = om2.MDagPath.getAPathTo(parent)

        #PostTransform
        parentPostMtx = om2.MDagPath.inclusiveMatrix(parentPath)

        if self.driver == self.mFirstNode:
            childPostMtx = self.offset * parentPostMtx
        else:
            childPostMtx = self.offset.inverse() * parentPostMtx

        transformMtx = om2.MTransformationMatrix(childPostMtx)
        om2.MFnTransform(child).setTransformation(transformMtx)       
        

if __name__ == '__main__':
    mc.file(new=1, f=1)
    mc.polyCube()
    mc.polyCone()
    mc.addAttr('pCone1', ln='eval', at='long', dv=1, min=0, max=1, k=1)
    biConstr = BiDirectionalConstr()
    
    