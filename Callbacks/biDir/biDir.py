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

def myCB(msg, plug, otherPlug, nodes):
    #print 'msg: {}'.format(msg)
    #print 'plug: {}'.format(plug)
    #print 'other plug: {}'.format(otherPlug)
    #print 'child node: {}'.format(nodes)
    
    #Get parent/child
    parent, child = nodes[0], nodes[1]
    parentPath = om2.MDagPath()
    childPath = om2.MDagPath()
    parentPath = om2.MDagPath.getAPathTo(parent)
    childPath = om2.MDagPath.getAPathTo(child)
    #print 'parent {}'.format(parentPath)
    #print 'child: {}'.format(childPath)
    
    #Matricies
    parentMtx = om2.MDagPath.inclusiveMatrix(parentPath)
    childMtx = om2.MDagPath.inclusiveMatrix(childPath)
    offset = childMtx * parentMtx.inverse()
    
    #PostTransform
    parentPostMtx = om2.MDagPath.inclusiveMatrix(parentPath)
    childPostMtx = offset * parentPostMtx

    transformMtx = om2.MTransformationMatrix(childPostMtx)
    om2.MFnTransform(child).setTransformation(transformMatrix)


if __name__ == '__main__':
    if 'firstCallbackID' in globals().keys():
        om2.MMessage.removeCallback(firstCallbackID)
    if 'secondCallbackID' in globals().keys():
        om2.MMessage.removeCallback(secondCallbackID)
    
    mFirstNode = getMObject('a')
    mSecondNode = getMObject('b')
    firstCallbackID = om2.MNodeMessage.addAttributeChangedCallback(mFirstNode, myCB, [mFirstNode ,mSecondNode])
    secondCallbackID = om2.MNodeMessage.addAttributeChangedCallback(mSecondNode, myCB, [mSecondNode ,mFirstNode])

