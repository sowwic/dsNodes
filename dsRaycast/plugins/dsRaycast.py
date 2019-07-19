from maya import cmds as mc, OpenMaya as om, OpenMayaMPx as ompx, mel
import getpass, os, sys

NAME = "dsRaycast"
VERSION = "1.0"
MAYAVERSION = "2019"
NODENAME = "dsRaycast"
NODEID = om.MTypeId(0x09933)

class MyNode(ompx.MPxNode):
   
    inAttr = om.MObject()
    outAttr = om.MObject()
   
    def __init__(self):
        ompx.MPxNode.__init__(self)
       
    def compute(self, pPlug, pDataBlock):
       
        if pPlug == MyNode.outAttr:
                   
           inHandle = pDataBlock.inputValue(MyNode.inAttr)
           outHandle = pDataBlock.outputValue(MyNode.outAttr)
           
           inValue = inHandle.asLong()
           
           outValue = inValue * 1.0
           
           outHandle.setFloat(outValue)
           
           outHandle.setClean()
           
        else:
           
            return om.kUnknownParameter
       
def nodeCreator():
   return ompx.asMPxPtr(MyNode())

def nodeInitializer():
   
    numericAttributeFn = om.MFnNumericAttribute()
   
    MyNode.inAttr = numericAttributeFn.create("input", 
                                             "input",
                                             om.MFnNumericData.kLong,
                                             0
                                             )
    MyNode.addAttribute(MyNode.inAttr)
   
    MyNode.outAttr = numericAttributeFn.create("output", 
                                              "output",
                                              om.MFnNumericData.kFloat
                                              )
    MyNode.addAttribute( MyNode.outAttr )
   
    MyNode.attributeAffects(MyNode.inAttr, MyNode.outAttr)

def initializePlugin(obj):
   plugin = ompx.MFnPlugin(obj, NAME, VERSION, MAYAVERSION)
   try:
       plugin.registerNode(NODENAME, NODEID, nodeCreator, nodeInitializer)
   except RuntimeError:
       sys.stderr.write("Failed to register node: %s" % NODENAME)


def uninitializePlugin(obj):
   plugin = ompx.MFnPlugin(obj)
   try:
       plugin.deregisterNode(NODEID)
   except Exception as err:
       sys.stderr.write("Failed to deregister node: %s\n%s" % (NODENAME, err))