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

def myCB(msg, plug, otherPlug, clientData):
    print 'msg: {}'.format(msg)
    print 'plug: {}'.format(plug)
    print 'other plug:'.format(otherPlug)
    print 'client data:'.format(clientData)


if __name__ == '__main__':
    if 'callbackID' in globals().keys():
        om2.MMessage.removeCallback(callbackID)
    mRaycastNode = getMObject('dsRaycast2')
    callbackID = om2.MNodeMessage.addAttributeChangedCallback(mRaycastNode, myCB)

