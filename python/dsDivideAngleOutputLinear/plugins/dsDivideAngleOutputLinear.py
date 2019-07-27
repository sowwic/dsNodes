from maya import cmds as mc, OpenMaya as om, OpenMayaMPx as ompx, mel
import getpass, os, sys

NAME = "Dmitrii Shevchenko"
VERSION = "1.0"
MAYAVERSION = "2018"
NODENAME = "dsDivideAngleOutputLinear"
NODEID = om.MTypeId(0x09993)

class MyNode(ompx.MPxNode):

    inAAttr = om.MObject()
    inBAttr = om.MObject()

    outAttr = om.MObject()

    def __init__(self):
        ompx.MPxNode.__init__(self)

    def compute(self, pPlug, pDataBlock):

        if pPlug == MyNode.outAttr:

            inAHandle = pDataBlock.inputValue(MyNode.inAAttr)
            inBHandle = pDataBlock.inputValue(MyNode.inBAttr)
            outHandle = pDataBlock.outputValue(MyNode.outAttr)

            inAValue = inAHandle.asAngle()
            inBValue = inBHandle.asAngle()
            inAAngle = inAValue.asRadians()
            inBAngle = inBValue.asRadians()

            if inBAngle!=0:
                outValue = inAAngle / inBAngle
            else:
                outValue = 0

            outHandle.setDouble(outValue)

            outHandle.setClean()

        else:

            return om.kUnknownParameter

def nodeCreator():
    return ompx.asMPxPtr(MyNode())

def nodeInitializer():

    numericAttributeFn = om.MFnNumericAttribute()
    unitAttribute = om.MFnUnitAttribute()

    MyNode.inAAttr = unitAttribute.create("angleA", 
            "aa",
            om.MFnUnitAttribute.kAngle,
            )
    MyNode.addAttribute(MyNode.inAAttr)

    MyNode.inBAttr = unitAttribute.create("angleB", 
            "ab",
            om.MFnUnitAttribute.kAngle,
            )
    MyNode.addAttribute(MyNode.inBAttr)

    MyNode.outAttr = numericAttributeFn.create("output", 
            "output",
            om.MFnNumericData.kDouble
            )
    MyNode.addAttribute( MyNode.outAttr )

    MyNode.attributeAffects(MyNode.inAAttr, MyNode.outAttr)
    MyNode.attributeAffects(MyNode.inBAttr, MyNode.outAttr)

def initializePlugin(obj):
    plugin = ompx.MFnPlugin(obj, NAME, VERSION, MAYAVERSION)
    try:
        plugin.registerNode(NODENAME, NODEID, nodeCreator, nodeInitializer)
    except RuntimeError:
        sys.stderr.write("Failed to register node: %s" % NODENAME)

    #     aeTemplate = open(r'C:/Users/'+getpass.getuser()+'/Documents/maya/scripts/rigging/nodes/AETemplates/AElbIconTemplate.mel', "r").read()
    #     mel.eval(aeTemplate)

def uninitializePlugin(obj):
    plugin = ompx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(NODEID)
    except Exception as err:
        sys.stderr.write("Failed to deregister node: %s\n%s" % (NODENAME, err))